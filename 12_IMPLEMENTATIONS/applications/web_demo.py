"""Compatibility import for the installable Lycheetah web demo."""

from lycheetah.applications.web_demo import *  # noqa: F401,F403
from lycheetah.applications.web_demo import main as _main


if __name__ == "__main__":
    raise SystemExit(_main())
