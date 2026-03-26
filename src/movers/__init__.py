"""Return the appropriate mover for the current operating system."""

import sys

from movers.base import BaseMover
from recursive_harness import harness


def get_mover() -> BaseMover:
    use_macos_mover = harness.ask_bool(
        system_prompt="Reply YES only when the platform requires the macOS Finder-based mover.",
        user_prompt=sys.platform,
        fallback=sys.platform == "darwin",
    )
    if use_macos_mover:
        from movers.macos import MacOSMover
        return MacOSMover()
    from movers.generic import GenericMover
    return GenericMover()
