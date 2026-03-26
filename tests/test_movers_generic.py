"""Tests for movers/generic.py — GenericMover."""

from pathlib import Path
from unittest.mock import patch

import pytest

from metadata import TabMetadata
from movers.generic import GenericMover


@pytest.fixture
def mover():
    return GenericMover()


@pytest.fixture
def meta():
    return TabMetadata(artist="Pantera", song="Walk", album="Vulgar Display of Power")


@pytest.fixture
def meta_no_album():
    return TabMetadata(artist="Pantera", song="Walk", album="Unknown")


class TestExists:
    def test_returns_true_for_existing_file(self, tmp_path, mover):
        f = tmp_path / "test.gp5"
        f.touch()
        assert mover.exists(f) is True

    def test_returns_false_for_missing_file(self, tmp_path, mover):
        assert mover.exists(tmp_path / "missing.gp5") is False


class TestMove:
    def test_moves_file_to_correct_location(self, tmp_path, mover, meta):
        src = tmp_path / "pantera_walk.gp5"
        src.touch()
        tabs = tmp_path / "Tabs"

        mover.move(src, tabs, meta)

        expected = tabs / "Pantera" / "Vulgar Display of Power" / "Walk.gp5"
        assert expected.exists()
        assert not src.exists()

    def test_creates_destination_directory(self, tmp_path, mover, meta):
        src = tmp_path / "walk.gp5"
        src.touch()
        tabs = tmp_path / "Tabs"
        assert not tabs.exists()

        mover.move(src, tabs, meta)

        assert (tabs / "Pantera" / "Vulgar Display of Power").is_dir()

    def test_moves_file_without_album(self, tmp_path, mover, meta_no_album):
        src = tmp_path / "walk.gp3"
        src.touch()
        tabs = tmp_path / "Tabs"

        mover.move(src, tabs, meta_no_album)

        expected = tabs / "Pantera" / "Walk.gp3"
        assert expected.exists()

    def test_preserves_extension(self, tmp_path, mover, meta):
        for ext in (".gp3", ".gp4", ".gp5", ".gpx"):
            src = tmp_path / f"walk{ext}"
            src.touch()
            tabs = tmp_path / f"Tabs{ext}"
            mover.move(src, tabs, meta)
            assert (tabs / "Pantera" / "Vulgar Display of Power" / f"Walk{ext}").exists()

    def test_versions_duplicate_filenames(self, tmp_path, mover, meta):
        src1 = tmp_path / "walk1.gp5"
        src2 = tmp_path / "walk2.gp5"
        src1.touch()
        src2.touch()
        tabs = tmp_path / "Tabs"

        mover.move(src1, tabs, meta)
        mover.move(src2, tabs, meta)

        album_dir = tabs / "Pantera" / "Vulgar Display of Power"
        assert (album_dir / "Walk.gp5").exists()
        assert (album_dir / "Walk v2.gp5").exists()

    def test_versions_triple_duplicates(self, tmp_path, mover, meta):
        srcs = [tmp_path / f"walk{i}.gp5" for i in range(3)]
        for s in srcs:
            s.touch()
        tabs = tmp_path / "Tabs"

        for s in srcs:
            mover.move(s, tabs, meta)

        album_dir = tabs / "Pantera" / "Vulgar Display of Power"
        assert (album_dir / "Walk.gp5").exists()
        assert (album_dir / "Walk v2.gp5").exists()
        assert (album_dir / "Walk v3.gp5").exists()

    def test_song_name_converted_to_title_case(self, tmp_path, mover):
        src = tmp_path / "walk_this_way.gp5"
        src.touch()
        meta = TabMetadata(artist="Aerosmith", song="walk_this_way", album="Rocks")
        tabs = tmp_path / "Tabs"

        mover.move(src, tabs, meta)

        assert (tabs / "Aerosmith" / "Rocks" / "Walk This Way.gp5").exists()

    def test_raises_runtime_error_on_permission_denied(self, tmp_path, mover, meta):
        src = tmp_path / "walk.gp5"
        src.touch()
        tabs = tmp_path / "Tabs"

        with patch("shutil.move", side_effect=PermissionError):
            with pytest.raises(RuntimeError, match="Permission denied"):
                mover.move(src, tabs, meta)

    def test_raises_runtime_error_on_file_not_found(self, tmp_path, mover, meta):
        src = tmp_path / "walk.gp5"
        src.touch()
        tabs = tmp_path / "Tabs"

        with patch("shutil.move", side_effect=FileNotFoundError):
            with pytest.raises(RuntimeError, match="disappeared"):
                mover.move(src, tabs, meta)

    def test_raises_runtime_error_on_os_error(self, tmp_path, mover, meta):
        src = tmp_path / "walk.gp5"
        src.touch()
        tabs = tmp_path / "Tabs"

        with patch("shutil.move", side_effect=OSError("disk full")):
            with pytest.raises(RuntimeError, match="OS error"):
                mover.move(src, tabs, meta)
