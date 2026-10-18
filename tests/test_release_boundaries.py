"""Regression checks for source-only tools and safe experiment scaffolding.

These check concrete interface boundaries, not scientific effectiveness.
"""

import ast
from pathlib import Path

import pytest

from lycheetah.cli import alexandria_cli


def test_alexandria_help_does_not_require_a_source_module(monkeypatch):
    monkeypatch.setattr(Path, "is_file", lambda _path: False)
    with pytest.raises(SystemExit) as error:
        alexandria_cli(["--help"])
    assert error.value.code == 0


def test_alexandria_without_source_fails_with_an_actionable_message(monkeypatch, capsys):
    monkeypatch.setattr(Path, "is_file", lambda _path: False)
    with pytest.raises(SystemExit) as error:
        alexandria_cli(["health"])
    assert error.value.code == 2
    assert "source checkout" in capsys.readouterr().err


def test_an_empty_health_census_does_not_pass(monkeypatch, capsys):
    import alexandria_agent

    monkeypatch.setattr(alexandria_agent, "health_check", lambda: ({}, "did not run"))
    with pytest.raises(SystemExit) as error:
        alexandria_cli(["health", "--json"])
    assert error.value.code == 1
    assert '"all_passed": false' in capsys.readouterr().out


@pytest.mark.parametrize("name", ["../escape", "a/../../escape", "a\\b", 'a"""', "a\ncode"])
def test_scaffold_names_cannot_traverse_or_inject_source(name, tmp_path, monkeypatch):
    import alexandria_agent

    monkeypatch.setattr(alexandria_agent, "FRAMEWORK_DIR", tmp_path)
    with pytest.raises(ValueError, match="domain name"):
        alexandria_agent.scaffold_new_domain(name)
    assert not list(tmp_path.rglob("*.py"))


def test_scaffold_quotes_descriptions_and_preserves_existing_files(tmp_path, monkeypatch):
    import alexandria_agent

    monkeypatch.setattr(alexandria_agent, "FRAMEWORK_DIR", tmp_path)
    description = 'A description with """ and a newline\nprint("not executed")'
    result = Path(alexandria_agent.scaffold_new_domain("safe_domain", description))
    original = result.read_bytes()
    assert description in ast.get_docstring(ast.parse(result.read_text()))
    with pytest.raises(FileExistsError):
        alexandria_agent.scaffold_new_domain("safe_domain", "replacement")
    assert result.read_bytes() == original
def test_web_cli_missing_extra_has_actionable_error(monkeypatch, capsys):
    import pytest
    from lycheetah.applications import web_demo
    from lycheetah.cli import web_demo_cli

    monkeypatch.setattr(web_demo, "FLASK_AVAILABLE", False)
    monkeypatch.setattr(web_demo, "app", None)
    with pytest.raises(SystemExit) as error:
        web_demo_cli([])
    assert error.value.code == 1
    captured = capsys.readouterr()
    assert "[web]" in captured.err
    assert "running at" not in captured.out

