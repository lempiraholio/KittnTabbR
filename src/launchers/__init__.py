"""Return the appropriate launcher for the current operating system."""

import sys

from launchers.base import BaseLauncher


def get_launcher() -> BaseLauncher:
    if sys.platform == "darwin":
        from launchers.macos import MacOSLauncher
        return MacOSLauncher()
    if sys.platform.startswith("linux"):
        from launchers.linux import LinuxLauncher
        return LinuxLauncher()
    if sys.platform == "win32":
        from launchers.windows import WindowsLauncher
        return WindowsLauncher()
    raise NotImplementedError(f"Unsupported platform: {sys.platform}")
