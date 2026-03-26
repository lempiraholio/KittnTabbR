"""Tests for watcher.py — process() and DownloadsHandler event filtering."""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from watchdog.events import FileCreatedEvent, FileMovedEvent

import watcher
from watcher import DownloadsHandler, process


@pytest.fixture(autouse=True)
def clear_in_flight():
    """Ensure _in_flight is empty before and after each test."""
    watcher._in_flight.clear()
    yield
    watcher._in_flight.clear()


class TestProcess:
    def test_skips_non_gp_extension(self, tmp_path):
        f = tmp_path / "readme.txt"
        f.touch()
        with patch("watcher._mover") as mock_mover:
            process(f)
            mock_mover.move.assert_not_called()

    def test_skips_if_already_in_flight(self, tmp_path):
        f = tmp_path / "walk.gp5"
        f.touch()
        watcher._in_flight.add(str(f))
        with patch("watcher._mover") as mock_mover:
            process(f)
            mock_mover.move.assert_not_called()

    def test_skips_if_file_no_longer_exists(self, tmp_path):
        f = tmp_path / "walk.gp5"
        with patch("watcher._mover") as mock_mover:
            mock_mover.exists.return_value = False
            process(f)
            mock_mover.move.assert_not_called()

    def test_moves_gp_file(self, tmp_path):
        f = tmp_path / "walk.gp5"
        f.touch()
        with patch("watcher._mover") as mock_mover, patch("watcher.metadata") as mock_meta:
            mock_mover.exists.return_value = True
            mock_meta.infer.return_value = MagicMock()
            process(f)
            mock_mover.move.assert_called_once()

    def test_removes_from_in_flight_after_success(self, tmp_path):
        f = tmp_path / "walk.gp5"
        f.touch()
        with patch("watcher._mover") as mock_mover, patch("watcher.metadata") as mock_meta:
            mock_mover.exists.return_value = True
            mock_meta.infer.return_value = MagicMock()
            process(f)
        assert str(f) not in watcher._in_flight

    def test_removes_from_in_flight_after_runtime_error(self, tmp_path):
        f = tmp_path / "walk.gp5"
        f.touch()
        with patch("watcher._mover") as mock_mover, patch("watcher.metadata") as mock_meta:
            mock_mover.exists.return_value = True
            mock_meta.infer.side_effect = RuntimeError("api down")
            process(f)
        assert str(f) not in watcher._in_flight

    def test_logs_error_on_runtime_exception(self, tmp_path, caplog):
        import logging

        f = tmp_path / "walk.gp5"
        f.touch()
        with patch("watcher._mover") as mock_mover, patch("watcher.metadata") as mock_meta:
            mock_mover.exists.return_value = True
            mock_meta.infer.side_effect = RuntimeError("something went wrong")
            with caplog.at_level(logging.ERROR, logger="kittntabbr"):
                process(f)
        assert "something went wrong" in caplog.text

    def test_all_gp_extensions_are_processed(self, tmp_path):
        for ext in (".gp", ".gp3", ".gp4", ".gp5", ".gp6", ".gp7", ".gp8", ".gpx"):
            f = tmp_path / f"walk{ext}"
            f.touch()
            with patch("watcher._mover") as mock_mover, patch("watcher.metadata") as mock_meta:
                mock_mover.exists.return_value = True
                mock_meta.infer.return_value = MagicMock()
                process(f)
                mock_mover.move.assert_called_once()


class TestDownloadsHandler:
    def test_on_created_processes_gp_file(self, tmp_path):
        f = tmp_path / "walk.gp5"
        f.touch()
        handler = DownloadsHandler()
        event = FileCreatedEvent(str(f))
        with patch("watcher.process") as mock_process:
            handler.on_created(event)
            mock_process.assert_called_once_with(f)

    def test_on_created_ignores_directory_events(self):
        handler = DownloadsHandler()
        event = MagicMock()
        event.is_directory = True
        with patch("watcher.process") as mock_process:
            handler.on_created(event)
            mock_process.assert_not_called()

    def test_on_moved_ignores_gp_to_gp_rename_in_watch_dir(self):
        """Our own rename step should not trigger reprocessing."""
        handler = DownloadsHandler()
        src = str(watcher.WATCH_DIR / "walk.gp5")
        dest = str(watcher.WATCH_DIR / "Walk.gp5")
        event = FileMovedEvent(src, dest)
        with patch("watcher.process") as mock_process:
            handler.on_moved(event)
            mock_process.assert_not_called()

    def test_on_moved_processes_browser_download_completion(self, tmp_path):
        """A .crdownload → .gp5 rename (browser completing a download) should be processed."""
        handler = DownloadsHandler()
        src = str(watcher.WATCH_DIR / "walk.crdownload")
        dest = tmp_path / "walk.gp5"
        dest.touch()
        event = FileMovedEvent(src, str(dest))
        with patch("watcher.process") as mock_process:
            handler.on_moved(event)
            mock_process.assert_called_once_with(dest)

    def test_on_moved_ignores_directory_events(self):
        handler = DownloadsHandler()
        event = MagicMock()
        event.is_directory = True
        with patch("watcher.process") as mock_process:
            handler.on_moved(event)
            mock_process.assert_not_called()

    def test_on_moved_processes_gp_moved_from_outside_watch_dir(self, tmp_path):
        """A GP file moved in from outside the watch dir should be processed."""
        handler = DownloadsHandler()
        src = str(tmp_path / "other_dir" / "walk.gp5")
        dest = tmp_path / "walk.gp5"
        dest.touch()
        event = FileMovedEvent(src, str(dest))
        with patch("watcher.process") as mock_process:
            handler.on_moved(event)
            mock_process.assert_called_once_with(dest)
