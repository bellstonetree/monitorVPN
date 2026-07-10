import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]


class HiddenLauncherTests(unittest.TestCase):
    def test_hidden_launcher_does_not_spawn_a_command_prompt(self) -> None:
        launcher = (PROJECT_ROOT / "run_hidden.vbs").read_text(encoding="utf-8")

        self.assertNotIn("shell.Exec", launcher)
        self.assertNotIn("cmd /c", launcher)
        self.assertIn('FindExecutableOnPath("pyw.exe")', launcher)
        self.assertIn('FindExecutableOnPath("pythonw.exe")', launcher)


if __name__ == "__main__":
    unittest.main()
