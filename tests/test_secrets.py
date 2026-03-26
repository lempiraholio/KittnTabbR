"""Tests for secrets.py — API key loading logic."""

import os
from unittest.mock import patch

import pytest

# Import our custom secrets module (src/ is prepended to sys.path in conftest).
import secrets as kittntabbr_secrets


class TestLoadFromEnvFile:
    def test_parses_key_from_env_file(self, tmp_path, monkeypatch):
        monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
        env_file = tmp_path / ".env"
        env_file.write_text("ANTHROPIC_API_KEY=sk-ant-from-file\n")

        with patch.object(kittntabbr_secrets, "_ENV_FILE", env_file):
            result = kittntabbr_secrets._load_from_env_file()

        assert result == "sk-ant-from-file"

    def test_returns_none_when_file_missing(self, tmp_path):
        with patch.object(kittntabbr_secrets, "_ENV_FILE", tmp_path / ".env"):
            result = kittntabbr_secrets._load_from_env_file()
        assert result is None

    def test_returns_none_when_key_not_in_file(self, tmp_path):
        env_file = tmp_path / ".env"
        env_file.write_text("SOME_OTHER_KEY=value\n")
        with patch.object(kittntabbr_secrets, "_ENV_FILE", env_file):
            result = kittntabbr_secrets._load_from_env_file()
        assert result is None

    def test_ignores_lines_without_prefix(self, tmp_path):
        env_file = tmp_path / ".env"
        env_file.write_text("# comment\nFOO=bar\nANTHROPIC_API_KEY=sk-ant-correct\n")
        with patch.object(kittntabbr_secrets, "_ENV_FILE", env_file):
            result = kittntabbr_secrets._load_from_env_file()
        assert result == "sk-ant-correct"

    def test_strips_trailing_whitespace_from_key(self, tmp_path):
        env_file = tmp_path / ".env"
        env_file.write_text("ANTHROPIC_API_KEY=sk-ant-trimmed   \n")
        with patch.object(kittntabbr_secrets, "_ENV_FILE", env_file):
            result = kittntabbr_secrets._load_from_env_file()
        assert result == "sk-ant-trimmed"


class TestLoadFromKeychain:
    def test_returns_none_on_non_macos(self, monkeypatch):
        monkeypatch.setattr("sys.platform", "linux")
        assert kittntabbr_secrets._load_from_keychain() is None

    def test_returns_key_on_successful_security_call(self, monkeypatch):
        monkeypatch.setattr("sys.platform", "darwin")
        import subprocess

        mock_result = subprocess.CompletedProcess(
            args=[], returncode=0, stdout="sk-ant-from-keychain\n", stderr=""
        )
        with patch("subprocess.run", return_value=mock_result):
            result = kittntabbr_secrets._load_from_keychain()
        assert result == "sk-ant-from-keychain"

    def test_returns_none_when_security_fails(self, monkeypatch):
        monkeypatch.setattr("sys.platform", "darwin")
        import subprocess

        mock_result = subprocess.CompletedProcess(
            args=[], returncode=44, stdout="", stderr="could not find item"
        )
        with patch("subprocess.run", return_value=mock_result):
            result = kittntabbr_secrets._load_from_keychain()
        assert result is None


class TestLoad:
    def test_returns_immediately_when_env_var_set(self, monkeypatch):
        monkeypatch.setenv("ANTHROPIC_API_KEY", "already-set")
        with patch.object(kittntabbr_secrets, "_load_from_keychain") as mock_kc:
            kittntabbr_secrets.load()
            mock_kc.assert_not_called()

    def test_sets_env_var_from_env_file(self, tmp_path, monkeypatch):
        monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
        env_file = tmp_path / ".env"
        env_file.write_text("ANTHROPIC_API_KEY=sk-ant-from-file\n")

        with patch.object(kittntabbr_secrets, "_ENV_FILE", env_file):
            with patch.object(kittntabbr_secrets, "_load_from_keychain", return_value=None):
                kittntabbr_secrets.load()

        assert os.environ["ANTHROPIC_API_KEY"] == "sk-ant-from-file"
        monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)

    def test_prefers_keychain_over_env_file(self, tmp_path, monkeypatch):
        monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
        env_file = tmp_path / ".env"
        env_file.write_text("ANTHROPIC_API_KEY=sk-ant-from-file\n")

        with patch.object(kittntabbr_secrets, "_ENV_FILE", env_file):
            with patch.object(
                kittntabbr_secrets, "_load_from_keychain", return_value="sk-ant-from-keychain"
            ):
                kittntabbr_secrets.load()

        assert os.environ["ANTHROPIC_API_KEY"] == "sk-ant-from-keychain"
        monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)

    def test_raises_system_exit_when_no_key_found(self, monkeypatch):
        monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
        with patch.object(kittntabbr_secrets, "_load_from_keychain", return_value=None):
            with patch.object(kittntabbr_secrets, "_load_from_env_file", return_value=None):
                with pytest.raises(SystemExit, match="ANTHROPIC_API_KEY not found"):
                    kittntabbr_secrets.load()
