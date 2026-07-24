"""Desktop indicator for a selected Windows network interface status."""

from __future__ import annotations

import json
import subprocess
import sys
from dataclasses import dataclass
from locale import getpreferredencoding
from pathlib import Path
from typing import Optional

from runtime_environment import MissingRuntimeComponents, require_runtime_environment


CONFIG_FILE = Path(__file__).with_name("vpn_monitor_config.json")
ANYCAST_EXECUTABLE = Path(r"C:\Program Files (x86)\Anycast\Anycast.exe")
REFRESH_INTERVAL_MS = 1000
DOT_SIZE = 28
WINDOW_MARGIN_RIGHT = 24
WINDOW_MARGIN_TOP = 80

CONNECTED_COLOR = "#18a558"
DISCONNECTED_COLOR = "#d72638"
UNSELECTED_COLOR = "#8a8f98"
OUTLINE_COLOR = "#ffffff"
TRANSPARENT_COLOR = "#010203"


@dataclass(frozen=True)
class InterfaceStatus:
    found: bool
    connected: bool
    state: str = "Unknown"
    error: Optional[str] = None


@dataclass(frozen=True)
class NetworkInterface:
    name: str
    state: str


@dataclass(frozen=True)
class NetshResult:
    output: str = ""
    error: Optional[str] = None


def load_selected_interface() -> Optional[str]:
    try:
        data = json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return None

    interface_name = data.get("interface_name")
    if isinstance(interface_name, str) and interface_name.strip():
        return interface_name

    return None


def save_selected_interface(interface_name: str) -> None:
    data = {"interface_name": interface_name}
    CONFIG_FILE.write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def start_anycast() -> None:
    try:
        subprocess.Popen([str(ANYCAST_EXECUTABLE)])
    except OSError:
        pass


def get_interface_status(interface_name: str) -> InterfaceStatus:
    """Return the status for a Windows network interface reported by netsh."""
    ipv4_status = get_interface_status_from_ipv4_netsh(interface_name)
    if ipv4_status.found or ipv4_status.error is not None:
        return ipv4_status

    return get_interface_status_from_netsh(interface_name)


def get_interface_status_from_ipv4_netsh(interface_name: str) -> InterfaceStatus:
    """Use netsh's IPv4 table, whose state values remain English when hidden."""
    result = run_netsh(["interface", "ipv4", "show", "interfaces"])
    if result.error is not None:
        return InterfaceStatus(found=False, connected=False, error=result.error)

    for line in result.output.splitlines():
        parsed = parse_netsh_ipv4_interface_line(line)
        if parsed is None:
            continue

        name, state = parsed
        if name == interface_name:
            return InterfaceStatus(
                found=True,
                connected=state.casefold() == "connected",
                state=state,
            )

    return InterfaceStatus(found=False, connected=False, state="Missing")


def get_interface_status_from_netsh(interface_name: str) -> InterfaceStatus:
    """Fallback to the general netsh interface table."""
    result = run_netsh(["interface", "show", "interface"])
    if result.error is not None:
        return InterfaceStatus(found=False, connected=False, error=result.error)

    connected_states = {"connected", "已连接"}
    for line in result.output.splitlines():
        parsed = parse_netsh_interface_line(line)
        if parsed is None:
            continue

        name, state = parsed
        if name == interface_name:
            return InterfaceStatus(
                found=True,
                connected=state.casefold() in connected_states,
                state=state,
            )

    return InterfaceStatus(found=False, connected=False, state="Missing")


def list_network_interfaces() -> list[NetworkInterface]:
    result = run_netsh(["interface", "ipv4", "show", "interfaces"])
    if result.error is not None:
        return []

    interfaces = []
    for line in result.output.splitlines():
        parsed = parse_netsh_ipv4_interface_line(line)
        if parsed is None:
            continue

        name, state = parsed
        interfaces.append(NetworkInterface(name=name, state=state))

    return interfaces


def run_netsh(arguments: list[str]) -> NetshResult:
    try:
        result = subprocess.run(
            ["netsh", *arguments],
            capture_output=True,
            check=False,
            creationflags=subprocess.CREATE_NO_WINDOW,
        )
    except Exception as exc:
        return NetshResult(error=str(exc))

    if result.returncode != 0:
        output = decode_netsh_output(result.stderr or result.stdout)
        return NetshResult(error=(output or "netsh failed").strip())

    return NetshResult(output=decode_netsh_output(result.stdout))


def decode_netsh_output(output: bytes) -> str:
    encodings = ("utf-8", getpreferredencoding(False), "mbcs", "gbk")
    for encoding in encodings:
        try:
            return output.decode(encoding)
        except UnicodeDecodeError:
            continue

    return output.decode(getpreferredencoding(False), errors="replace")


def parse_netsh_ipv4_interface_line(line: str) -> Optional[tuple[str, str]]:
    stripped = line.strip()
    if (
        not stripped
        or stripped.startswith("Idx")
        or stripped.startswith("---")
    ):
        return None

    parts = stripped.split()
    if len(parts) < 5 or not parts[0].isdigit():
        return None

    state = parts[3]
    name = " ".join(parts[4:])
    return name, state


def parse_netsh_interface_line(line: str) -> Optional[tuple[str, str]]:
    """Parse one data row from 'netsh interface show interface' output."""
    stripped = line.strip()
    if (
        not stripped
        or stripped.startswith("Admin State")
        or stripped.startswith("管理员状态")
        or stripped.startswith("----")
    ):
        return None

    parts = stripped.split()
    if len(parts) < 4:
        return None

    state = parts[1]
    name = " ".join(parts[3:])
    return name, state


class VpnIndicator:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.drag_start_x = 0
        self.drag_start_y = 0
        self.selected_interface = load_selected_interface()
        self.last_status = InterfaceStatus(found=False, connected=False)
        self.tooltip: Optional[tk.Toplevel] = None

        self.root.title("VPN Monitor")
        self.root.overrideredirect(True)
        self.root.attributes("-topmost", True)
        self.root.configure(bg=TRANSPARENT_COLOR)
        self.root.wm_attributes("-transparentcolor", TRANSPARENT_COLOR)

        screen_width = self.root.winfo_screenwidth()
        start_x = max(0, screen_width - DOT_SIZE - WINDOW_MARGIN_RIGHT)
        start_y = WINDOW_MARGIN_TOP
        self.root.geometry(f"{DOT_SIZE}x{DOT_SIZE}+{start_x}+{start_y}")

        self.canvas = tk.Canvas(
            self.root,
            width=DOT_SIZE,
            height=DOT_SIZE,
            bg=TRANSPARENT_COLOR,
            highlightthickness=0,
            bd=0,
        )
        self.canvas.pack(fill="both", expand=True)
        pad = 2
        self.dot = self.canvas.create_oval(
            pad,
            pad,
            DOT_SIZE - pad,
            DOT_SIZE - pad,
            fill=UNSELECTED_COLOR,
            outline=OUTLINE_COLOR,
            width=2,
        )

        self.menu = tk.Menu(self.root, tearoff=False)

        self.root.bind("<ButtonPress-1>", self.start_drag)
        self.root.bind("<B1-Motion>", self.drag)
        self.root.bind("<Double-Button-1>", self.launch_anycast)
        self.root.bind("<Button-3>", self.show_menu)
        self.root.bind("<Enter>", self.show_tooltip)
        self.root.bind("<Leave>", self.hide_tooltip)
        self.root.bind("<Escape>", lambda _event: self.root.destroy())

        self.refresh()

    def start_drag(self, event: tk.Event) -> None:
        self.drag_start_x = event.x
        self.drag_start_y = event.y

    def drag(self, event: tk.Event) -> None:
        x = self.root.winfo_x() + event.x - self.drag_start_x
        y = self.root.winfo_y() + event.y - self.drag_start_y
        self.root.geometry(f"+{x}+{y}")

    def launch_anycast(self, _event: Optional[tk.Event] = None) -> None:
        start_anycast()

    def show_menu(self, event: tk.Event) -> None:
        self.rebuild_menu()
        self.menu.tk_popup(event.x_root, event.y_root)

    def rebuild_menu(self) -> None:
        self.menu.delete(0, "end")

        interface_menu = tk.Menu(self.menu, tearoff=False)
        interfaces = list_network_interfaces()
        if interfaces:
            for network_interface in interfaces:
                label = f"{network_interface.name} ({network_interface.state})"
                if network_interface.name == self.selected_interface:
                    label = f"* {label}"

                interface_menu.add_command(
                    label=label,
                    command=lambda name=network_interface.name: self.select_interface(name),
                )
        else:
            interface_menu.add_command(label="No interfaces found", state="disabled")

        self.menu.add_cascade(label="Select interface", menu=interface_menu)
        self.menu.add_separator()
        self.menu.add_command(label="Exit", command=self.root.destroy)

    def select_interface(self, interface_name: str) -> None:
        self.selected_interface = interface_name
        save_selected_interface(interface_name)
        self.refresh()

    def show_tooltip(self, _event: Optional[tk.Event] = None) -> None:
        self.hide_tooltip()

        self.tooltip = tk.Toplevel(self.root)
        self.tooltip.overrideredirect(True)
        self.tooltip.attributes("-topmost", True)
        self.tooltip.configure(bg="#222222")

        label = tk.Label(
            self.tooltip,
            text=self.status_text(),
            bg="#222222",
            fg="#ffffff",
            padx=8,
            pady=4,
            font=("Segoe UI", 9),
        )
        label.pack()

        x = self.root.winfo_x()
        y = self.root.winfo_y() + DOT_SIZE + 6
        self.tooltip.geometry(f"+{x}+{y}")

    def hide_tooltip(self, _event: Optional[tk.Event] = None) -> None:
        if self.tooltip is not None:
            self.tooltip.destroy()
            self.tooltip = None

    def refresh(self) -> None:
        if self.selected_interface is None:
            self.last_status = InterfaceStatus(
                found=False,
                connected=False,
                state="Unselected",
            )
            color = UNSELECTED_COLOR
        else:
            self.last_status = get_interface_status(self.selected_interface)
            color = CONNECTED_COLOR if self.last_status.connected else DISCONNECTED_COLOR

        self.canvas.itemconfigure(self.dot, fill=color)
        self.root.title(self.status_text())
        if self.tooltip is not None:
            self.show_tooltip()
        self.root.after(REFRESH_INTERVAL_MS, self.refresh)

    def status_text(self) -> str:
        if self.selected_interface is None:
            return "No interface selected"

        if self.last_status.connected:
            return f"{self.selected_interface}: Connected"
        if self.last_status.found:
            return f"{self.selected_interface}: {self.last_status.state}"
        if self.last_status.error:
            return f"{self.selected_interface}: Check failed"
        return f"{self.selected_interface}: Not found"


def main() -> None:
    global tk

    require_runtime_environment()
    import tkinter as tk

    root = tk.Tk()
    VpnIndicator(root)
    root.mainloop()


if __name__ == "__main__":
    try:
        main()
    except MissingRuntimeComponents as exc:
        print(exc, file=sys.stderr)
        sys.exit(1)
