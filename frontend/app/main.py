from flask import Flask

app = Flask(__name__)

@app.route("/")
def index():
    """
    Root route for the frontend web UI.
    """
    return "<h1>GCP AI Cost Optimizer Frontend</h1><p>Welcome to the MVP Flask UI.</p>"

if __name__ == "__main__":
    app.run(debug=True)
