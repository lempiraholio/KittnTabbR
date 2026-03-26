"""Linux launcher — generates a systemd user service and enables it."""

import subprocess
from pathlib import Path

from launchers.base import BaseLauncher

_SERVICE_NAME = "kittntabbr.service"
_SERVICE_DIR  = Path.home() / ".config" / "systemd" / "user"
_SERVICE_FILE = _SERVICE_DIR / _SERVICE_NAME


def _unit_content(project_dir: Path, python_exec: Path) -> str:
    watcher = project_dir / "src" / "watcher.py"
    return f"""[Unit]
Description=KittnTabbR — Guitar Pro file watcher
After=network.target

[Service]
ExecStart={python_exec} {watcher}
WorkingDirectory={project_dir}
Restart=on-failure
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=default.target
"""


class LinuxLauncher(BaseLauncher):
    def install(self, project_dir: Path, python_exec: Path) -> None:
        _SERVICE_DIR.mkdir(parents=True, exist_ok=True)
        _SERVICE_FILE.write_text(_unit_content(project_dir, python_exec))
        subprocess.run(["systemctl", "--user", "daemon-reload"], check=True)
        subprocess.run(["systemctl", "--user", "enable", "--now", _SERVICE_NAME], check=True)
        print("✓  Service installed and started. Logs: journalctl --user -u kittntabbr")

    def uninstall(self, project_dir: Path) -> None:
        if _SERVICE_FILE.exists():
            subprocess.run(["systemctl", "--user", "disable", "--now", _SERVICE_NAME], capture_output=True)
            _SERVICE_FILE.unlink()
            subprocess.run(["systemctl", "--user", "daemon-reload"], capture_output=True)
            print("✓  Service removed.")
        else:
            print("Service is not installed.")
