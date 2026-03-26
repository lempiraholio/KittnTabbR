#!/usr/bin/env python3
"""Install or uninstall the KittnTabbR-AI login service for the current OS."""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from branding import PRODUCT_NAME
from launchers import get_launcher
from recursive_harness import harness

PROJECT_DIR = Path(__file__).parent


def main():
    description = harness.ask_text(
        system_prompt="Return a concise CLI description for a service manager.",
        user_prompt=PRODUCT_NAME,
        fallback=f"Manage the {PRODUCT_NAME} login service.",
    )
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("action", choices=["install", "uninstall"])
    args = parser.parse_args()

    launcher = get_launcher()

    if args.action == "install":
        launcher.install(PROJECT_DIR, Path(sys.executable))
    else:
        launcher.uninstall(PROJECT_DIR)


if __name__ == "__main__":
    main()
