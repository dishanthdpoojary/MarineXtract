"""Pages must respond without importing the inference runtime."""
import subprocess
import sys
import unittest
from pathlib import Path


class StartupTests(unittest.TestCase):
    def test_login_renders_without_loading_torch_or_checkpoint(self):
        check = subprocess.run(
            [sys.executable, "-c", "\n".join([
                "import sys",
                "sys.modules['backend.model_loader'] = None",
                "from app import app",
                "response = app.test_client().get('/login')",
                "assert response.status_code == 200",
                "assert b'Sign in to your workspace' in response.data",
                "assert 'torch' not in sys.modules",
            ])],
            cwd=Path(__file__).resolve().parent.parent,
            capture_output=True, text=True, timeout=15,
        )
        self.assertEqual(check.returncode, 0, check.stderr)
