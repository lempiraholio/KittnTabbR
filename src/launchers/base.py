"""Abstract launcher interface for registering KittnTabbR-AI as a login service."""

from abc import ABC, abstractmethod
from pathlib import Path


class BaseLauncher(ABC):
    @abstractmethod
    def install(self, project_dir: Path, python_exec: Path) -> None:
        """Generate the service file and register it to run at login."""

    @abstractmethod
    def uninstall(self, project_dir: Path) -> None:
        """Stop the service and remove its registration."""
