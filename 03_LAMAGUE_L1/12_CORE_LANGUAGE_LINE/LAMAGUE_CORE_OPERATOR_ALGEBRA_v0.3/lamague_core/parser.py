from __future__ import annotations

from collections.abc import Sequence

from .errors import ParseError
from .model import Atom, Binary, ModifiedAtom, Program, Reference, Statement, Token
from .ontology import (
    ATOM_ONTOLOGY,
    DERIVED_ONTOLOGY,
    CoreType,
    TYPE_NAMES,
)

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
                f"expected {value!r} at {token.line}:{token.column}, "
                f"got {token.raw or token.value!r}"
            )
        return self.advance()

    def expect_ident(self) -> Token:
        token = self.current()
        if token.kind != "IDENT":
            raise ParseError(f"expected identifier at {token.line}:{token.column}")
        return self.advance()

    def expect_type_name(self) -> str:
        token = self.current()
        if token.kind not in {"IDENT", "KEYWORD"} or token.value not in TYPE_NAMES:
            raise ParseError(
                f"expected core type name at {token.line}:{token.column}, "
                f"got {token.raw or token.value!r}"
            )
        self.advance()
        return token.value

    def optional_annotation(self) -> str | None:
        if self.match(":"):
            return self.expect_type_name()
        return None

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
            annotation = self.optional_annotation()
            self.expect("=")
            expr = self.parse_expression()
            self.expect(";")
            return Statement("let", name=name, expression=expr, type_name=annotation)

        if token.value == "invariant":
            self.advance()
            name = self.expect_ident().value
            annotation = self.optional_annotation()
            self.expect("=")
            expr = self.parse_expression()
            self.expect(";")
            return Statement(
                "invariant", name=name, expression=expr, type_name=annotation
            )

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
                raise ParseError(
                    f"expected Z₁, Z₂, or Z₃ at {level.line}:{level.column}"
                )
            self.advance()
            name = self.expect_ident().value
            annotation = self.optional_annotation()
            self.expect("=")
            expr = self.parse_expression()
            self.expect(";")
            return Statement(
                "macro",
                name=name,
                expression=expr,
                level=level.value,
                type_name=annotation,
            )

        if token.value == "check":
            self.advance()
            mode = self.current().value
            if mode == "equivalent":
                self.advance()
                self.expect("(")
                left = self.parse_expression()
                self.expect(",")
                right = self.parse_expression()
                self.expect(")")
                self.expect(";")
                return Statement("check", expression=left, expression_b=right)
            if mode == "type":
                self.advance()
                self.expect("(")
                expr = self.parse_expression()
                self.expect(",")
                expected = self.expect_type_name()
                self.expect(")")
                self.expect(";")
                return Statement("type_check", expression=expr, type_name=expected)
            if mode == "subtype":
                self.advance()
                self.expect("(")
                actual = self.expect_type_name()
                self.expect(",")
                expected = self.expect_type_name()
                self.expect(")")
                self.expect(";")
                return Statement(
                    "subtype_check", type_name=actual, type_name_b=expected
                )
            if mode == "law":
                self.advance()
                self.expect("(")
                op = self.current()
                if op.kind != "OP":
                    raise ParseError(
                        f"expected core operator at {op.line}:{op.column}"
                    )
                self.advance()
                self.expect(",")
                law = self.current()
                if law.kind not in {"IDENT", "KEYWORD"}:
                    raise ParseError(
                        f"expected law name at {law.line}:{law.column}"
                    )
                self.advance()
                self.expect(")")
                self.expect(";")
                return Statement(
                    "law_check",
                    operator=op.value,
                    property_name=law.value,
                )
            if mode == "composition":
                self.advance()
                self.expect("(")
                first = self.current()
                if first.kind != "OP":
                    raise ParseError(
                        f"expected first core operator at "
                        f"{first.line}:{first.column}"
                    )
                self.advance()
                self.expect(",")
                second = self.current()
                if second.kind != "OP":
                    raise ParseError(
                        f"expected second core operator at "
                        f"{second.line}:{second.column}"
                    )
                self.advance()
                self.expect(")")
                self.expect(";")
                return Statement(
                    "composition_check",
                    operator=first.value,
                    operator_b=second.value,
                )
            raise ParseError(
                f"expected equivalent, type, subtype, law, or composition at "
                f"{self.current().line}:{self.current().column}"
            )

        if token.value == "describe":
            self.advance()
            if self.current().value == "operator":
                self.advance()
                op = self.current()
                if op.kind != "OP":
                    raise ParseError(
                        f"expected core operator at {op.line}:{op.column}"
                    )
                self.advance()
                self.expect(";")
                return Statement("describe_operator", operator=op.value)
            expr = self.parse_expression()
            self.expect(";")
            return Statement("describe", expression=expr)

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
            left = Binary(
                raw=op_token.raw,
                operator=op_token.value,
                left=left,
                right=right,
            )
        return left

    def parse_primary(self):
        token = self.advance()

        if token.kind == "ATOM":
            if token.value in ATOM_ONTOLOGY:
                record = ATOM_ONTOLOGY[token.value]
                return Atom(
                    raw=token.raw,
                    name=token.value,
                    core_type=record["type"],
                    role=record["role"],
                )
            record = DERIVED_ONTOLOGY[token.value]
            base_record = ATOM_ONTOLOGY[record["base"]]
            base = Atom(
                raw=record["base"],
                name=record["base"],
                core_type=base_record["type"],
                role=base_record["role"],
            )
            return ModifiedAtom(
                raw=token.raw,
                name=token.value,
                base=base,
                modifier=record["modifier"],
                core_type=record["type"],
                role=record["role"],
            )

        if token.kind == "META":
            raise ParseError(
                f"meta symbol {token.value} is legal only in macro declarations "
                f"at {token.line}:{token.column}"
            )

        if token.kind == "IDENT":
            return Reference(raw=token.raw, name=token.value)

        if token.value == "(":
            expr = self.parse_expression()
            self.expect(")")
            return expr

        raise ParseError(
            f"unexpected token {token.raw or token.value!r} "
            f"at {token.line}:{token.column}"
        )
