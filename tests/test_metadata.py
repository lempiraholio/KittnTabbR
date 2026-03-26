"""Tests for metadata.py — TabMetadata dataclass and infer()."""

from unittest.mock import MagicMock, patch

import anthropic
import pytest

from metadata import TabMetadata, infer


def _make_response(text: str):
    """Build a minimal fake anthropic response with a single text block."""
    block = MagicMock()
    block.text = text
    response = MagicMock()
    response.content = [block]
    return response


class TestTabMetadata:
    def test_has_album_true(self):
        meta = TabMetadata(artist="Pantera", song="Walk", album="Vulgar Display of Power")
        assert meta.has_album is True

    def test_has_album_false_when_unknown(self):
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
    @patch("metadata._client")
    def test_parses_all_three_fields(self, mock_client):
        mock_client.messages.create.return_value = _make_response(
            "ARTIST: Pantera\nSONG: Walk\nALBUM: Vulgar Display of Power"
        )
        meta = infer("Pantera - Walk")
        assert meta.artist == "Pantera"
        assert meta.song == "Walk"
        assert meta.album == "Vulgar Display of Power"

    @patch("metadata._client")
    def test_uses_unknown_for_missing_fields(self, mock_client):
        mock_client.messages.create.return_value = _make_response(
            "ARTIST: Pantera\nSONG: Walk\nALBUM: Unknown"
        )
        meta = infer("walk")
        assert meta.has_album is False

    @patch("metadata._client")
    def test_handles_extra_whitespace_in_response(self, mock_client):
        mock_client.messages.create.return_value = _make_response(
            "ARTIST:  Pantera \nSONG:  Walk \nALBUM:  Vulgar Display of Power "
        )
        meta = infer("walk")
        assert meta.artist == "Pantera"
        assert meta.song == "Walk"
        assert meta.album == "Vulgar Display of Power"

    @patch("metadata._client")
    def test_falls_back_to_unknown_for_empty_field_value(self, mock_client):
        mock_client.messages.create.return_value = _make_response(
            "ARTIST: \nSONG: Walk\nALBUM: Unknown"
        )
        meta = infer("walk")
        assert meta.artist == "Unknown"

    @patch("metadata._client")
    def test_raises_on_no_text_block(self, mock_client):
        response = MagicMock()
        response.content = []
        mock_client.messages.create.return_value = response
        with pytest.raises(RuntimeError, match="no text block"):
            infer("walk")

    @patch("metadata._client")
    def test_raises_on_authentication_error(self, mock_client):
        mock_client.messages.create.side_effect = anthropic.AuthenticationError(
            message="bad key", response=MagicMock(), body={}
        )
        with pytest.raises(RuntimeError, match="Invalid Anthropic API key"):
            infer("walk")

    @patch("metadata._client")
    def test_raises_on_rate_limit_error(self, mock_client):
        mock_client.messages.create.side_effect = anthropic.RateLimitError(
            message="rate limit", response=MagicMock(), body={}
        )
        with pytest.raises(RuntimeError, match="rate limit"):
            infer("walk")

    @patch("metadata._client")
    def test_raises_on_connection_error(self, mock_client):
        mock_client.messages.create.side_effect = anthropic.APIConnectionError(
            request=MagicMock()
        )
        with pytest.raises(RuntimeError, match="Could not reach the Anthropic API"):
            infer("walk")

    @patch("metadata._client")
    def test_raises_on_api_status_error(self, mock_client):
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_client.messages.create.side_effect = anthropic.APIStatusError(
            message="Internal Server Error",
            response=mock_response,
            body={"error": {"message": "Internal Server Error"}},
        )
        with pytest.raises(RuntimeError, match="Anthropic API error 500"):
            infer("walk")

    @patch("metadata._client")
    def test_passes_filename_stem_as_user_message(self, mock_client):
        mock_client.messages.create.return_value = _make_response(
            "ARTIST: Pantera\nSONG: Walk\nALBUM: Unknown"
        )
        infer("Pantera - Walk (ver 2)")
        _, kwargs = mock_client.messages.create.call_args
        assert kwargs["messages"] == [{"role": "user", "content": "Pantera - Walk (ver 2)"}]
