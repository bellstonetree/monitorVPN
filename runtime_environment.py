"""Runtime dependency checks shared by all VPN Monitor launch paths."""

from __future__ import annotations

import importlib
import shutil
import sys
from collections.abc import Callable, Sequence


MINIMUM_PYTHON_VERSION = (3, 9)


class MissingRuntimeComponents(RuntimeError):
    """Raised when one or more required runtime components are unavailable."""

    def __init__(self, components: Sequence[str]) -> None:
        self.components = tuple(components)
        super().__init__(format_missing_components(self.components))


def detect_missing_components(
    *,
    platform_name: str | None = None,
    version_info: Sequence[int] | None = None,
    module_loader: Callable[[str], object] | None = None,
    executable_finder: Callable[[str], str | None] | None = None,
) -> list[str]:
    """Return the display names of unavailable required components."""
    current_platform = platform_name if platform_name is not None else sys.platform
    current_version = version_info if version_info is not None else sys.version_info
    load_module = module_loader if module_loader is not None else importlib.import_module
    find_executable = (
        executable_finder if executable_finder is not None else shutil.which
    )

    missing = []
    if current_platform != "win32":
        missing.append("Microsoft Windows")

    if tuple(current_version[:2]) < MINIMUM_PYTHON_VERSION:
        missing.append("Python 3.9+")

    try:
        load_module("tkinter")
    except (ImportError, OSError):
        missing.append("Tkinter")

    if find_executable("netsh") is None:
        missing.append("netsh")

    return missing


def format_missing_components(components: Sequence[str]) -> str:
    component_list = "\n".join(f"- {component}" for component in components)
    return (
        "VPN Monitor cannot start because required components are missing:\n\n"
        f"{component_list}\n\n"
        "Install or enable the listed components, then try again."
    )


def require_runtime_environment() -> None:
    """Raise a user-facing error when the local runtime is incomplete."""
    missing = detect_missing_components()
    if missing:
        raise MissingRuntimeComponents(missing)
