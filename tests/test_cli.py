import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

CLI = Path(__file__).resolve().parents[1] / "aiworkspace.py"


class WorkspaceTest(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.temp = Path(temporary.name)
        self.root = self.temp / "space with spaces"

    def call(self, *args):
        return subprocess.run(
            [sys.executable, str(CLI), *map(str, args)], capture_output=True, text=True
        )

    def test_version(self):
        self.assertEqual(self.call("--version").stdout.strip(), "0.2.0")

    def test_setup_can_resume_without_overwriting(self):
        self.root.mkdir()
        url = "https://github.com/example/pilot"
        self.assertEqual(self.call("setup", self.root, "demo", "--github", url).returncode, 0)
        brief = self.root / "10 Projects" / "demo" / "PROJECT.md"
        brief.write_text("Keep my edits")
        self.assertEqual(self.call("setup", self.root, "demo", "--github", url).returncode, 0)
        self.assertEqual(self.call("setup", self.root, "demo", "--github", url + "2").returncode, 1)
        self.assertEqual(brief.read_text(), "Keep my edits")

    def test_doctor_checks_parent_without_creating_it(self):
        self.assertEqual(self.call("doctor", "--workspace-parent", self.temp).returncode, 0)
        self.assertEqual(self.call("doctor", "--workspace-parent", self.root).returncode, 1)
        self.assertFalse(self.root.exists())

    def test_lifecycle(self):
        self.assertEqual(self.call("init", self.root).returncode, 0)
        self.assertEqual(self.call("new", self.root, "demo").returncode, 0)
        self.assertIn("1 project(s)", self.call("check", self.root).stdout)
        project = self.root / "10 Projects" / "demo"
        self.assertTrue((project / "PROJECT.md").read_text().startswith("# demo\n"))
        self.assertTrue((project / "HANDOFF.md").is_file())

    def test_nonempty_root_is_preserved(self):
        self.root.mkdir()
        existing = self.root / "existing.txt"
        existing.write_text("keep")
        self.assertEqual(self.call("init", self.root).returncode, 1)
        self.assertEqual(list(self.root.iterdir()), [existing])
        self.assertEqual(existing.read_text(), "keep")

    def test_duplicate_project_is_preserved(self):
        self.assertEqual(self.call("init", self.root).returncode, 0)
        self.assertEqual(self.call("new", self.root, "demo").returncode, 0)
        brief = self.root / "10 Projects" / "demo" / "PROJECT.md"
        brief.write_text("Edited")
        self.assertEqual(self.call("new", self.root, "demo").returncode, 1)
        self.assertEqual(brief.read_text(), "Edited")

    def test_refuses_invalid_slug(self):
        self.assertEqual(self.call("init", self.root).returncode, 0)
        self.assertEqual(self.call("new", self.root, "../elsewhere").returncode, 1)
        self.assertEqual(list((self.root / "10 Projects").iterdir()), [])

    def test_github_link_and_clone_with_local_git_transport(self):
        repo = self.temp / "remote"
        repo.mkdir()
        subprocess.run(["git", "init", str(repo)], check=True, capture_output=True)
        (repo / "README.md").write_text("Pilot")
        subprocess.run(["git", "-C", str(repo), "add", "README.md"], check=True)
        subprocess.run(["git", "-C", str(repo), "-c", "user.name=Pilot",
                        "-c", "user.email=pilot@example.invalid", "commit", "-m", "Pilot"],
                       check=True, capture_output=True)
        url = "https://github.com/example/pilot"
        self.assertEqual(self.call("init", self.root).returncode, 0)
        self.assertEqual(self.call("new", self.root, "demo", "--github", url).returncode, 0)
        self.assertEqual(self.call("check", self.root).returncode, 0)
        project = self.root / "10 Projects" / "demo"
        self.assertEqual((project / "REPOSITORY").read_text().strip(), url)
        self.assertIn(url, (project / "PROJECT.md").read_text())
        self.assertEqual(self.call("clone", self.root, "demo", self.root / "checkout").returncode, 1)
        checkout = self.temp / "checkout"
        with patch.dict(os.environ, {"GIT_CONFIG_COUNT": "1",
                                     "GIT_CONFIG_KEY_0": f"url.{repo.as_uri()}.insteadOf",
                                     "GIT_CONFIG_VALUE_0": url}):
            result = self.call("clone", self.root, "demo", checkout)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual((checkout / "README.md").read_text(), "Pilot")
        setup_root = self.temp / "setup workspace"
        setup_checkout = self.temp / "setup checkout"
        with patch.dict(os.environ, {"GIT_CONFIG_COUNT": "1",
                                     "GIT_CONFIG_KEY_0": f"url.{repo.as_uri()}.insteadOf",
                                     "GIT_CONFIG_VALUE_0": url}):
            result = self.call("setup", setup_root, "demo", "--github", url, "--checkout", setup_checkout)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual((setup_checkout / "README.md").read_text(), "Pilot")

    def test_setup_reuses_checkout_and_rejects_unrelated_directory(self):
        url = "https://github.com/example/pilot"
        checkout = self.temp / "checkout"
        checkout.mkdir()
        args = ("setup", self.root, "demo", "--github", url, "--checkout", checkout)
        self.assertEqual(self.call(*args).returncode, 1)
        self.assertFalse(self.root.exists())
        subprocess.run(["git", "init", str(checkout)], check=True, capture_output=True)
        subprocess.run(["git", "-C", str(checkout), "remote", "add", "origin", url], check=True)
        for _ in range(2):
            result = self.call(*args)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("Existing checkout verified", result.stdout)

    def test_github_url_cannot_carry_credentials(self):
        self.assertEqual(self.call("init", self.root).returncode, 0)
        for url in ("https://user@github.com/example/pilot", "https://github.com/example/pilot?x=y",
                    "https://example.org/example/pilot", "https://github.com/example/.."):
            with self.subTest(url=url):
                result = self.call("new", self.root, "demo", "--github", url)
                self.assertEqual(result.returncode, 1)
                self.assertNotIn(url, result.stderr)
        self.assertEqual(list((self.root / "10 Projects").iterdir()), [])

    def test_check_reports_missing_file_without_writing(self):
        self.assertEqual(self.call("init", self.root).returncode, 0)
        self.assertEqual(self.call("new", self.root, "demo").returncode, 0)
        handoff = self.root / "10 Projects" / "demo" / "HANDOFF.md"
        handoff.unlink()
        check = self.call("check", self.root)
        self.assertEqual(check.returncode, 1)
        self.assertIn("HANDOFF.md", check.stderr)
        self.assertFalse(handoff.exists())


if __name__ == "__main__":
    unittest.main()
