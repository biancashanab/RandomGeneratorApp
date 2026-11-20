"""Mathematical random-number generator implementations."""

from .bbs import generate_bbs
from .lcg import generate_lcg

__all__ = ["generate_bbs", "generate_lcg"]
