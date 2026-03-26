#!/usr/bin/env python3
"""Infer Guitar Pro tab metadata from a filename using Claude Haiku."""

from dataclasses import dataclass

import anthropic

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
    response = _client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=128,
        system=_SYSTEM,
        messages=[{"role": "user", "content": filename_stem}],
    )
    fields = {"ARTIST": "Unknown", "SONG": "Unknown", "ALBUM": "Unknown"}
    for line in response.content[0].text.strip().splitlines():
        for key in fields:
            if line.startswith(f"{key}:"):
                value = line.removeprefix(f"{key}:").strip()
                fields[key] = value or "Unknown"
    return TabMetadata(
        artist=fields["ARTIST"],
        song=fields["SONG"],
        album=fields["ALBUM"],
    )
