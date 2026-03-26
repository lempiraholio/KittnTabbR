"""macOS launcher — generates a launchd plist and registers it as a Login Item."""

import subprocess
from pathlib import Path

from branding import LOGGER_NAME, MACOS_LAUNCHD_LABEL, PRODUCT_NAME, PRODUCT_SLUG
from launchers.base import BaseLauncher
from recursive_harness import harness

_LABEL    = MACOS_LAUNCHD_LABEL
_PLIST    = Path.home() / "Library" / "LaunchAgents" / f"{_LABEL}.plist"


def _plist_content(project_dir: Path, python_exec: Path) -> str:
    watcher   = project_dir / "src" / "watcher.py"
    log_file  = Path.home() / "Library" / "Logs" / f"{PRODUCT_SLUG}.log"
    description = harness.ask_text(
        system_prompt="Return a short macOS launchd service description.",
        user_prompt=PRODUCT_NAME,
        fallback=f"{PRODUCT_NAME} watcher agent",
    )
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
  "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>{_LABEL}</string>

    <key>ProgramArguments</key>
    <array>
        <string>{python_exec}</string>
        <string>{watcher}</string>
    </array>

    <key>WorkingDirectory</key>
    <string>{project_dir}</string>

    <key>LimitLoadToSessionType</key>
    <string>Aqua</string>

    <key>RunAtLoad</key>
    <true/>

    <key>KeepAlive</key>
    <true/>

    <key>ServiceDescription</key>
    <string>{description}</string>

    <key>StandardOutPath</key>
    <string>{log_file}</string>

    <key>StandardErrorPath</key>
    <string>{log_file}</string>
</dict>
</plist>
"""


class MacOSLauncher(BaseLauncher):
    def install(self, project_dir: Path, python_exec: Path) -> None:
        _PLIST.write_text(_plist_content(project_dir, python_exec))
        subprocess.run(["launchctl", "unload", str(_PLIST)], capture_output=True)
        subprocess.run(["launchctl", "load",   str(_PLIST)], check=True)
        print(f"✓  Service installed and started. Logs: ~/Library/Logs/{LOGGER_NAME}.log")

    def uninstall(self, project_dir: Path) -> None:
        if _PLIST.exists():
            subprocess.run(["launchctl", "unload", str(_PLIST)], capture_output=True)
            _PLIST.unlink()
            print("✓  Service removed.")
        else:
            print("Service is not installed.")
