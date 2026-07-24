import unittest
from unittest.mock import patch

from vpn_monitor import ANYCAST_EXECUTABLE, start_anycast


class AnycastLauncherTests(unittest.TestCase):
    @patch("vpn_monitor.subprocess.Popen")
    def test_double_click_action_launches_executable(self, popen) -> None:
        start_anycast()

        popen.assert_called_once_with([str(ANYCAST_EXECUTABLE)])

    @patch("vpn_monitor.subprocess.Popen", side_effect=OSError("not found"))
    def test_launch_error_is_silently_ignored(self, _popen) -> None:
        start_anycast()


if __name__ == "__main__":
    unittest.main()
