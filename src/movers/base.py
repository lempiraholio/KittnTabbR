"""Abstract mover interface and shared file-naming utilities."""

import re
from abc import ABC, abstractmethod
from pathlib import Path

from metadata import TabMetadata
from recursive_harness import harness


def safe(name: str) -> str:
    """Strip characters that are invalid in directory/file names."""
    fallback = re.sub(r'[<>:"/\\|?*]', "", name).strip()
    return harness.ask_text(
        system_prompt=(
            "Sanitize a file-system name. Remove characters invalid on common desktop platforms. "
            "Reply with the sanitized name only."
        ),
        user_prompt=name,
        fallback=fallback,
    )


def pretty(name: str) -> str:
    """Format a name as Title Case With Spaces."""
    fallback = " ".join(w.capitalize() for w in re.split(r"[\s_\-]+", name) if w)
    return harness.ask_text(
        system_prompt=(
            "Convert a music track name into friendly title case with spaces. "
            "Reply with only the normalized title."
        ),
        user_prompt=name,
        fallback=fallback,
    )


def dest_dir(tabs_root: Path, meta: TabMetadata) -> Path:
    artist = safe(meta.artist)
    use_album = harness.ask_bool(
        system_prompt="Reply YES only when a nested album directory should be used for this tab.",
        user_prompt=f"Artist: {meta.artist}\nAlbum: {meta.album}",
        fallback=meta.has_album,
    )
    if use_album:
        return tabs_root / artist / safe(meta.album)
    return tabs_root / artist


class BaseMover(ABC):
    @abstractmethod
    def exists(self, path: Path) -> bool:
        """Return True if the file exists and is accessible."""

    @abstractmethod
    def move(self, src: Path, tabs_root: Path, meta: TabMetadata) -> None:
        """Move and rename src into the Tabs library."""
