import subprocess
import sys

import pytest


pytestmark = pytest.mark.scaffold


def run_with_blocked_import(package: str, body: str):
    script = f'''
import builtins
real_import = builtins.__import__
def blocked(name, globals=None, locals=None, fromlist=(), level=0):
    if name == {package!r} or name.startswith({package!r} + "."):
        raise ImportError("blocked optional dependency")
    return real_import(name, globals, locals, fromlist, level)
builtins.__import__ = blocked
{body}
'''
    return subprocess.run(
        [sys.executable, "-c", script],
        check=False,
        capture_output=True,
        text=True,
    )


def test_web_module_imports_without_flask_extra():
    result = run_with_blocked_import(
        "flask",
        """
from lycheetah.applications import web_demo
assert web_demo.FLASK_AVAILABLE is False
assert web_demo.app is None
assert web_demo.main() == 1
""",
    )
    assert result.returncode == 0, result.stderr
    assert "Flask not installed" in result.stderr


def test_mcp_module_imports_without_mcp_extra():
    result = run_with_blocked_import(
        "mcp",
        """
from lycheetah.applications import lycheetah_guard_mcp
assert lycheetah_guard_mcp.MCP_AVAILABLE is False
try:
    lycheetah_guard_mcp.build_server()
except RuntimeError as exc:
    assert "[mcp]" in str(exc)
else:
    raise AssertionError("build_server should require the MCP extra")
""",
    )
    assert result.returncode == 0, result.stderr
