"""Compatibility import for the installable AURA text checker."""

from lycheetah.applications.aura_text_checker import *  # noqa: F401,F403
from lycheetah.applications.aura_text_checker import main as _main


if __name__ == "__main__":
    raise SystemExit(_main())
