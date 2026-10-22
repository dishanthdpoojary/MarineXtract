import io
import os
import secrets
from datetime import timedelta

from flask import Flask, jsonify, redirect, render_template, request, session, url_for
from PIL import Image
from werkzeug.security import check_password_hash, generate_password_hash

from backend.model_loader import model_service

app = Flask(__name__)
app.config.update(
    SECRET_KEY=os.environ.get("MARINEXTRACT_SECRET_KEY") or secrets.token_hex(32),
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
    SESSION_COOKIE_SECURE=os.environ.get("MARINEXTRACT_COOKIE_SECURE") == "1",
    PERMANENT_SESSION_LIFETIME=timedelta(hours=8),
    LOGIN_USERNAME=os.environ.get("MARINEXTRACT_USERNAME", "admin"),
    LOGIN_PASSWORD_HASH=generate_password_hash(os.environ["MARINEXTRACT_PASSWORD"])
    if os.environ.get("MARINEXTRACT_PASSWORD") else None,
)


def csrf_token():
    if "csrf_token" not in session:
        session["csrf_token"] = secrets.token_hex(32)
    return session["csrf_token"]


app.jinja_env.globals["csrf_token"] = csrf_token


@app.before_request
def require_login():
    if request.endpoint in {"index", "predict", "species_metadata", "logout"}:
        if not session.get("username"):
            if request.path.startswith("/api/"):
                return jsonify({"error": "Please sign in to continue."}), 401
            return redirect(url_for("login"))
    if request.method == "POST" and request.endpoint in {"login", "logout", "predict"}:
        token = request.form.get("csrf_token") or request.headers.get("X-CSRF-Token", "")
        if not token or not secrets.compare_digest(token, session.get("csrf_token", "")):
            if request.path.startswith("/api/"):
                return jsonify({"error": "Your session expired. Refresh the page and try again."}), 400
            return render_template("login.html", error="Your session expired. Please try again.",
                                   configured=bool(app.config["LOGIN_PASSWORD_HASH"])), 400


@app.route("/login", methods=["GET", "POST"])
def login():
    if session.get("username"):
        return redirect(url_for("index"))
    configured = bool(app.config["LOGIN_PASSWORD_HASH"])
    error = None
    status = 200
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        if not configured:
            error = "Sign-in is not configured yet. Please contact the project administrator."
            status = 503
        else:
            password_matches = check_password_hash(app.config["LOGIN_PASSWORD_HASH"], password)
            if secrets.compare_digest(username.encode(), app.config["LOGIN_USERNAME"].encode()) and password_matches:
                session.clear()
                session["username"] = username
                session.permanent = True
                return redirect(url_for("index"))
            error = "The username or password is incorrect. Please try again."
            status = 401
    return render_template("login.html", error=error, configured=configured), status


@app.route("/logout", methods=["POST"])
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.after_request
def prevent_cached_account_pages(response):
    if request.endpoint in {"login", "index", "predict", "species_metadata", "logout"}:
        response.headers["Cache-Control"] = "no-store"
    return response


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/health")
def health_check():
    return jsonify({"status": "ok", "model": "MarineXtract EfficientNetV2-S"})


@app.route("/api/predict", methods=["POST"])
def predict():
    if "image" not in request.files:
        return jsonify({"error": "No image file uploaded"}), 400

    file = request.files["image"]
    if file.filename == "":
        return jsonify({"error": "No file selected"}), 400

    try:
        image = Image.open(io.BytesIO(file.read())).convert("RGB")
        result = model_service.predict(image)
        return jsonify(result)
    except Exception as exc:  # pragma: no cover - defensive for UI errors
        return jsonify({"error": f"Prediction failed: {str(exc)}"}), 500


@app.route("/api/species")
def species_metadata():
    from backend.metadata import SPECIES_CLASSES

    return jsonify({"species": SPECIES_CLASSES})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
