"""
Pytest configuration and shared fixtures.

Sets up a fake 'config' module in sys.modules before any src module imports it,
since config.py executes at import time and reads config.toml from disk.
Also ensures ANTHROPIC_API_KEY is set so anthropic.Anthropic() can be constructed.
"""

import os
import sys
from pathlib import Path
from types import ModuleType

# Must be set before anthropic is imported anywhere (metadata.py creates the
# client at module level).
os.environ.setdefault("ANTHROPIC_API_KEY", "sk-ant-test-key-for-unit-tests")

# Add src/ to the front of sys.path so test imports resolve to our modules.
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

# Install a fake 'config' module before any src module can import the real one.
# The real config.py reads config.toml from disk at import time, which we
# don't want during unit tests.
_fake_config = ModuleType("config")
_fake_config.watch_dir = Path("/tmp/kittntabbr_watch")
_fake_config.tabs_dir = Path("/tmp/kittntabbr_tabs")
_fake_config.extensions = {".gp", ".gp3", ".gp4", ".gp5", ".gp6", ".gp7", ".gp8", ".gpx"}
_fake_config.model = "claude-haiku-4-5-20251001"
_fake_config.max_tokens = 128
sys.modules["config"] = _fake_config
