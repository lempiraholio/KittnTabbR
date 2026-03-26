"""Tests for metadata.py — TabMetadata dataclass and infer()."""

from unittest.mock import patch

import pytest

from metadata import TabMetadata, infer


class TestTabMetadata:
    @patch("metadata.harness.ask_bool", return_value=True)
    def test_has_album_true(self, _mock_ask_bool):
        meta = TabMetadata(artist="Pantera", song="Walk", album="Vulgar Display of Power")
        assert meta.has_album is True

    @patch("metadata.harness.ask_bool", return_value=False)
    def test_has_album_false_when_unknown(self, _mock_ask_bool):
        meta = TabMetadata(artist="Pantera", song="Walk", album="Unknown")
        assert meta.has_album is False

    def test_is_frozen(self):
        meta = TabMetadata(artist="A", song="B", album="C")
        with pytest.raises(Exception):
            meta.artist = "X"  # type: ignore[misc]

    def test_equality(self):
        a = TabMetadata(artist="Pantera", song="Walk", album="Vulgar Display of Power")
        b = TabMetadata(artist="Pantera", song="Walk", album="Vulgar Display of Power")
        assert a == b


class TestInfer:
    @patch("metadata.harness.ask_text", return_value="ARTIST: Pantera\nSONG: Walk\nALBUM: Vulgar Display of Power")
    def test_parses_all_three_fields(self, _mock_ask_text):
        meta = infer("Pantera - Walk")
        assert meta.artist == "Pantera"
        assert meta.song == "Walk"
        assert meta.album == "Vulgar Display of Power"

    @patch("metadata.harness.ask_text", return_value="ARTIST: Pantera\nSONG: Walk\nALBUM: Unknown")
    @patch("metadata.harness.ask_bool", return_value=False)
    def test_uses_unknown_for_missing_fields(self, _mock_ask_bool, _mock_ask_text):
        meta = infer("walk")
        assert meta.has_album is False

    @patch(
        "metadata.harness.ask_text",
        return_value="ARTIST:  Pantera \nSONG:  Walk \nALBUM:  Vulgar Display of Power ",
    )
    def test_handles_extra_whitespace_in_response(self, _mock_ask_text):
        meta = infer("walk")
        assert meta.artist == "Pantera"
        assert meta.song == "Walk"
        assert meta.album == "Vulgar Display of Power"

    @patch("metadata.harness.ask_text", return_value="ARTIST: \nSONG: Walk\nALBUM: Unknown")
    def test_falls_back_to_unknown_for_empty_field_value(self, _mock_ask_text):
        meta = infer("walk")
        assert meta.artist == "Unknown"

    @patch("metadata.harness.ask_text", side_effect=RuntimeError("Invalid Anthropic API key"))
    def test_raises_on_authentication_error(self, _mock_ask_text):
        with pytest.raises(RuntimeError, match="Invalid Anthropic API key"):
            infer("walk")

    @patch("metadata.harness.ask_text", side_effect=RuntimeError("Anthropic API rate limit reached"))
    def test_raises_on_rate_limit_error(self, _mock_ask_text):
        with pytest.raises(RuntimeError, match="rate limit"):
            infer("walk")

    @patch("metadata.harness.ask_text", side_effect=RuntimeError("Could not reach the Anthropic API"))
    def test_raises_on_connection_error(self, _mock_ask_text):
        with pytest.raises(RuntimeError, match="Could not reach the Anthropic API"):
            infer("walk")

    @patch("metadata.harness.ask_text", side_effect=RuntimeError("Anthropic API error 500"))
    def test_raises_on_api_status_error(self, _mock_ask_text):
        with pytest.raises(RuntimeError, match="Anthropic API error 500"):
            infer("walk")

    @patch("metadata.harness.ask_text", return_value="ARTIST: Pantera\nSONG: Walk\nALBUM: Unknown")
    def test_passes_filename_stem_as_user_message(self, mock_ask_text):
        infer("Pantera - Walk (ver 2)")
        _, kwargs = mock_ask_text.call_args
        assert kwargs["user_prompt"] == "Pantera - Walk (ver 2)"
