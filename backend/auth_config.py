"""Persistent local sign-in settings; deployment environment variables take priority."""
import json
import os
import secrets
from pathlib import Path

from werkzeug.security import generate_password_hash

LOGIN_SETTINGS_PATH = Path(__file__).resolve().parent.parent / "instance" / "login.json"


def save_local_login(username, password, path=LOGIN_SETTINGS_PATH):
    username = username.strip()
    if not username or len(username) > 150:
        raise ValueError("Choose a username between 1 and 150 characters.")
    if len(password) < 12:
        raise ValueError("Choose a password with at least 12 characters.")
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    settings = {
        "username": username,
        "password_hash": generate_password_hash(password),
        "secret_key": secrets.token_hex(32),
    }
    # Replace the complete file so an interrupted write cannot truncate an existing login.
    temporary_path = path.with_suffix(".tmp")
    temporary_path.write_text(json.dumps(settings, indent=2), encoding="utf-8")
    temporary_path.replace(path)


def load_login_config(path=LOGIN_SETTINGS_PATH, environ=None):
    environ = os.environ if environ is None else environ
    path = Path(path)
    settings = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}
    password = environ.get("MARINEXTRACT_PASSWORD")
    return {
        "LOGIN_USERNAME": environ.get("MARINEXTRACT_USERNAME", "admin")
        if password else settings.get("username", "admin"),
        "LOGIN_PASSWORD_HASH": generate_password_hash(password)
        if password else settings.get("password_hash"),
        "SECRET_KEY": environ.get("MARINEXTRACT_SECRET_KEY")
        or settings.get("secret_key") or secrets.token_hex(32),
    }
