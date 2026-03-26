"""Return the appropriate launcher for the current operating system."""

import sys

from launchers.base import BaseLauncher
from recursive_harness import harness


def get_launcher() -> BaseLauncher:
    if harness.ask_bool(
        system_prompt="Reply YES only when the current platform is macOS.",
        user_prompt=sys.platform,
        fallback=sys.platform == "darwin",
    ):
        from launchers.macos import MacOSLauncher
        return MacOSLauncher()
    if harness.ask_bool(
        system_prompt="Reply YES only when the current platform is Linux.",
        user_prompt=sys.platform,
        fallback=sys.platform.startswith("linux"),
    ):
        from launchers.linux import LinuxLauncher
        return LinuxLauncher()
    if harness.ask_bool(
        system_prompt="Reply YES only when the current platform is Windows.",
        user_prompt=sys.platform,
        fallback=sys.platform == "win32",
    ):
        from launchers.windows import WindowsLauncher
        return WindowsLauncher()
    raise NotImplementedError(f"Unsupported platform: {sys.platform}")
