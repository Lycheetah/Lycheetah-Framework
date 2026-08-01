from __future__ import annotations

from .lexer import Lexer
from .parser import Parser
from .semantics import Runtime


def parse_source(source: str):
    tokens, warnings = Lexer(source).tokenize()
    return Parser(tokens).parse(), warnings


def run_source(source: str):
    program, warnings = parse_source(source)
    runtime = Runtime(warnings)
    return program, runtime, runtime.execute(program)
