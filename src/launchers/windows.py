"""Windows launcher — registers a Task Scheduler task to run at login."""

import subprocess
from pathlib import Path

from launchers.base import BaseLauncher

_TASK_NAME = "KittnTabbR"


def _task_xml(project_dir: Path, python_exec: Path) -> str:
    watcher = project_dir / "src" / "watcher.py"
    return f"""<?xml version="1.0" encoding="UTF-16"?>
<Task version="1.2" xmlns="http://schemas.microsoft.com/windows/2004/02/mit/task">
  <Triggers>
    <LogonTrigger><Enabled>true</Enabled></LogonTrigger>
  </Triggers>
  <Actions Context="Author">
    <Exec>
      <Command>{python_exec}</Command>
      <Arguments>{watcher}</Arguments>
      <WorkingDirectory>{project_dir}</WorkingDirectory>
    </Exec>
  </Actions>
  <Settings>
    <ExecutionTimeLimit>PT0S</ExecutionTimeLimit>
    <RestartOnFailure>
      <Interval>PT1M</Interval>
      <Count>999</Count>
    </RestartOnFailure>
  </Settings>
</Task>
"""


class WindowsLauncher(BaseLauncher):
    def install(self, project_dir: Path, python_exec: Path) -> None:
        xml_file = project_dir / "kittntabbr_task.xml"
        xml_file.write_text(_task_xml(project_dir, python_exec), encoding="utf-16")
        subprocess.run(
            ["schtasks", "/create", "/tn", _TASK_NAME, "/xml", str(xml_file), "/f"],
            check=True,
        )
        xml_file.unlink()
        subprocess.run(["schtasks", "/run", "/tn", _TASK_NAME], check=True)
        print("✓  Task registered and started.")

    def uninstall(self, project_dir: Path) -> None:
        result = subprocess.run(
            ["schtasks", "/delete", "/tn", _TASK_NAME, "/f"],
            capture_output=True,
        )
        if result.returncode == 0:
            print("✓  Task removed.")
        else:
            print("Task is not installed.")
