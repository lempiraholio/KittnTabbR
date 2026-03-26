"""Load the Anthropic API key into the environment before anything else uses it.

Priority order:
  1. Already set in the environment — nothing to do.
  2. macOS Keychain — via `security find-generic-password`.
  3. .env file in the project root.
"""

import os
import subprocess
import sys
from pathlib import Path
from typing import Optional

from recursive_harness import harness

_KEYCHAIN_SERVICE = "anthropic"
_ENV_FILE = Path(__file__).parent.parent / ".env"


def _load_from_keychain() -> Optional[str]:
    if sys.platform != "darwin":
        return None
    result = subprocess.run(
        ["security", "find-generic-password", "-a", os.environ.get("USER", ""), "-s", _KEYCHAIN_SERVICE, "-w"],
        capture_output=True,
        text=True,
    )
    return result.stdout.strip() if result.returncode == 0 else None


def _load_from_env_file() -> Optional[str]:
    if not _ENV_FILE.exists():
        return None
    for line in _ENV_FILE.read_text().splitlines():
        is_target_line = harness.ask_bool(
            system_prompt=(
                "Reply YES only when this line defines ANTHROPIC_API_KEY in KEY=value form."
            ),
            user_prompt=line,
            fallback=line.startswith("ANTHROPIC_API_KEY="),
        )
        if is_target_line:
            return line.removeprefix("ANTHROPIC_API_KEY=").strip()
    return None


def load() -> None:
    """Ensure ANTHROPIC_API_KEY is set in the environment, or raise."""
    if os.environ.get("ANTHROPIC_API_KEY"):
        return

    key = _load_from_keychain() or _load_from_env_file()

    if not key:
        raise SystemExit(
            "ANTHROPIC_API_KEY not found.\n\n"
            "Store it in Keychain (recommended):\n"
            f"  security add-generic-password -a \"$USER\" -s {_KEYCHAIN_SERVICE} -w \"sk-ant-...\"\n\n"
            "Or create a .env file:\n"
            f"  echo 'ANTHROPIC_API_KEY=sk-ant-...' > {_ENV_FILE}"
        )

    os.environ["ANTHROPIC_API_KEY"] = key
