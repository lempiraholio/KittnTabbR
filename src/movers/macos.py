"""macOS mover — delegates file operations to Finder via AppleScript to bypass TCC."""

import logging
import subprocess
from pathlib import Path

from metadata import TabMetadata
from movers.base import BaseMover, dest_dir, pretty, safe

log = logging.getLogger("kittntabbr")


def _osascript(script: str) -> subprocess.CompletedProcess:
    return subprocess.run(["osascript", "-e", script], capture_output=True, text=True)


class MacOSMover(BaseMover):
    def exists(self, path: Path) -> bool:
        result = _osascript(
            f'tell application "Finder" to return (exists POSIX file "{path}")'
        )
        return result.stdout.strip() == "true"

    def move(self, src: Path, tabs_root: Path, meta: TabMetadata) -> None:
        target_dir = dest_dir(tabs_root, meta)
        target_dir.mkdir(parents=True, exist_ok=True)

        pretty_stem = pretty(safe(meta.song))
        ext = src.suffix.lower()

        script = f"""
tell application "Finder"
    try
        set srcFile to (POSIX file "{src}") as alias
    on error
        return
    end try
    set destFolder to (POSIX file "{target_dir}") as alias
    set baseName to "{pretty_stem}"
    set ext to "{ext}"
    set finalName to baseName & ext
    set counter to 2
    repeat while exists item finalName of destFolder
        set finalName to baseName & " v" & counter & ext
        set counter to counter + 1
    end repeat
    set srcContainer to container of srcFile
    set name of srcFile to finalName
    move item finalName of srcContainer to destFolder
end tell
"""
        result = _osascript(script)
        if result.returncode != 0:
            raise RuntimeError(result.stderr.strip())

        path_display = str(dest_dir(tabs_root, meta).relative_to(tabs_root) / f"{pretty_stem}{ext}")
        log.info("✓  %s  →  %s", src.name, path_display)
