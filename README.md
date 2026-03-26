# KittnTabbR

Watches a folder for Guitar Pro files and automatically organises them into your Tabs library — sorted by artist and album — using Claude Haiku to infer metadata from the filename.

```
~/Downloads/Pantera - Walk.gp3
        ↓
~/Documents/Tabs/Pantera/Vulgar Display of Power/Walk.gp3
```

Works on **macOS**, **Linux**, and **Windows**.

---

## Requirements

- Python 3.9+
- An [Anthropic API key](https://console.anthropic.com/settings/keys)

---

## Installation

**1. Clone and create a virtual environment**

```bash
git clone https://github.com/lempiraholio/KittnTabbR.git
cd KittnTabbR
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
```

**2. Configure**

```bash
cp config.toml.example config.toml
# edit config.toml to set your watch and tabs directories
```

**3. Add your API key**

macOS Keychain (recommended):
```bash
security add-generic-password -a "$USER" -s anthropic -w "sk-ant-..."
```

Or create a `.env` file:
```
ANTHROPIC_API_KEY=sk-ant-...
```

**4. Install the login service**

```bash
.venv/bin/python install.py install
```

This generates and registers the appropriate service for your OS (launchd on macOS, systemd on Linux, Task Scheduler on Windows). The watcher starts immediately and runs automatically at every login.

---

## Running manually

```bash
.venv/bin/python src/watcher.py
```

---

## Uninstalling the service

```bash
.venv/bin/python install.py uninstall
```

---

## Configuration

Edit `config.toml` to customise behaviour:

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

---

## How it works

1. **Watchdog** monitors the watch directory for new Guitar Pro files using native OS events (FSEvents / inotify / ReadDirectoryChangesW) — no polling.
2. **Claude Haiku** infers the artist, album, and song name from the filename using its training knowledge.
3. The file is moved to `{tabs_dir}/{Artist}/{Album}/{Song}.ext`. If the album can't be determined, it falls under `{Artist}/` directly. Duplicate filenames are versioned automatically (`Song v2.gp5`, etc.).

### macOS note

macOS TCC restrictions block direct Python file operations on `~/Downloads` and `~/Documents`. KittnTabbR works around this by delegating all file moves to Finder via AppleScript, which already has the necessary permissions.

---

## Logs

| Platform | Location |
|----------|----------|
| macOS    | `~/Library/Logs/kittntabbr.log` |
| Linux    | `journalctl --user -u kittntabbr` |
| Windows  | Event Viewer → Task Scheduler |
