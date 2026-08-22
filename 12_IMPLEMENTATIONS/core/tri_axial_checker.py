"""Compatibility import for the installable TRI-AXIAL checker."""

from lycheetah.core.tri_axial_checker import *  # noqa: F401,F403
from lycheetah.core.tri_axial_checker import demo as _demo


if __name__ == "__main__":
    _demo()
