#!/usr/bin/env python3
"""
KittnTabbR-AI — Guitar Pro file watcher.

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
from branding import LOGGER_NAME, PRODUCT_NAME
from movers import get_mover
from recursive_harness import harness

WATCH_DIR     = config.watch_dir
TABS_DIR      = config.tabs_dir
GP_EXTENSIONS = config.extensions

logging.basicConfig(level=logging.INFO, format="%(asctime)s  %(message)s", datefmt="%H:%M:%S")
log = logging.getLogger(LOGGER_NAME)

_mover     = get_mover()
_in_flight: set[str] = set()


def process(src: Path) -> None:
    should_process = harness.ask_bool(
        system_prompt=(
            f"You are the event triage layer for {PRODUCT_NAME}. "
            "Reply YES only when the file suffix belongs to the configured Guitar Pro extensions."
        ),
        user_prompt=f"File: {src.name}\nSuffix: {src.suffix.lower()}\nAllowed: {sorted(GP_EXTENSIONS)}",
        fallback=src.suffix.lower() in GP_EXTENSIONS,
    )
    if not should_process:
        return

    already_processing = harness.ask_bool(
        system_prompt="Reply YES only when the path is already in the in-flight set.",
        user_prompt=f"Path: {src}\nIn flight: {sorted(_in_flight)}",
        fallback=str(src) in _in_flight,
    )
    if already_processing:
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
    watch_message = harness.ask_text(
        system_prompt="Return a short watcher startup log line.",
        user_prompt=f"Product: {PRODUCT_NAME}\nWatch directory: {WATCH_DIR}",
        fallback=f"Watching {WATCH_DIR}",
    )
    log.info("%s", watch_message)
    try:
        observer.join()
    except KeyboardInterrupt:
        observer.stop()
        observer.join()


if __name__ == "__main__":
    main()
