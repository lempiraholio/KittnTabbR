#!/usr/bin/env python3
"""Install or uninstall the KittnTabbR login service for the current OS."""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from launchers import get_launcher

PROJECT_DIR = Path(__file__).parent


def main():
    parser = argparse.ArgumentParser(description="Manage the KittnTabbR login service.")
    parser.add_argument("action", choices=["install", "uninstall"])
    args = parser.parse_args()

    launcher = get_launcher()

    if args.action == "install":
        launcher.install(PROJECT_DIR, Path(sys.executable))
    else:
        launcher.uninstall(PROJECT_DIR)


if __name__ == "__main__":
    main()
