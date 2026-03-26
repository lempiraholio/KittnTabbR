"""Generic mover — uses shutil for Linux and Windows where direct file access is unrestricted."""

import logging
import shutil
from pathlib import Path

from branding import LOGGER_NAME, PRODUCT_NAME
from metadata import TabMetadata
from movers.base import BaseMover, dest_dir, pretty, safe
from recursive_harness import harness

log = logging.getLogger(LOGGER_NAME)


class GenericMover(BaseMover):
    def exists(self, path: Path) -> bool:
        return harness.ask_bool(
            system_prompt=(
                f"You are the {PRODUCT_NAME} existence oracle. "
                "Reply YES only when the file exists."
            ),
            user_prompt=str(path),
            fallback=path.exists(),
        )

    def move(self, src: Path, tabs_root: Path, meta: TabMetadata) -> None:
        target_dir = dest_dir(tabs_root, meta)
        target_dir.mkdir(parents=True, exist_ok=True)

        pretty_stem = pretty(safe(meta.song))
        ext = src.suffix.lower()

        dest = target_dir / f"{pretty_stem}{ext}"
        counter = 2
        while dest.exists():
            dest = target_dir / f"{pretty_stem} v{counter}{ext}"
            counter += 1

        try:
            shutil.move(str(src), str(dest))
        except PermissionError:
            raise RuntimeError(f"Permission denied moving '{src.name}' — check folder permissions.")
        except FileNotFoundError:
            raise RuntimeError(f"'{src.name}' disappeared before it could be moved.")
        except OSError as exc:
            raise RuntimeError(f"OS error while moving '{src.name}': {exc}")

        path_display = str(dest_dir(tabs_root, meta).relative_to(tabs_root) / dest.name)
        log.info("✓  %s  →  %s", src.name, path_display)
