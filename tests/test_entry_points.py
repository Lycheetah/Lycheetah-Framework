"""
Tests for the console-script entry points declared in pyproject.toml.

Claim coverage:
  [ACTIVE] Every [project.scripts] target resolves to a callable
  [ACTIVE] lycheetah_guard_mcp exposes the main() that lycheetah.cli imports
  [ACTIVE] lycheetah-guard --help exits 0 without requiring the mcp extra
  [ACTIVE] Missing mcp extra produces a diagnostic exit, not NameError

Why this file exists
--------------------
`lycheetah-guard` was declared in [project.scripts] from 1.0.0 and could never
have run. Three failures were stacked in it:

  1. `build_server()` is annotated `-> Server`, a name bound only inside the
     `try: from mcp.server import Server` block. Annotations were evaluated at
     definition time, so importing the module without the optional `mcp` extra
     raised NameError before the MCP_AVAILABLE flag could be consulted.
  2. `lycheetah/cli.py` does `from applications.lycheetah_guard_mcp import main`,
     and no `main` existed — only `main_stdio` and `main_http`. The script was
     therefore broken even with `mcp` installed.
  3. The MCP_AVAILABLE guard lived in the `if __name__ == "__main__"` block,
     which a console script never executes, so the intended "install mcp"
     message was unreachable from the path users actually take.

None of this was caught because nothing imported the module and nothing ran the
scripts. The tests below close that gap at the level the defect lived on:
resolution of the declared entry point, not the behaviour of the server.
"""

import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '12_IMPLEMENTATIONS'))

REPO_ROOT = os.path.join(os.path.dirname(__file__), '..')


def _declared_scripts():
    """Read [project.scripts] out of pyproject.toml."""
    tomllib = pytest.importorskip(
        "tomllib",
        reason="tomllib is stdlib from 3.11; the floor is 3.10",
    )
    with open(os.path.join(REPO_ROOT, "pyproject.toml"), "rb") as fh:
        return tomllib.load(fh).get("project", {}).get("scripts", {})


@pytest.mark.active
def test_declared_console_scripts_resolve():
    """
    Every 'module:function' in [project.scripts] must import and be callable.

    This is the generic form of the lycheetah-guard defect: a declared entry
    point whose target does not exist. It catches a rename or a moved function
    without anyone having to remember to test the new name.
    """
    import importlib

    scripts = _declared_scripts()
    assert scripts, "no console scripts declared — the test is pointing at nothing"

    unresolved = []
    for name, target in scripts.items():
        module_path, _, attr = target.partition(":")
        try:
            module = importlib.import_module(module_path)
        except ImportError as exc:
            unresolved.append(f"{name}: cannot import {module_path} ({exc})")
            continue
        fn = getattr(module, attr, None)
        if fn is None:
            unresolved.append(f"{name}: {module_path} has no attribute {attr!r}")
        elif not callable(fn):
            unresolved.append(f"{name}: {target} is not callable")

    assert not unresolved, "unresolved console scripts:\n  " + "\n  ".join(unresolved)


@pytest.mark.active
def test_guard_module_imports_without_mcp_extra():
    """
    The module must import whether or not the optional 'mcp' extra is present.

    Regression for the `-> Server` annotation: without
    `from __future__ import annotations` this raises NameError at import.
    """
    import applications.lycheetah_guard_mcp as guard

    assert guard is not None


@pytest.mark.active
def test_guard_module_exposes_main():
    """
    Regression for the missing main(): lycheetah/cli.py imports this name.

    Asserted against the name cli.py actually uses, so renaming one without the
    other fails here rather than at a user's shell.
    """
    import applications.lycheetah_guard_mcp as guard

    assert hasattr(guard, "main"), (
        "lycheetah/cli.py does `from applications.lycheetah_guard_mcp import main`; "
        "that name must exist"
    )
    assert callable(guard.main)


@pytest.mark.active
def test_guard_help_exits_zero():
    """--help must work without the mcp extra installed."""
    import applications.lycheetah_guard_mcp as guard

    with pytest.raises(SystemExit) as excinfo:
        guard.main(["--help"])
    assert excinfo.value.code == 0


@pytest.mark.active
def test_guard_without_mcp_exits_with_diagnostic(monkeypatch, capsys):
    """
    A missing optional dependency must fail as a named, actionable error.

    The failure mode being guarded against is an opaque NameError or
    ImportError traceback, which tells the user nothing about what to install.
    """
    import applications.lycheetah_guard_mcp as guard

    monkeypatch.setattr(guard, "MCP_AVAILABLE", False)

    with pytest.raises(SystemExit) as excinfo:
        guard.main([])
    assert excinfo.value.code == 1

    message = capsys.readouterr().err
    assert "mcp" in message.lower()
    assert "install" in message.lower()


@pytest.mark.active
@pytest.mark.parametrize("argv", [["--port=9000"], ["--port", "9000"], ["--stdio"]])
def test_guard_documented_flags_parse(argv, monkeypatch):
    """
    Every documented invocation must reach dispatch rather than a usage error.

    The hand-rolled parser this replaced understood only `--port=N`; the
    docstring also advertises `--stdio`. With MCP_AVAILABLE forced off, main()
    exits 1 at the dependency gate — which sits *after* parsing. An argparse
    rejection would exit 2 instead, so the exit code distinguishes "parsed and
    stopped for a missing extra" from "no such flag".
    """
    import applications.lycheetah_guard_mcp as guard

    monkeypatch.setattr(guard, "MCP_AVAILABLE", False)

    with pytest.raises(SystemExit) as excinfo:
        guard.main(argv)
    assert excinfo.value.code == 1, f"{argv} was rejected by the parser"
