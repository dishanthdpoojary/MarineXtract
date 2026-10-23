"""Regression checks for login settings surviving terminal and server restarts."""
import tempfile
import unittest
from pathlib import Path

from werkzeug.security import check_password_hash

from backend.auth_config import load_login_config, save_local_login


class LoginConfigurationTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.path = Path(self.directory.name) / "instance" / "login.json"

    def test_saved_login_and_session_key_survive_reloads(self):
        password = "a-long-test-password"
        save_local_login("owner", password, self.path)
        first = load_login_config(self.path, {})
        second = load_login_config(self.path, {})
        self.assertEqual(first, second)
        self.assertEqual(first["LOGIN_USERNAME"], "owner")
        self.assertTrue(check_password_hash(first["LOGIN_PASSWORD_HASH"], password))
        self.assertNotIn(password, self.path.read_text())

    def test_environment_overrides_local_account(self):
        save_local_login("local-owner", "local-test-password", self.path)
        config = load_login_config(self.path, {
            "MARINEXTRACT_USERNAME": "deployed-owner",
            "MARINEXTRACT_PASSWORD": "deployed-test-password",
            "MARINEXTRACT_SECRET_KEY": "deployment-secret",
        })
        self.assertEqual(config["LOGIN_USERNAME"], "deployed-owner")
        self.assertEqual(config["SECRET_KEY"], "deployment-secret")
        self.assertTrue(check_password_hash(config["LOGIN_PASSWORD_HASH"], "deployed-test-password"))

    def test_setup_validates_before_writing(self):
        for username, password in [("", "long-test-password"), ("owner", "short")]:
            with self.assertRaises(ValueError):
                save_local_login(username, password, self.path)
        self.assertFalse(self.path.exists())

    def test_reset_invalidates_old_password_and_sessions(self):
        save_local_login("owner", "first-test-password", self.path)
        first = load_login_config(self.path, {})
        save_local_login("owner", "second-test-password", self.path)
        second = load_login_config(self.path, {})
        self.assertNotEqual(first["SECRET_KEY"], second["SECRET_KEY"])
        self.assertFalse(check_password_hash(second["LOGIN_PASSWORD_HASH"], "first-test-password"))
        self.assertTrue(check_password_hash(second["LOGIN_PASSWORD_HASH"], "second-test-password"))

    def test_missing_configuration_stays_unconfigured(self):
        self.assertIsNone(load_login_config(self.path, {})["LOGIN_PASSWORD_HASH"])
