"""Compatibility import for the installable semantic extractor.

The canonical implementation lives in :mod:`lycheetah.core.semantic_extractor`
so source checkouts and built wheels execute the same code.
"""

from lycheetah.core.semantic_extractor import *  # noqa: F401,F403
from lycheetah.core.semantic_extractor import _main


if __name__ == "__main__":
    raise SystemExit(_main())
