"""Compatibility import for the installable Lycheetah Guard MCP server."""

from lycheetah.applications.lycheetah_guard_mcp import *  # noqa: F401,F403
from lycheetah.applications.lycheetah_guard_mcp import main as _main


if __name__ == "__main__":
    _main()
