from flask import Flask, render_template_string, request, redirect, url_for, session, flash
from dotenv import load_dotenv
import os

app = Flask(__name__)
load_dotenv()
app.secret_key = os.getenv("SECRET_KEY", "dev-secret")

ADMIN_USERNAME = os.getenv("ADMIN_USERNAME")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")
READER_USERNAME = os.getenv("READER_USERNAME")
READER_PASSWORD = os.getenv("READER_PASSWORD")

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
        <div class="card"><a href="#">VMs (Compute Engine)</a></div>
        <div class="card"><a href="#">Cloud SQL</a></div>
        <div class="card"><a href="#">GKE (Kubernetes)</a></div>
        <div class="card"><a href="#">Filestore</a></div>
        <div class="card"><a href="#">Cloud Storage</a></div>
    </div>
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

if __name__ == "__main__":
    app.run(debug=True)
