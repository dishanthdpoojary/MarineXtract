"""Authentication checks without loading the image-classification checkpoint."""
import importlib
import sys
import unittest
from unittest.mock import patch, Mock

from werkzeug.security import generate_password_hash


class AuthenticationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with patch.dict(sys.modules, {"backend.model_loader": Mock()}):
            cls.module = importlib.import_module("app")
        cls.app = cls.module.app
        cls.app.config.update(TESTING=True, SECRET_KEY="test-session-key",
                              LOGIN_USERNAME="researcher",
                              LOGIN_PASSWORD_HASH=generate_password_hash("test-password"))

    def setUp(self):
        self.client = self.app.test_client()

    def token(self):
        self.client.get("/login")
        with self.client.session_transaction() as session:
            return session["csrf_token"]

    def sign_in(self, password="test-password"):
        return self.client.post("/login", data={"username": "researcher",
                                "password": password, "csrf_token": self.token()})

    def test_anonymous_access(self):
        self.assertEqual(self.client.get("/").location, "/login")
        self.assertEqual(self.client.get("/api/species").status_code, 401)
        self.assertEqual(self.client.post("/api/predict").status_code, 401)
        self.assertEqual(self.client.get("/api/health").status_code, 200)

    def test_login_logout_and_protected_access(self):
        self.assertEqual(self.sign_in().location, "/")
        page = self.client.get("/")
        self.assertEqual(page.status_code, 200)
        self.assertIn(b"Sign out", page.data)
        self.assertEqual(page.headers["Cache-Control"], "no-store")
        self.assertEqual(self.client.get("/login").location, "/")
        self.assertEqual(self.client.get("/api/species").status_code, 200)
        with self.client.session_transaction() as session:
            token = session["csrf_token"]
        self.assertEqual(self.client.post("/logout", data={"csrf_token": token}).location, "/login")
        self.assertEqual(self.client.get("/").location, "/login")

    def test_incorrect_password(self):
        response = self.sign_in("wrong-password")
        self.assertEqual(response.status_code, 401)
        self.assertIn(b"username or password is incorrect", response.data)
        self.assertEqual(self.client.get("/").location, "/login")

    def test_csrf_is_required(self):
        self.assertEqual(self.client.post("/login", data={"username": "researcher",
                         "password": "test-password"}).status_code, 400)
        self.sign_in()
        self.assertEqual(self.client.post("/logout").status_code, 400)
        self.assertEqual(self.client.post("/api/predict").status_code, 400)

    def test_missing_configuration(self):
        with patch.dict(self.app.config, {"LOGIN_PASSWORD_HASH": None}):
            self.assertIn(b"disabled", self.client.get("/login").data)
            self.assertEqual(self.sign_in().status_code, 503)


if __name__ == "__main__":
    unittest.main()
