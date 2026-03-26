#!/usr/bin/env python3
"""Infer Guitar Pro tab metadata from a filename using Claude Haiku."""

from dataclasses import dataclass

import anthropic

import config

_SYSTEM = (
    "You extract metadata from Guitar Pro tab filenames. "
    "The filename may be in PascalCase, snake_case, camelCase, or plain text. "
    "Use your knowledge to infer the artist, album, and song — even if not all are present in the filename. "
    "For ALBUM, always prefer the original studio album. Never use greatest hits, compilations, or live albums. "
    "If only a live or compilation album is known, use Unknown. "
    "Reply with exactly three lines:\n"
    "ARTIST: <artist name or Unknown>\n"
    "SONG: <song title or Unknown>\n"
    "ALBUM: <album name or Unknown>\n"
    "No quotes, no extra text."
)

_client = anthropic.Anthropic()


@dataclass(frozen=True)
class TabMetadata:
    artist: str
    song: str
    album: str

    @property
    def has_album(self) -> bool:
        return self.album != "Unknown"


def infer(filename_stem: str) -> TabMetadata:
    """Return artist, song, and album inferred from a Guitar Pro filename."""
    try:
        response = _client.messages.create(
            model=config.model,
            max_tokens=config.max_tokens,
            system=_SYSTEM,
            messages=[{"role": "user", "content": filename_stem}],
        )
    except anthropic.AuthenticationError:
        raise RuntimeError(
            "Invalid Anthropic API key. "
            "Store it in Keychain: security add-generic-password -a \"$USER\" -s kittntabbr -w \"sk-ant-...\""
        )
    except anthropic.RateLimitError:
        raise RuntimeError("Anthropic API rate limit reached. The file will not be processed.")
    except anthropic.APIConnectionError as exc:
        raise RuntimeError(f"Could not reach the Anthropic API — check your internet connection. ({exc})")
    except anthropic.APIStatusError as exc:
        raise RuntimeError(f"Anthropic API error {exc.status_code}: {exc.message}")

    text_block = next((b for b in response.content if hasattr(b, "text")), None)
    if text_block is None:
        raise RuntimeError(f"Unexpected response from Haiku — no text block returned.")

    fields = {"ARTIST": "Unknown", "SONG": "Unknown", "ALBUM": "Unknown"}
    for line in text_block.text.strip().splitlines():
        for key in fields:
            if line.startswith(f"{key}:"):
                value = line.removeprefix(f"{key}:").strip()
                fields[key] = value or "Unknown"
    return TabMetadata(
        artist=fields["ARTIST"],
        song=fields["SONG"],
        album=fields["ALBUM"],
    )
