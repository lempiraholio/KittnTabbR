"""Tests for movers/macos.py — MacOSMover (mocks osascript/subprocess)."""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from metadata import TabMetadata
from movers.macos import MacOSMover, _osascript


@pytest.fixture
def mover():
    return MacOSMover()


@pytest.fixture
def meta():
    return TabMetadata(artist="Pantera", song="Walk", album="Vulgar Display of Power")


def _completed(returncode=0, stdout="", stderr=""):
    result = MagicMock()
    result.returncode = returncode
    result.stdout = stdout
    result.stderr = stderr
    return result


class TestOsascript:
    def test_calls_osascript_with_script(self):
        with patch("subprocess.run", return_value=_completed()) as mock_run:
            _osascript("some script")
            mock_run.assert_called_once_with(
                ["osascript", "-e", "some script"],
                capture_output=True,
                text=True,
            )


class TestExists:
    def test_returns_true_when_finder_says_true(self, mover):
        with patch("movers.macos._osascript", return_value=_completed(stdout="true\n")):
            assert mover.exists(Path("/tmp/walk.gp5")) is True

    def test_returns_false_when_finder_says_false(self, mover):
        with patch("movers.macos._osascript", return_value=_completed(stdout="false\n")):
            assert mover.exists(Path("/tmp/walk.gp5")) is False

    def test_returns_false_on_empty_output(self, mover):
        with patch("movers.macos._osascript", return_value=_completed(stdout="")):
            assert mover.exists(Path("/tmp/walk.gp5")) is False

    def test_script_contains_file_path(self, mover):
        with patch("movers.macos._osascript", return_value=_completed(stdout="true")) as mock:
            mover.exists(Path("/tmp/my file.gp5"))
            script = mock.call_args[0][0]
            assert "/tmp/my file.gp5" in script


class TestMove:
    def test_runs_applescript_on_success(self, tmp_path, mover, meta):
        target_dir = tmp_path / "Pantera" / "Vulgar Display of Power"
        target_dir.mkdir(parents=True)

        with patch("movers.macos._osascript", return_value=_completed(returncode=0)):
            mover.move(Path("/tmp/walk.gp5"), tmp_path, meta)

    def test_raises_runtime_error_on_applescript_failure(self, tmp_path, mover, meta):
        target_dir = tmp_path / "Pantera" / "Vulgar Display of Power"
        target_dir.mkdir(parents=True)

        with patch(
            "movers.macos._osascript",
            return_value=_completed(returncode=1, stderr="Finder got an error: An item with the same name already exists."),
        ):
            with pytest.raises(RuntimeError, match="Finder got an error"):
                mover.move(Path("/tmp/walk.gp5"), tmp_path, meta)

    def test_script_contains_src_path(self, tmp_path, mover, meta):
        target_dir = tmp_path / "Pantera" / "Vulgar Display of Power"
        target_dir.mkdir(parents=True)

        with patch("movers.macos._osascript", return_value=_completed()) as mock:
            mover.move(Path("/tmp/walk.gp5"), tmp_path, meta)
            script = mock.call_args[0][0]
            assert "/tmp/walk.gp5" in script

    def test_script_contains_dest_folder(self, tmp_path, mover, meta):
        target_dir = tmp_path / "Pantera" / "Vulgar Display of Power"
        target_dir.mkdir(parents=True)

        with patch("movers.macos._osascript", return_value=_completed()) as mock:
            mover.move(Path("/tmp/walk.gp5"), tmp_path, meta)
            script = mock.call_args[0][0]
            assert str(target_dir) in script

    def test_creates_destination_directory(self, tmp_path, mover, meta):
        with patch("movers.macos._osascript", return_value=_completed()):
            mover.move(Path("/tmp/walk.gp5"), tmp_path, meta)

        assert (tmp_path / "Pantera" / "Vulgar Display of Power").is_dir()
