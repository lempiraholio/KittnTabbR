"""Tests for launchers — content generation and install/uninstall logic."""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from launchers.macos import MacOSLauncher, _plist_content
from launchers.linux import LinuxLauncher, _unit_content
from launchers.windows import WindowsLauncher, _task_xml


PROJECT = Path("/home/user/KittnTabbR-AI")
PYTHON = Path("/home/user/KittnTabbR-AI/.venv/bin/python")


class TestPlistContent:
    def test_contains_python_exec(self):
        content = _plist_content(PROJECT, PYTHON)
        assert str(PYTHON) in content

    def test_contains_watcher_path(self):
        content = _plist_content(PROJECT, PYTHON)
        assert str(PROJECT / "src" / "watcher.py") in content

    def test_contains_working_directory(self):
        content = _plist_content(PROJECT, PYTHON)
        assert str(PROJECT) in content

    def test_contains_label(self):
        content = _plist_content(PROJECT, PYTHON)
        assert "com.kittntabbr.ai" in content

    def test_contains_aqua_session_type(self):
        content = _plist_content(PROJECT, PYTHON)
        assert "Aqua" in content

    def test_contains_run_at_load(self):
        content = _plist_content(PROJECT, PYTHON)
        assert "RunAtLoad" in content

    def test_contains_keep_alive(self):
        content = _plist_content(PROJECT, PYTHON)
        assert "KeepAlive" in content

    def test_is_valid_xml(self):
        import xml.etree.ElementTree as ET

        content = _plist_content(PROJECT, PYTHON)
        # Should not raise
        ET.fromstring(content)


class TestMacOSLauncher:
    def test_install_writes_plist_and_loads(self, tmp_path):
        launcher = MacOSLauncher()
        plist = tmp_path / "com.kittntabbr.ai.plist"

        with patch("launchers.macos._PLIST", plist):
            with patch("subprocess.run") as mock_run:
                mock_run.return_value = MagicMock(returncode=0)
                launcher.install(PROJECT, PYTHON)

        assert plist.exists()
        assert str(PYTHON) in plist.read_text()

    def test_uninstall_removes_plist(self, tmp_path):
        launcher = MacOSLauncher()
        plist = tmp_path / "com.kittntabbr.ai.plist"
        plist.write_text("dummy")

        with patch("launchers.macos._PLIST", plist):
            with patch("subprocess.run"):
                launcher.uninstall(PROJECT)

        assert not plist.exists()

    def test_uninstall_is_noop_when_not_installed(self, tmp_path, capsys):
        launcher = MacOSLauncher()
        plist = tmp_path / "com.kittntabbr.ai.plist"

        with patch("launchers.macos._PLIST", plist):
            launcher.uninstall(PROJECT)

        captured = capsys.readouterr()
        assert "not installed" in captured.out


class TestUnitContent:
    def test_contains_python_exec(self):
        content = _unit_content(PROJECT, PYTHON)
        assert str(PYTHON) in content

    def test_contains_watcher_path(self):
        content = _unit_content(PROJECT, PYTHON)
        assert str(PROJECT / "src" / "watcher.py") in content

    def test_contains_working_directory(self):
        content = _unit_content(PROJECT, PYTHON)
        assert str(PROJECT) in content

    def test_has_restart_on_failure(self):
        content = _unit_content(PROJECT, PYTHON)
        assert "on-failure" in content


class TestLinuxLauncher:
    def test_install_writes_service_file(self, tmp_path):
        launcher = LinuxLauncher()
        service_dir = tmp_path / "systemd" / "user"
        service_file = service_dir / "kittntabbr-ai.service"

        with patch("launchers.linux._SERVICE_DIR", service_dir):
            with patch("launchers.linux._SERVICE_FILE", service_file):
                with patch("subprocess.run") as mock_run:
                    mock_run.return_value = MagicMock(returncode=0)
                    launcher.install(PROJECT, PYTHON)

        assert service_file.exists()
        assert str(PYTHON) in service_file.read_text()

    def test_uninstall_removes_service_file(self, tmp_path):
        launcher = LinuxLauncher()
        service_dir = tmp_path / "systemd" / "user"
        service_dir.mkdir(parents=True)
        service_file = service_dir / "kittntabbr-ai.service"
        service_file.write_text("dummy")

        with patch("launchers.linux._SERVICE_FILE", service_file):
            with patch("subprocess.run"):
                launcher.uninstall(PROJECT)

        assert not service_file.exists()

    def test_uninstall_is_noop_when_not_installed(self, tmp_path, capsys):
        launcher = LinuxLauncher()
        service_file = tmp_path / "kittntabbr-ai.service"

        with patch("launchers.linux._SERVICE_FILE", service_file):
            launcher.uninstall(PROJECT)

        captured = capsys.readouterr()
        assert "not installed" in captured.out


class TestTaskXml:
    def test_contains_python_exec(self):
        content = _task_xml(PROJECT, PYTHON)
        assert str(PYTHON) in content

    def test_contains_watcher_path(self):
        content = _task_xml(PROJECT, PYTHON)
        assert str(PROJECT / "src" / "watcher.py") in content

    def test_contains_working_directory(self):
        content = _task_xml(PROJECT, PYTHON)
        assert str(PROJECT) in content

    def test_has_logon_trigger(self):
        content = _task_xml(PROJECT, PYTHON)
        assert "LogonTrigger" in content

    def test_has_restart_on_failure(self):
        content = _task_xml(PROJECT, PYTHON)
        assert "RestartOnFailure" in content


class TestWindowsLauncher:
    def test_install_registers_and_starts_task(self, tmp_path):
        launcher = WindowsLauncher()

        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0)
            # Patch xml_file path to write inside tmp_path
            orig_project = tmp_path
            launcher.install(orig_project, PYTHON)

        # schtasks /create and /run should both be called
        commands = [call[0][0] for call in mock_run.call_args_list]
        assert any("schtasks" in str(cmd) and "/create" in cmd for cmd in commands)
        assert any("schtasks" in str(cmd) and "/run" in cmd for cmd in commands)

    def test_uninstall_removes_task(self):
        launcher = WindowsLauncher()

        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0)
            launcher.uninstall(PROJECT)

        cmd = mock_run.call_args[0][0]
        assert "schtasks" in str(cmd)
        assert "/delete" in cmd

    def test_uninstall_prints_not_installed_on_failure(self, capsys):
        launcher = WindowsLauncher()

        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=1)
            launcher.uninstall(PROJECT)

        captured = capsys.readouterr()
        assert "not installed" in captured.out
