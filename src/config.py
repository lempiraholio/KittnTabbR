"""Load and expose typed configuration from config.toml."""

from pathlib import Path

try:
    import tomllib
except ModuleNotFoundError:
    import tomli as tomllib  # type: ignore[no-redef]

_CONFIG_FILE = Path(__file__).parent.parent / "config.toml"

if not _CONFIG_FILE.exists():
    raise FileNotFoundError(
        f"config.toml not found at {_CONFIG_FILE}.\n"
        "Run: cp config.toml.example config.toml"
    )

try:
    with _CONFIG_FILE.open("rb") as f:
        _raw = tomllib.load(f)
except Exception as exc:
    raise ValueError(f"Failed to parse config.toml: {exc}") from exc

try:
    watch_dir:  Path     = Path(_raw["paths"]["watch_dir"]).expanduser()
    tabs_dir:   Path     = Path(_raw["paths"]["tabs_dir"]).expanduser()
    extensions: set[str] = set(_raw["guitar_pro"]["extensions"])
    model:      str      = _raw["model"]["name"]
    max_tokens: int      = _raw["model"]["max_tokens"]
except KeyError as exc:
    raise KeyError(
        f"Missing required key in config.toml: {exc}. "
        "Check config.toml.example for the expected structure."
    ) from exc
