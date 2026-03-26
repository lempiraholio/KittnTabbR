# KittnTabbR-AI

Watches `~/Downloads` for Guitar Pro files and moves them automatically to `~/Documents/Tabs/{Artist}/{Album}/{Song}.ext` using Claude Haiku to infer metadata from the filename.

## Architecture

```
src/
├── watcher.py          Entry point, watchdog Observer, event handler
├── metadata.py         Claude Haiku inference → TabMetadata dataclass
├── config.py           Loads config.toml and exposes typed values
├── secrets.py          Loads ANTHROPIC_API_KEY from Keychain or .env
├── movers/
│   ├── __init__.py     OS factory → get_mover()
│   ├── base.py         Abstract interface + shared naming utilities
│   ├── macos.py        Finder/AppleScript (bypasses TCC)
│   └── generic.py      shutil (Linux / Windows)
└── launchers/
    ├── __init__.py     OS factory → get_launcher()
    ├── base.py         Abstract interface
    ├── macos.py        Generates and installs launchd plist
    ├── linux.py        Generates and installs systemd user service
    └── windows.py      Generates and registers Task Scheduler task
```

## Setup

```bash
cp config.toml.example config.toml
# edit config.toml to your preferences
security add-generic-password -a "$USER" -s anthropic -w "sk-ant-..."
.venv/bin/python install.py install
```

## Service management

```bash
.venv/bin/python install.py install    # install and start
.venv/bin/python install.py uninstall  # stop and remove
launchctl list | grep kittntabbr-ai       # check status (macOS)
tail -f ~/Library/Logs/kittntabbr-ai.log  # logs (macOS)
```

## Running manually

```bash
.venv/bin/python src/watcher.py
```

## API Key

Loaded automatically at startup from (in order of priority):
1. `ANTHROPIC_API_KEY` environment variable
2. macOS Keychain — service name `anthropic`
3. `.env` file in the project root

Store in Keychain:
```bash
security add-generic-password -a "$USER" -s anthropic -w "sk-ant-..."
```

## macOS Permissions

File operations go through Finder via AppleScript to bypass TCC. The launchd agent uses `LimitLoadToSessionType = Aqua` to run in the user's GUI session.
