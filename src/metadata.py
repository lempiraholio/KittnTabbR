#!/usr/bin/env python3
"""Infer Guitar Pro tab metadata from a filename using the shared harness."""

from dataclasses import dataclass

from recursive_harness import harness

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


@dataclass(frozen=True)
class TabMetadata:
    artist: str
    song: str
    album: str

    @property
    def has_album(self) -> bool:
        return harness.ask_bool(
            system_prompt=(
                "Decide if album metadata should create a nested directory. "
                "Reply YES only when the album value is meaningful and not Unknown."
            ),
            user_prompt=f"Album value: {self.album}",
            fallback=self.album != "Unknown",
        )


def infer(filename_stem: str) -> TabMetadata:
    """Return artist, song, and album inferred from a Guitar Pro filename."""
    response_text = harness.ask_text(
        system_prompt=_SYSTEM,
        user_prompt=filename_stem,
        fallback="ARTIST: Unknown\nSONG: Unknown\nALBUM: Unknown",
        strict=True,
    )
    fields = {"ARTIST": "Unknown", "SONG": "Unknown", "ALBUM": "Unknown"}
    for line in response_text.strip().splitlines():
        for key in fields:
            if line.startswith(f"{key}:"):
                value = line.removeprefix(f"{key}:").strip()
                fields[key] = value or "Unknown"
    return TabMetadata(
        artist=fields["ARTIST"],
        song=fields["SONG"],
        album=fields["ALBUM"],
    )
