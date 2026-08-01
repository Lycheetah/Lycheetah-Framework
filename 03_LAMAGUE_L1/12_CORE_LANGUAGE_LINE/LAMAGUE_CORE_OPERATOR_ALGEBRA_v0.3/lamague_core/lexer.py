from __future__ import annotations

from .errors import LexError
from .model import Token, WarningRecord

ALIASES = {
    "A₀": ("Ao", "LEGACY_ALIAS", "Use canonical anchor spelling Ao."),
    "∆": ("Δ", "LEGACY_ALIAS", "Use Greek capital delta Δ U+0394."),
    "♾": ("∞", "LEGACY_ALIAS", "Use infinity ∞ U+221E."),
    "->": ("→", "ASCII_ALIAS", "Use canonical projection arrow →."),
    "<->": ("⇌", "ASCII_ALIAS", "Use canonical exchange arrow ⇌."),
}

KEYWORDS = {
    "let", "invariant", "require", "forbid", "macro", "check",
    "equivalent", "type", "subtype", "describe", "operator",
    "law", "composition",
}
ATOMS = {"⟟", "∅", "⟐", "⟁", "∞", "Ψ_inv", "Ao", "Φ", "Φ↑", "Ψ", "S", "Δ"}
META = {"Z₁", "Z₂", "Z₃"}
OPERATORS = {"→", "⇌", "⊗", "⟲", "↯", "↗"}


class Lexer:
    def __init__(self, source: str):
        self.source = source
        self.i = 0
        self.line = 1
        self.column = 1
        self.tokens: list[Token] = []
        self.warnings: list[WarningRecord] = []

    def current(self) -> str:
        return self.source[self.i] if self.i < len(self.source) else ""

    def starts(self, text: str) -> bool:
        return self.source.startswith(text, self.i)

    def advance(self) -> str:
        ch = self.current()
        self.i += 1
        if ch == "\n":
            self.line += 1
            self.column = 1
        else:
            self.column += 1
        return ch

    def emit(self, kind: str, value: str, raw: str, line: int, column: int):
        self.tokens.append(Token(kind, value, raw, line, column))

    def tokenize(self) -> tuple[list[Token], list[WarningRecord]]:
        while self.i < len(self.source):
            ch = self.current()
            if ch.isspace():
                self.advance()
                continue
            if ch == "#":
                while self.current() and self.current() != "\n":
                    self.advance()
                continue

            line, col = self.line, self.column

            if ch == "∮":
                raise LexError(
                    f"reserved symbol '∮' at {line}:{col}; core recursion is '⟲' "
                    "and '∮' is reserved for integration"
                )

            matched = False
            for raw in ("<->", "->", "A₀"):
                if self.starts(raw):
                    canonical, code, message = ALIASES[raw]
                    for _ in raw:
                        self.advance()
                    kind = "OP" if canonical in OPERATORS else "ATOM"
                    self.emit(kind, canonical, raw, line, col)
                    self.warnings.append(
                        WarningRecord(code, message, raw, canonical, line, col)
                    )
                    matched = True
                    break
            if matched:
                continue

            if ch in {"∆", "♾"}:
                canonical, code, message = ALIASES[ch]
                self.advance()
                self.emit("ATOM", canonical, ch, line, col)
                self.warnings.append(
                    WarningRecord(code, message, ch, canonical, line, col)
                )
                continue

            if ch in OPERATORS:
                self.advance()
                self.emit("OP", ch, ch, line, col)
                continue

            if ch in "=;(),:":
                self.advance()
                self.emit("PUNCT", ch, ch, line, col)
                continue

            if self._is_ident_start(ch):
                raw = self._read_identifier()
                if raw in ATOMS:
                    kind = "ATOM"
                elif raw in META:
                    kind = "META"
                elif raw in KEYWORDS:
                    kind = "KEYWORD"
                else:
                    kind = "IDENT"
                self.emit(kind, raw, raw, line, col)
                continue

            if ch in {"⟟", "∅", "⟐", "⟁", "∞"}:
                self.advance()
                self.emit("ATOM", ch, ch, line, col)
                continue

            raise LexError(f"unexpected character {ch!r} at {line}:{col}")

        self.tokens.append(Token("EOF", "", "", self.line, self.column))
        return self.tokens, self.warnings

    @staticmethod
    def _is_ident_start(ch: str) -> bool:
        return bool(ch) and (ch.isalpha() or ch == "_")

    @staticmethod
    def _is_ident_continue(ch: str) -> bool:
        return bool(ch) and (
            ch.isalnum() or ch == "_" or ch in "₀₁₂₃₄₅₆₇₈₉↑"
        )

    def _read_identifier(self) -> str:
        out: list[str] = []
        while self._is_ident_continue(self.current()):
            out.append(self.advance())
        return "".join(out)
