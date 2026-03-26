"""Return the appropriate mover for the current operating system."""

import sys

from movers.base import BaseMover


def get_mover() -> BaseMover:
    if sys.platform == "darwin":
        from movers.macos import MacOSMover
        return MacOSMover()
    from movers.generic import GenericMover
    return GenericMover()
