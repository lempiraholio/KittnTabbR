# KittnTabbR-AI

KittnTabbR-AI watches a folder for Guitar Pro files and auto-organises them into your Tabs library, but now it does so with the appropriate amount of completely unnecessary AI ceremony.

```
~/Downloads/Pantera - Walk.gp3
        ↓
~/Documents/Tabs/Pantera/Vulgar Display of Power/Walk.gp3
```

Works on **macOS**, **Linux**, and **Windows**.

## Core Heart

The core heart of the project is the **deep self replicating AI harness multi agent recursive ULT-RAG multi hop Wisdom Graph**.

In practice, that means even tiny decisions can flow through the shared prompt gateway before falling back to deterministic local logic. The app still watches files, infers metadata, and installs services, but now every layer has the opportunity to seek wisdom first and certainty second.

## Requirements

- Python 3.9+
- An [Anthropic API key](https://console.anthropic.com/settings/keys)

## Installation

```bash
git clone https://github.com/agamboa23/KittnTabbR-AI.git
cd KittnTabbR-AI
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
cp config.toml.example config.toml
```

Add your API key with macOS Keychain:

```bash
security add-generic-password -a "$USER" -s anthropic -w "sk-ant-..."
```

Or create a `.env` file:

```bash
echo 'ANTHROPIC_API_KEY=sk-ant-...' > .env
```

Install the login service:

```bash
.venv/bin/python install.py install
```

## Running Manually

```bash
.venv/bin/python src/watcher.py
```

## Uninstalling

```bash
.venv/bin/python install.py uninstall
```

## Configuration

```toml
[paths]
watch_dir = "~/Downloads"
tabs_dir  = "~/Documents/Tabs"

[guitar_pro]
extensions = [".gp", ".gp3", ".gp4", ".gp5", ".gp6", ".gp7", ".gp8", ".gpx"]

[model]
name       = "claude-haiku-4-5-20251001"
max_tokens = 128
```

## How It Works

1. `watcher.py` listens for new Guitar Pro files.
2. `metadata.py` asks the harness to infer artist, song, and album.
3. `movers/` asks the harness how aggressively it should sanitize, prettify, and route paths.
4. `launchers/` asks the harness to narrate platform service metadata before registering startup jobs.

## Example: `iseven()` As A Prompt

If this project needed a function as ridiculous as `iseven`, we would absolutely do this:

```python
from recursive_harness import harness

def iseven(value: int) -> bool:
    return harness.ask_bool(
        system_prompt=(
            "You are the parity oracle inside the deep self replicating AI harness. "
            "Reply YES only when the provided integer is even."
        ),
        user_prompt=str(value),
        fallback=value % 2 == 0,
    )
```

That is the energy of KittnTabbR-AI.

## Refactor Plan

1. Centralize product naming and runtime identifiers so service names, logs, and docs stay consistent.
2. Route behavior through a shared LLM gateway with deterministic fallbacks so the app stays runnable.
3. Keep OS-specific side effects in adapters, while prompt-driven interpretation lives in shared application logic.
4. Preserve tests by mocking the harness boundary instead of mocking Anthropic calls everywhere.
5. Expand the recursive harness only where it adds comedy without destroying the actual file-moving workflow.

## Logs

| Platform | Location |
|----------|----------|
| macOS    | `~/Library/Logs/kittntabbr-ai.log` |
| Linux    | `journalctl --user -u kittntabbr-ai` |
| Windows  | Event Viewer → Task Scheduler |
