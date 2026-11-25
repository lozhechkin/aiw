from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

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
        self.assertEqual(self.call("--version").stdout.strip(), "0.1.0")

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
