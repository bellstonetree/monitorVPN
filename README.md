# VPN Monitor

Windows desktop indicator for a selected network interface.

The app shows a small always-on-top dot:

- Gray: no interface is selected
- Green: the selected interface is connected
- Red: the selected interface is disconnected, missing, or cannot be checked

## Requirements

- Windows
- Python 3 with Tkinter

This project uses only the Python standard library. No third-party packages are required.

## Run

Double-click `run_hidden.vbs` to start without a command prompt window.
If hidden startup fails, an error dialog is shown and details are saved to
`vpn_monitor_error.log`.

For troubleshooting, double-click `run.bat`, or run:

```powershell
python vpn_monitor.py
```

If `python` is not available, install Python 3 from:

https://www.python.org/downloads/windows/

During installation, enable "Add python.exe to PATH".

## Controls

- Drag the dot with the left mouse button to move it.
- Right-click the dot and choose `Select interface` to pick the interface to monitor.
- Right-click the dot and choose `Exit` to close it.
- Press `Esc` while the dot has focus to close it.

## Configuration

The selected interface is saved to `vpn_monitor_config.json` next to the script.
On the next launch, the app uses the saved interface automatically.

Edit these constants near the top of `vpn_monitor.py` if needed:

```python
REFRESH_INTERVAL_MS = 1000
DOT_SIZE = 28
WINDOW_MARGIN_RIGHT = 24
WINDOW_MARGIN_TOP = 80
```

Interface names are read from:

```powershell
netsh interface ipv4 show interfaces
```

## Status Check

The program primarily runs:

```powershell
netsh interface ipv4 show interfaces
```

It treats the selected interface as connected only when that interface row reports `State` as `connected`.
