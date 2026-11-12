import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import bypass_files


class MesaInstallSafetyTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.app = self.root / "app"
        self.source = self.root / "mesa"
        self.app.mkdir()
        self.source.mkdir()
        self.exe = self.app / "demo.exe"
        self.exe.write_bytes(b"executable")
        self.dll = self.source / "opengl32.dll"
        self.dll.write_bytes(b"mesa dll")

    def tearDown(self):
        self.temp.cleanup()

    def test_partial_copy_failure_restores_original_file(self):
        destination = self.app / "opengl32.dll"
        destination.write_bytes(b"original dll")
        real_copy = bypass_files.shutil.copy2

        calls = 0

        def fail_after_partial_write(source, target):
            nonlocal calls
            calls += 1
            if calls == 2:
                Path(target).write_bytes(b"partial")
                raise OSError("simulated copy failure")
            return real_copy(source, target)

        with patch("bypass_files.shutil.copy2", side_effect=fail_after_partial_write):
            with self.assertRaisesRegex(OSError, "simulated copy failure"):
                bypass_files.install_mesa_files(self.exe, self.source)

        self.assertEqual(destination.read_bytes(), b"original dll")
        self.assertFalse((self.app / bypass_files.MANIFEST).exists())
        self.assertFalse((self.app / bypass_files.BACKUP_DIR).exists())

    def test_partial_copy_failure_removes_new_partial_file(self):
        destination = self.app / "opengl32.dll"

        def fail_after_partial_write(source, target):
            Path(target).write_bytes(b"partial")
            raise OSError("simulated copy failure")

        with patch("bypass_files.shutil.copy2", side_effect=fail_after_partial_write):
            with self.assertRaisesRegex(OSError, "simulated copy failure"):
                bypass_files.install_mesa_files(self.exe, self.source)

        self.assertFalse(destination.exists())
        self.assertFalse((self.app / bypass_files.MANIFEST).exists())
        self.assertFalse((self.app / bypass_files.BACKUP_DIR).exists())

    def test_install_refuses_symlink_destination(self):
        destination = self.app / "opengl32.dll"
        protected = self.root / "protected.dll"
        protected.write_bytes(b"do not overwrite")
        try:
            destination.symlink_to(protected)
        except (OSError, NotImplementedError):
            self.skipTest("Symlink creation is unavailable on this runner")

        with self.assertRaisesRegex(ValueError, "link simbólico"):
            bypass_files.install_mesa_files(self.exe, self.source)
        self.assertEqual(protected.read_bytes(), b"do not overwrite")
        self.assertFalse((self.app / bypass_files.BACKUP_DIR).exists())

    def test_restore_refuses_symlink_destination(self):
        destination = self.app / "opengl32.dll"
        protected = self.root / "protected.dll"
        protected.write_bytes(b"do not overwrite")
        backup = self.app / bypass_files.BACKUP_DIR
        backup.mkdir()
        (backup / "opengl32.dll").write_bytes(b"original dll")
        (self.app / bypass_files.MANIFEST).write_text(
            json.dumps({"files": ["opengl32.dll"], "backup": bypass_files.BACKUP_DIR}),
            encoding="utf-8",
        )
        try:
            destination.symlink_to(protected)
        except (OSError, NotImplementedError):
            self.skipTest("Symlink creation is unavailable on this runner")

        with self.assertRaisesRegex(ValueError, "Link simbólico"):
            bypass_files.restore_mesa_files(self.exe)
        self.assertEqual(protected.read_bytes(), b"do not overwrite")
        self.assertTrue((self.app / bypass_files.MANIFEST).exists())


if __name__ == "__main__":
    unittest.main()
