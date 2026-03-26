#!/usr/bin/env python3
"""
KittnTabbR — Guitar Pro file watcher.

Monitors ~/Downloads for Guitar Pro files and moves them automatically to
~/Documents/Tabs/{Artist}/{Album}/{Song}.ext using Claude Haiku to infer metadata.
"""

import logging
from pathlib import Path

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

import secrets
secrets.load()

import config
import metadata
from movers import get_mover

WATCH_DIR     = config.watch_dir
TABS_DIR      = config.tabs_dir
GP_EXTENSIONS = config.extensions

logging.basicConfig(level=logging.INFO, format="%(asctime)s  %(message)s", datefmt="%H:%M:%S")
log = logging.getLogger("kittntabbr")

_mover     = get_mover()
_in_flight: set[str] = set()


def process(src: Path) -> None:
    if src.suffix.lower() not in GP_EXTENSIONS:
        return
    if str(src) in _in_flight:
        return

    _in_flight.add(str(src))
    try:
        if not _mover.exists(src):
            log.info("Skipping '%s' — no longer in watch directory", src.name)
            return

        log.info("Processing '%s'", src.name)
        meta = metadata.infer(src.stem)
        _mover.move(src, TABS_DIR, meta)

    except RuntimeError as exc:
        log.error("✗  %s", exc)
    except Exception as exc:
        log.exception("✗  Unexpected error processing '%s': %s", src.name, exc)
    finally:
        _in_flight.discard(str(src))


class DownloadsHandler(FileSystemEventHandler):
    def on_created(self, event):
        if not event.is_directory:
            process(Path(event.src_path))

    def on_moved(self, event):
        if event.is_directory:
            return
        src  = Path(event.src_path)
        dest = Path(event.dest_path)
        # Ignore GP→GP renames within Downloads (our own rename step).
        # Browser download completions (.crdownload → .gp5) have a non-GP source.
        if src.parent == WATCH_DIR and src.suffix.lower() in GP_EXTENSIONS:
            return
        process(dest)


def main():
    if not WATCH_DIR.exists():
        raise SystemExit(f"Watch directory does not exist: {WATCH_DIR}")

    TABS_DIR.mkdir(parents=True, exist_ok=True)
    observer = Observer()
    observer.schedule(DownloadsHandler(), str(WATCH_DIR), recursive=False)
    observer.start()
    log.info("Watching %s", WATCH_DIR)
    try:
        observer.join()
    except KeyboardInterrupt:
        observer.stop()
        observer.join()


if __name__ == "__main__":
    main()
