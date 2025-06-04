from flask import Flask, render_template_string, request, redirect, url_for, session, flash
from dotenv import load_dotenv
import os
import requests
from components.resource_summary import ResourceSummary

app = Flask(__name__)
load_dotenv()
app.secret_key = os.getenv("SECRET_KEY", "dev-secret")

ADMIN_USERNAME = os.getenv("ADMIN_USERNAME")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")
READER_USERNAME = os.getenv("READER_USERNAME")
READER_PASSWORD = os.getenv("READER_PASSWORD")
BACKEND_API_URL = os.getenv("BACKEND_API_URL", "http://localhost:8000")
VM_FETCH_TIMEOUT = int(os.getenv("FRONTEND_VM_FETCH_TIMEOUT", 60))

LOGIN_PAGE_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Login - GCP AI Cost Optimizer</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 2rem; }
        .login-box { max-width: 350px; margin: 4rem auto; padding: 2rem; border: 1px solid #ddd; border-radius: 8px; background: #fafbfc; }
        h2 { text-align: center; color: #2c3e50; }
        label { display: block; margin-top: 1rem; }
        input[type=text], input[type=password] { width: 100%; padding: 0.5rem; margin-top: 0.5rem; border-radius: 4px; border: 1px solid #ccc; }
        button { margin-top: 1.5rem; width: 100%; padding: 0.7rem; background: #2980b9; color: #fff; border: none; border-radius: 4px; font-size: 1rem; }
        .error { color: #c0392b; text-align: center; margin-top: 1rem; }
    </style>
</head>
<body>
    <div class="login-box">
        <h2>Login</h2>
        {% with messages = get_flashed_messages() %}
          {% if messages %}
            <div class="error">{{ messages[0] }}</div>
          {% endif %}
        {% endwith %}
        <form method="post" action="{{ url_for('login') }}">
            <label for="username">Username:</label>
            <input type="text" name="username" id="username" required autofocus>
            <label for="password">Password:</label>
            <input type="password" name="password" id="password" required>
            <button type="submit">Login</button>
        </form>
    </div>
</body>
</html>
"""

HOME_PAGE_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>GCP AI Cost Optimizer - Home</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 2rem; }
        h1 { color: #2c3e50; }
        .resources { display: flex; flex-wrap: wrap; gap: 1.5rem; margin-top: 2rem; }
        .card {
            border: 1px solid #ddd;
            border-radius: 8px;
            padding: 1.5rem;
            min-width: 180px;
            text-align: center;
            box-shadow: 0 2px 6px #eee;
            background: #fafbfc;
            transition: box-shadow 0.2s;
        }
        .card:hover { box-shadow: 0 4px 12px #ccc; }
        .card a { text-decoration: none; color: #2980b9; font-weight: bold; }
        .logout { float: right; }
        .role { font-size: 1rem; color: #888; margin-top: 0.5rem; }
    </style>
</head>
<body>
    <a href="{{ url_for('logout') }}" class="logout">Logout</a>
    <h1>GCP AI Cost Optimizer</h1>
    <div class="role">Logged in as: <b>{{ role }}</b></div>
    <p>Welcome! Select a resource to view cost and optimization insights:</p>
    <div class="resources">
        <div class="card"><a href="{{ url_for('vms') }}">VMs (Compute Engine)</a></div>
        <div class="card"><a href="#">Cloud SQL</a></div>
        <div class="card"><a href="#">GKE (Kubernetes)</a></div>
        <div class="card"><a href="#">Filestore</a></div>
        <div class="card"><a href="#">Cloud Storage</a></div>
    </div>
</body>
</html>
"""

VM_FORM_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>VMs - GCP AI Cost Optimizer</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 2rem; }
        h2 { color: #2c3e50; }
        form { margin-bottom: 2rem; }
        label { display: block; margin-top: 1rem; }
        select, input[type=text] { width: 100%; padding: 0.5rem; border-radius: 4px; border: 1px solid #ccc; }
        button { margin-top: 1.5rem; width: 100%; padding: 0.7rem; background: #2980b9; color: #fff; border: none; border-radius: 4px; font-size: 1rem; }
        .error { color: #c0392b; margin-top: 1rem; }
        .result { margin-top: 2rem; }
        .loading { color: #2980b9; font-weight: bold; margin-top: 1rem; }
        th.sortable { cursor: pointer; text-decoration: underline; }
    </style>
    <script>
        function showLoading() {
            document.getElementById('loading-msg').style.display = 'block';
        }
        function setSort(field, currentSortBy, currentSortDir) {
            var form = document.getElementById('vm-form');
            var sortByInput = document.getElementById('sort_by');
            var sortDirInput = document.getElementById('sort_dir');
            if (sortByInput && sortDirInput) {
                if (currentSortBy === field) {
                    sortDirInput.value = currentSortDir === "asc" ? "desc" : "asc";
                } else {
                    sortByInput.value = field;
                    sortDirInput.value = "asc";
                }
                form.submit();
            }
        }
    </script>
</head>
<body>
    <a href="{{ url_for('index') }}">&#8592; Back to Home</a>
    <h2>VMs (Compute Engine)</h2>
    <form method="post" action="{{ url_for('vms') }}" onsubmit="showLoading()" id="vm-form">
        <label for="project_id">Project ID:</label>
        <select name="project_id" id="project_id" required>
            {% for pid in project_ids %}
                <option value="{{ pid }}" {% if pid == selected_project_id %}selected{% endif %}>{{ pid }}</option>
            {% endfor %}
        </select>
        <label for="geo">Location:</label>
        <select name="geo" id="geo" required>
            {% for geo in geo_map.keys() %}
                <option value="{{ geo }}" {% if geo == selected_geo %}selected{% endif %}>{{ geo }}</option>
            {% endfor %}
        </select>
        <input type="hidden" name="sort_by" id="sort_by" value="{{ sort_by }}">
        <input type="hidden" name="sort_dir" id="sort_dir" value="{{ sort_dir }}">
        <button type="submit">Fetch VMs</button>
    </form>
    <div id="loading-msg" class="loading" style="display:none;">Loading VMs, please wait...</div>
    {% if loading %}
        <div class="loading">Loading VMs, please wait...</div>
    {% endif %}
    {% if error %}
        <div class="error">{{ error }}</div>
    {% endif %}
    {% if vms is not none %}
        <div class="result">
            <table border="1" cellpadding="5">
                <tr>
                    <th class="sortable" onclick="setSort('name', '{{ sort_by }}', '{{ sort_dir }}')">Name</th>
                    <th class="sortable" onclick="setSort('status', '{{ sort_by }}', '{{ sort_dir }}')">Status</th>
                    <th class="sortable" onclick="setSort('zone', '{{ sort_by }}', '{{ sort_dir }}')">Zone</th>
                    <th class="sortable" onclick="setSort('machineType', '{{ sort_by }}', '{{ sort_dir }}')">Machine Type</th>
                    <th class="sortable" onclick="setSort('creationTime', '{{ sort_by }}', '{{ sort_dir }}')">Creation Time</th>
                    <th class="sortable" onclick="setSort('lastStartedTime', '{{ sort_by }}', '{{ sort_dir }}')">Start Time</th>
                    <th class="sortable" onclick="setSort('lastStoppedTime', '{{ sort_by }}', '{{ sort_dir }}')">Stop Time</th>
                    <th class="sortable" onclick="setSort('daysStarted', '{{ sort_by }}', '{{ sort_dir }}')">Days Started</th>
                    <th class="sortable" onclick="setSort('daysStopped', '{{ sort_by }}', '{{ sort_dir }}')">Days Stopped</th>
                </tr>
                {% if vms|length == 0 %}
                    <tr>
                        <td colspan="9" style="text-align:center; color:#888;">No VMs found for the selected location.</td>
                    </tr>
                {% else %}
                    {% for vm in vms %}
                        <tr>
                            <td>{{ vm.name }}</td>
                            <td>{{ vm.status }}</td>
                            <td>{{ vm.zone }}</td>
                            <td>{{ vm.machineType }}</td>
                            <td>{{ vm.creationTime }}</td>
                            <td>{{ vm.lastStartedTime }}</td>
                            <td>{{ vm.lastStoppedTime }}</td>
                            <td>{{ vm.daysStarted }}</td>
                            <td>{{ vm.daysStopped }}</td>
                        </tr>
                    {% endfor %}
                {% endif %}
            </table>
        </div>
    {% endif %}
</body>
</html>
"""

def check_credentials(username, password):
    if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
        return "admin"
    if username == READER_USERNAME and password == READER_PASSWORD:
        return "reader"
    return None

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "")
        password = request.form.get("password", "")
        role = check_credentials(username, password)
        if role:
            session["user"] = username
            session["role"] = role
            return redirect(url_for("index"))
        else:
            flash("Invalid username or password.")
    return render_template_string(LOGIN_PAGE_HTML)

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

@app.route("/")
def index():
    if "user" not in session or "role" not in session:
        return redirect(url_for("login"))
    return render_template_string(HOME_PAGE_HTML, role=session["role"])

@app.route("/vms", methods=["GET", "POST"])
def vms():
    if "user" not in session or "role" not in session:
        return redirect(url_for("login"))
    # Fetch project ids and geo_map from backend
    try:
        resp = requests.get(f"{BACKEND_API_URL}/gcp/options", timeout=10)
        resp.raise_for_status()
        options = resp.json()
        project_ids = options.get("project_ids", [])
        geo_map = options.get("geo_map", {})
    except Exception as e:
        return render_template_string(VM_FORM_HTML, project_ids=[], geo_map={}, error=f"Error fetching options: {e}", vms=None, selected_project_id=None, selected_geo=None, loading=False, sort_by="name", sort_dir="asc")

    vms = None
    error = None
    loading = False
    selected_project_id = project_ids[0] if project_ids else ""
    selected_geo = list(geo_map.keys())[0] if geo_map else ""
    sort_by = "name"
    sort_dir = "asc"

    if request.method == "POST":
        selected_project_id = request.form.get("project_id", "")
        selected_geo = request.form.get("geo", "")
        sort_by = request.form.get("sort_by", "name")
        sort_dir = request.form.get("sort_dir", "asc")
        if not selected_project_id or not selected_geo:
            error = "Please select a project and a location."
        else:
            loading = True
            try:
                zones = geo_map.get(selected_geo, [])
                zones_param = ",".join(zones)
                params = {"project_id": selected_project_id, "zones": zones_param}
                resp = requests.get(f"{BACKEND_API_URL}/resources/vms", params=params, timeout=VM_FETCH_TIMEOUT)
                resp.raise_for_status()
                data = resp.json()
                vms = data.get("vms", [])
                # Sort the VMs by the selected column and direction
                reverse = sort_dir == "desc"
                vms = sorted(vms, key=lambda vm: str(vm.get(sort_by, "")), reverse=reverse)
                loading = False
            except Exception as e:
                error = f"Error fetching VMs: {e}"
                loading = False

    return render_template_string(
        VM_FORM_HTML,
        project_ids=project_ids,
        geo_map=geo_map,
        vms=vms,
        error=error,
        selected_project_id=selected_project_id,
        selected_geo=selected_geo,
        loading=loading,
        sort_by=sort_by,
        sort_dir=sort_dir
    )

if __name__ == "__main__":
    app.run(debug=True)
