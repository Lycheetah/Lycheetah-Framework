from __future__ import annotations

from collections.abc import Sequence

from .errors import ParseError
from .model import Atom, Binary, Program, Reference, Sort, Statement, Token

ATOM_SORTS = {
    "⟟": Sort.INVARIANT,
    "∅": Sort.INVARIANT,
    "⟐": Sort.INVARIANT,
    "⟁": Sort.INVARIANT,
    "∞": Sort.INVARIANT,
    "Ψ_inv": Sort.INVARIANT,
    "Ao": Sort.FIELD,
    "Φ": Sort.FIELD,
    "Φ↑": Sort.FIELD,
    "Ψ": Sort.FIELD,
    "S": Sort.FIELD,
    "Δ": Sort.FIELD,
}

PRECEDENCE = {"→": 10, "⇌": 10, "↯": 20, "↗": 20, "⟲": 20, "⊗": 30}


class Parser:
    def __init__(self, tokens: Sequence[Token]):
        self.tokens = list(tokens)
        self.i = 0

    def current(self) -> Token:
        return self.tokens[self.i]

    def advance(self) -> Token:
        token = self.current()
        self.i += 1
        return token

    def match(self, value: str) -> bool:
        if self.current().value == value:
            self.advance()
            return True
        return False

    def expect(self, value: str) -> Token:
        token = self.current()
        if token.value != value:
            raise ParseError(
                f"expected {value!r} at {token.line}:{token.column}, got {token.raw or token.value!r}"
            )
        return self.advance()

    def expect_ident(self) -> Token:
        token = self.current()
        if token.kind != "IDENT":
            raise ParseError(f"expected identifier at {token.line}:{token.column}")
        return self.advance()

    def parse(self) -> Program:
        statements = []
        while self.current().kind != "EOF":
            statements.append(self.parse_statement())
        return Program(tuple(statements))

    def parse_statement(self) -> Statement:
        token = self.current()
        if token.value == "let":
            self.advance()
            name = self.expect_ident().value
            self.expect("=")
            expr = self.parse_expression()
            self.expect(";")
            return Statement("let", name=name, expression=expr)

        if token.value == "invariant":
            self.advance()
            name = self.expect_ident().value
            self.expect("=")
            expr = self.parse_expression()
            self.expect(";")
            return Statement("invariant", name=name, expression=expr)

        if token.value == "require":
            self.advance()
            expr = self.parse_expression()
            self.expect(";")
            return Statement("require", expression=expr)

        if token.value == "forbid":
            self.advance()
            expr = self.parse_expression()
            self.expect(";")
            return Statement("forbid", expression=expr)

        if token.value == "macro":
            self.advance()
            level = self.current()
            if level.kind != "META":
                raise ParseError(f"expected Z₁, Z₂, or Z₃ at {level.line}:{level.column}")
            self.advance()
            name = self.expect_ident().value
            self.expect("=")
            expr = self.parse_expression()
            self.expect(";")
            return Statement("macro", name=name, expression=expr, level=level.value)

        if token.value == "check":
            self.advance()
            self.expect("equivalent")
            self.expect("(")
            left = self.parse_expression()
            self.expect(",")
            right = self.parse_expression()
            self.expect(")")
            self.expect(";")
            return Statement("check", expression=left, expression_b=right)

        expr = self.parse_expression()
        self.expect(";")
        return Statement("expression", expression=expr)

    def parse_expression(self, min_precedence: int = 0):
        left = self.parse_primary()
        while self.current().kind == "OP":
            op_token = self.current()
            precedence = PRECEDENCE[op_token.value]
            if precedence < min_precedence:
                break
            self.advance()
            right = self.parse_expression(precedence + 1)
            left = Binary(raw=op_token.raw, operator=op_token.value, left=left, right=right)
        return left

    def parse_primary(self):
        token = self.advance()
        if token.kind == "ATOM":
            return Atom(raw=token.raw, name=token.value, sort=ATOM_SORTS[token.value])
        if token.kind == "META":
            raise ParseError(
                f"meta symbol {token.value} is legal only in macro declarations at {token.line}:{token.column}"
            )
        if token.kind == "IDENT":
            return Reference(raw=token.raw, name=token.value)
        if token.value == "(":
            expr = self.parse_expression()
            self.expect(")")
            return expr
        raise ParseError(f"unexpected token {token.raw or token.value!r} at {token.line}:{token.column}")
