"""Launch the VPN monitor with visible error reporting for pythonw.exe."""

from __future__ import annotations

import ctypes
import sys
import traceback
from pathlib import Path


LOG_FILE = Path(__file__).with_name("vpn_monitor_error.log")


def show_error(message: str) -> None:
    ctypes.windll.user32.MessageBoxW(None, message, "VPN Monitor failed to start", 0x10)


def main() -> int:
    try:
        from vpn_monitor import main as run_monitor

        run_monitor()
        return 0
    except Exception:
        details = traceback.format_exc()
        LOG_FILE.write_text(details, encoding="utf-8")
        show_error(
            "VPN Monitor failed to start.\n\n"
            f"Error details were saved to:\n{LOG_FILE}"
        )
        return 1


if __name__ == "__main__":
    sys.exit(main())
