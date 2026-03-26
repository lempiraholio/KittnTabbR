#!/usr/bin/env bash
set -euo pipefail

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# 1. Already in the environment — nothing to do.
# 2. Try macOS Keychain (preferred — encrypted, never plaintext on disk).
# 3. Fall back to a local .env file.
if [[ -z "${ANTHROPIC_API_KEY:-}" ]]; then
    ANTHROPIC_API_KEY="$(security find-generic-password -a "$USER" -s "anthropic" -w 2>/dev/null || true)"
    export ANTHROPIC_API_KEY
fi

if [[ -z "${ANTHROPIC_API_KEY:-}" && -f "$DIR/.env" ]]; then
    export ANTHROPIC_API_KEY="$(grep -E '^ANTHROPIC_API_KEY=' "$DIR/.env" | cut -d= -f2-)"
fi

if [[ -z "${ANTHROPIC_API_KEY:-}" ]]; then
    echo "Error: ANTHROPIC_API_KEY not found." >&2
    echo >&2
    echo "Store it in Keychain (recommended):" >&2
    echo "  security add-generic-password -a \"\$USER\" -s anthropic -w \"sk-ant-...\"" >&2
    echo >&2
    echo "Or create a .env file:" >&2
    echo "  echo \"ANTHROPIC_API_KEY=sk-ant-...\" > $DIR/.env" >&2
    exit 1
fi

exec "$DIR/.venv/bin/python" "$DIR/watcher.py"
