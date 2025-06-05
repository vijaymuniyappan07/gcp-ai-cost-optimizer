from flask import Flask, render_template, request, redirect, url_for, session, flash
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

PAGINATION_OPTIONS = [10, 20, 50, 100, 200, 500]

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
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

@app.route("/")
def index():
    if "user" not in session or "role" not in session:
        return redirect(url_for("login"))
    return render_template("home.html", role=session["role"])

@app.route("/storage", methods=["GET", "POST"])
def storage():
    loading = True
    error = None
    storage_buckets = None
    project_ids = []
    selected_project_id = ""
    GCS_FETCH_TIMEOUT = int(os.getenv("FRONTEND_GCS_FETCH_TIMEOUT", 60))
    try:
        # Fetch project ids for the dropdown
        resp = requests.get(f"{BACKEND_API_URL}/gcp/options", timeout=10)
        resp.raise_for_status()
        options = resp.json()
        project_ids = options.get("project_ids", [])
        selected_project_id = project_ids[0] if project_ids else ""
    except Exception as e:
        error = f"Error fetching project ids: {e}"
        loading = False
        return render_template("storage.html", storage=None, error=error, loading=loading, project_ids=[], selected_project_id=None)

    sort_by = request.form.get("sort_by") or request.args.get("sort_by") or "name"
    sort_dir = request.form.get("sort_dir") or request.args.get("sort_dir") or "asc"
    if request.method == "POST":
        selected_project_id = request.form.get("project_id", "") or selected_project_id
    try:
        resp = requests.get(f"{BACKEND_API_URL}/resources/storage", params={"project_id": selected_project_id}, timeout=GCS_FETCH_TIMEOUT)
        resp.raise_for_status()
        data = resp.json()
        storage_buckets = data.get("storage", [])
        # Sorting logic
        reverse = sort_dir == "desc"
        def sort_key(bucket):
            val = bucket.get(sort_by, "")
            try:
                return float(val)
            except Exception:
                return str(val)
        storage_buckets = sorted(storage_buckets, key=sort_key, reverse=reverse)
        loading = False
    except Exception as e:
        error = f"Error fetching Cloud Storage buckets: {e}"
        loading = False
    return render_template("storage.html", storage=storage_buckets, error=error, loading=loading, project_ids=project_ids, selected_project_id=selected_project_id, sort_by=sort_by, sort_dir=sort_dir)

@app.route("/filestore", methods=["GET", "POST"])
def filestore():
    loading = True
    error = None
    filestore = None
    project_ids = []
    selected_project_id = ""
    try:
        # Fetch project ids for the dropdown
        resp = requests.get(f"{BACKEND_API_URL}/gcp/options", timeout=10)
        resp.raise_for_status()
        options = resp.json()
        project_ids = options.get("project_ids", [])
        selected_project_id = project_ids[0] if project_ids else ""
    except Exception as e:
        error = f"Error fetching project ids: {e}"
        loading = False
        return render_template("filestore.html", filestore=None, error=error, loading=loading, project_ids=[], selected_project_id=None)

    sort_by = request.form.get("sort_by") or request.args.get("sort_by") or "name"
    sort_dir = request.form.get("sort_dir") or request.args.get("sort_dir") or "asc"
    if request.method == "POST":
        selected_project_id = request.form.get("project_id", "") or selected_project_id
    try:
        resp = requests.get(f"{BACKEND_API_URL}/resources/filestore", params={"project_id": selected_project_id}, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        filestore = data.get("filestore", [])
        # Sorting logic
        reverse = sort_dir == "desc"
        def sort_key(fs):
            val = fs.get(sort_by, "")
            # Try to sort numerically if possible
            try:
                return float(val)
            except Exception:
                return str(val)
        filestore = sorted(filestore, key=sort_key, reverse=reverse)
        loading = False
    except Exception as e:
        error = f"Error fetching Filestore instances: {e}"
        loading = False
    return render_template("filestore.html", filestore=filestore, error=error, loading=loading, project_ids=project_ids, selected_project_id=selected_project_id, sort_by=sort_by, sort_dir=sort_dir)

@app.route("/gke", methods=["GET", "POST"])
def gke():
    loading = True
    error = None
    clusters = None
    project_ids = []
    selected_project_id = ""
    sort_by = request.form.get("sort_by") or request.args.get("sort_by") or "name"
    sort_dir = request.form.get("sort_dir") or request.args.get("sort_dir") or "asc"
    try:
        # Fetch project ids for the dropdown
        resp = requests.get(f"{BACKEND_API_URL}/gcp/options", timeout=10)
        resp.raise_for_status()
        options = resp.json()
        project_ids = options.get("project_ids", [])
        selected_project_id = project_ids[0] if project_ids else ""
    except Exception as e:
        error = f"Error fetching project ids: {e}"
        loading = False
        return render_template("gke.html", clusters=None, error=error, loading=loading, project_ids=[], selected_project_id=None, sort_by=sort_by, sort_dir=sort_dir)

    if request.method == "POST":
        selected_project_id = request.form.get("project_id", "") or selected_project_id
        sort_by = request.form.get("sort_by", "name")
        sort_dir = request.form.get("sort_dir", "asc")
    try:
        resp = requests.get(f"{BACKEND_API_URL}/resources/gke", params={"project_id": selected_project_id}, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        clusters = data.get("gke", [])
        # Sorting logic
        reverse = sort_dir == "desc"
        numeric_fields = {"nodeCount", "minNodeCount", "maxNodeCount"}
        def sort_key(cluster):
            val = cluster.get(sort_by, "")
            if sort_by in numeric_fields:
                try:
                    return int(str(val).split(",")[0].strip())
                except Exception:
                    return float('inf') if reverse else float('-inf')
            return str(val)
        clusters = sorted(clusters, key=sort_key, reverse=reverse)
        # Ensure each cluster has project_id for modal use
        for cluster in clusters:
            cluster["project_id"] = selected_project_id
        loading = False
    except Exception as e:
        error = f"Error fetching GKE clusters: {e}"
        loading = False
    return render_template("gke.html", clusters=clusters, error=error, loading=loading, project_ids=project_ids, selected_project_id=selected_project_id, sort_by=sort_by, sort_dir=sort_dir)

@app.route("/cloudsql", methods=["GET", "POST"])
def cloudsql():
    loading = True
    error = None
    instances = None
    project_ids = []
    selected_project_id = ""
    sort_by = request.form.get("sort_by") or request.args.get("sort_by") or "name"
    sort_dir = request.form.get("sort_dir") or request.args.get("sort_dir") or "asc"
    try:
        # Fetch project ids for the dropdown
        resp = requests.get(f"{BACKEND_API_URL}/gcp/options", timeout=10)
        resp.raise_for_status()
        options = resp.json()
        project_ids = options.get("project_ids", [])
        selected_project_id = project_ids[0] if project_ids else ""
    except Exception as e:
        error = f"Error fetching project ids: {e}"
        loading = False
        return render_template("cloudsql.html", instances=None, error=error, loading=loading, project_ids=[], selected_project_id=None, sort_by=sort_by, sort_dir=sort_dir)

    if request.method == "POST":
        selected_project_id = request.form.get("project_id", "") or selected_project_id
        sort_by = request.form.get("sort_by", "name")
        sort_dir = request.form.get("sort_dir", "asc")
    try:
        resp = requests.get(f"{BACKEND_API_URL}/resources/cloudsql", params={"project_id": selected_project_id}, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        instances = data.get("cloudsql", [])
        # Sorting logic
        reverse = sort_dir == "desc"
        numeric_fields = {"dataDiskSizeGb"}
        def sort_key(inst):
            val = inst.get(sort_by, "")
            if sort_by in numeric_fields:
                try:
                    return int(val)
                except Exception:
                    return float('inf') if reverse else float('-inf')
            return str(val)
        instances = sorted(instances, key=sort_key, reverse=reverse)
        loading = False
    except Exception as e:
        error = f"Error fetching Cloud SQL instances: {e}"
        loading = False
    return render_template("cloudsql.html", instances=instances, error=error, loading=loading, project_ids=project_ids, selected_project_id=selected_project_id, sort_by=sort_by, sort_dir=sort_dir)

@app.route("/gke/resize", methods=["POST"])
def gke_resize():
    if "user" not in session or "role" not in session:
        return {"success": False, "message": "Unauthorized"}, 401
    try:
        data = request.get_json()
        print("Received resize payload in Flask:", data, flush=True)
        if not data:
            return {"success": False, "message": "No data provided"}, 400
        # Forward the request to the backend API
        resp = requests.post(
            f"{BACKEND_API_URL}/resources/gke/resize",
            json=data,
            timeout=60
        )
        resp.raise_for_status()
        backend_response = resp.json()
        return backend_response, resp.status_code
    except Exception as e:
        return {"success": False, "message": f"Error forwarding resize request: {e}"}, 500

@app.route("/vms", methods=["GET", "POST"])
def vms():
    if "user" not in session or "role" not in session:
        return redirect(url_for("login"))
    try:
        resp = requests.get(f"{BACKEND_API_URL}/gcp/options", timeout=10)
        resp.raise_for_status()
        options = resp.json()
        project_ids = options.get("project_ids", [])
        geo_map = options.get("geo_map", {})
    except Exception as e:
        return render_template("vms.html", project_ids=[], geo_map={}, error=f"Error fetching options: {e}", vms=None, selected_project_id=None, selected_geo=None, loading=False, sort_by="name", sort_dir="asc", page=1, page_size=10, total_pages=1, pagination_options=PAGINATION_OPTIONS)

    vms = None
    error = None
    loading = False
    selected_project_id = project_ids[0] if project_ids else ""
    selected_geo = list(geo_map.keys())[0] if geo_map else ""
    sort_by = request.form.get("sort_by") or request.args.get("sort_by") or "name"
    sort_dir = request.form.get("sort_dir") or request.args.get("sort_dir") or "asc"
    if request.method == "POST":
        try:
            page = int(request.form.get("page", 1))
        except Exception:
            page = 1
        try:
            page_size = int(request.form.get("page_size", 10))
            if page_size not in PAGINATION_OPTIONS:
                page_size = 10
        except Exception:
            page_size = 10
    else:
        try:
            page = int(request.args.get("page", 1))
        except Exception:
            page = 1
        try:
            page_size = int(request.args.get("page_size", 10))
            if page_size not in PAGINATION_OPTIONS:
                page_size = 10
        except Exception:
            page_size = 10
    total_pages = 1
    total_vms = 0

    if request.method == "POST":
        selected_project_id = request.form.get("project_id", "")
        selected_geo = request.form.get("geo", "")
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
                reverse = sort_dir == "desc"
                numeric_fields = {"daysStarted", "daysStopped"}
                def sort_key(vm):
                    val = vm.get(sort_by, "")
                    if sort_by == "diskSizes":
                        try:
                            first_size = int(str(val).split(",")[0].strip())
                            return first_size
                        except Exception:
                            return float('inf') if reverse else float('-inf')
                    if sort_by == "memory":
                        # Parse "12 GB" as 12.0
                        try:
                            num = float(str(val).split()[0])
                            return num
                        except Exception:
                            return float('inf') if reverse else float('-inf')
                    if sort_by in numeric_fields:
                        try:
                            return int(val)
                        except Exception:
                            return float('inf') if reverse else float('-inf')
                    return str(val)
                vms = sorted(vms, key=sort_key, reverse=reverse)
                total_vms = len(vms)
                total_pages = max(1, (total_vms + page_size - 1) // page_size)
                start = (page - 1) * page_size
                end = start + page_size
                vms = vms[start:end]
                loading = False
            except Exception as e:
                error = f"Error fetching VMs: {e}"
                loading = False
    else:
        total_pages = 1
        page = 1
        page_size = 10
        total_vms = 0

    page_numbers = list(range(1, total_pages + 1))

    return render_template(
        "vms.html",
        project_ids=project_ids,
        geo_map=geo_map,
        vms=vms,
        error=error,
        selected_project_id=selected_project_id,
        selected_geo=selected_geo,
        loading=loading,
        sort_by=sort_by,
        sort_dir=sort_dir,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
        page_numbers=page_numbers,
        total_vms=total_vms,
        pagination_options=PAGINATION_OPTIONS
    )

if __name__ == "__main__":
    app.run(debug=True)
