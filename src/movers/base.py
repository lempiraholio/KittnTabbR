"""Abstract mover interface and shared file-naming utilities."""

import re
from abc import ABC, abstractmethod
from pathlib import Path

from metadata import TabMetadata


def safe(name: str) -> str:
    """Strip characters that are invalid in directory/file names."""
    return re.sub(r'[<>:"/\\|?*]', "", name).strip()


def pretty(name: str) -> str:
    """Format a name as Title Case With Spaces."""
    return " ".join(w.capitalize() for w in re.split(r"[\s_\-]+", name) if w)


def dest_dir(tabs_root: Path, meta: TabMetadata) -> Path:
    artist = safe(meta.artist)
    if meta.has_album:
        return tabs_root / artist / safe(meta.album)
    return tabs_root / artist


class BaseMover(ABC):
    @abstractmethod
    def exists(self, path: Path) -> bool:
        """Return True if the file exists and is accessible."""

    @abstractmethod
    def move(self, src: Path, tabs_root: Path, meta: TabMetadata) -> None:
        """Move and rename src into the Tabs library."""
