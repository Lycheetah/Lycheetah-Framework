"""
LAMAGUE BNF Parser — Tokenizer, Parser, and Compression Measurer
=================================================================

Implements a parser for LAMAGUE expressions. The grammar it accepts is:

  <input>      ::= <expression> ( "|" <expression> )*
  <expression> ::= <leaf> ( <operator> <leaf> )*
  <operator>   ::= "→" | "⊗" | "⇌" | "⟲" | "↯"
  <leaf>       ::= <invariant> | <field> | <meta> | "↑" | "(" <expression> ")"
  <field>      ::= ( "Ψ" | "Φ" | "S" | "Δ" ) [ "↑" ] [ <subscript> ]
                 | "Ao" [ <subscript> ]
  <subscript>  ::= "_" <letter-or-digit>+
  <invariant>  ::= "⟟" | "∅" | "⟐" | "⟁" | "∞"
  <meta>       ::= "Z₁" | "Z₂" | "Z₃"

Operators share one precedence and associate to the left. Each expression after
"|" is a constraint: it is validated but not attached to the tree. Input with
more than MAX_OPERATORS operators or MAX_NESTING levels of parentheses is
refused with an error rather than exhausting the stack.

This is not yet the grammar of 03_LAMAGUE_L1/04_BNF_GRAMMAR.md. That file lists
↯ only as a <dynamic> (and, in prose, as a junction), defines no "↑" compound,
subscript, "|" or parentheses, leaves <composition> ambiguous, and writes its
canonical constraint as C(Ψ_t) ≥ C(Ψ₀), which this parser rejects. Settling those
differences is a grammar decision for the author; see
FOR-REVIEW/2026-10-22_OPUS_REVIEW/BATCH13_FINDINGS_AND_LEDGER.md.

PURPOSE:
  1. Validates LAMAGUE expressions against the grammar above
  2. Builds parse trees for structured analysis
  3. Measures actual compression ratio vs natural language
  4. Makes the "LAMAGUE compresses alignment concepts" claim empirically testable

CLAIM STATUS:
  [ACTIVE]   Tokenizer classifies the symbols listed above
  [ACTIVE]   Parser accepts the grammar above and reports everything else
  [ACTIVE]   Compression measurement is computable from parse tree + reference text
  [SCAFFOLD] The compression ratio claim (source: "~500:1") is unverified. The demo
             measures ~2.9:1 tokens and ~10.9:1 characters on the five
             CANONICAL_EXAMPLES below against hand-written English. Five chosen
             examples demonstrate the tool; they do not measure LAMAGUE in general.
  [CONJECTURE] LAMAGUE Turing-completeness — not proven; not assumed here.

HONEST NOTE:
  The "500:1 compression ratio" cited in source documents is a design estimate.
  The measurement infrastructure in this file allows testing against real examples.
  Results from the demo show actual ratios; they may differ substantially from 500:1.

Author: Mackenzie Clark (Lycheetah Foundation)
Implementation: Sol (Sonnet 4.6, Anthropic) — March 2026
"""

import sys
from dataclasses import dataclass, field
from typing import List, Optional, Tuple, Dict
from enum import Enum


# =============================================================================
# TOKEN TYPES
# =============================================================================

class TokenType(Enum):
    INVARIANT   = "invariant"    # ⟟ ∅ ⟐ ⟁ ∞
    DYNAMIC     = "dynamic"      # ↑ ↯ ⟲ ⊗ ⇌ →
    FIELD       = "field"        # Ψ Φ Ao S Δ
    META        = "meta"         # Z₁ Z₂ Z₃
    OPERATOR    = "operator"     # → ⊗ ⇌ ⟲  (composition operators)
    MODIFIER    = "modifier"     # ↑ as Φ-modifier (Φ↑ compound)
    SUBSCRIPT   = "subscript"    # _inv, _t, etc.
    LPAREN      = "lparen"       # (
    RPAREN      = "rparen"       # )
    PIPE        = "pipe"         # |  (constraint separator)
    UNKNOWN     = "unknown"


@dataclass
class Token:
    type: TokenType
    value: str
    position: int

    def __repr__(self):
        return f"Token({self.type.value}, {repr(self.value)}, pos={self.position})"


# =============================================================================
# SYMBOL TABLES
# =============================================================================

INVARIANTS = {"⟟", "∅", "⟐", "⟁", "∞"}
DYNAMICS   = {"↑", "↯", "⟲", "⊗", "⇌", "→"}
FIELDS     = {"Ψ", "Φ", "S", "Δ"}
MULTI_CHAR_FIELDS = {"Ao"}
META       = {"Z₁", "Z₂", "Z₃"}
OPERATORS  = {"→", "⊗", "⇌", "⟲", "↯"}

# Parser limits. The parser recurses once per parenthesis level and the tree
# grows one level per operator, so input past either limit could exhaust
# Python's stack; it is refused with an error instead.
MAX_OPERATORS = 256
MAX_NESTING   = 64

# Natural language expansions for compression measurement
LAMAGUE_EXPANSIONS = {
    "Ψ":   "drift field — deviation from invariant trajectory",
    "Φ":   "orientation field — direction toward purpose",
    "Φ↑":  "ascent operator — reorientation toward purpose via gradient",
    "Ao":  "anchor operator — project to low-entropy baseline state",
    "S":   "entropy field — disorder measure",
    "Δ":   "variation — change operator",
    "⟟":   "fixed point — stable attractor state",
    "∅":   "zero node — null state or absence",
    "⟐":   "stable triad",
    "⟁":   "integrity crest",
    "∞":   "closed infinite — cycle completion",
    "↑":   "ascent — orientation upward",
    "↯":   "collapse — entropy spike or junction point",
    "⟲":   "recursion — return to cycle",
    "⊗":   "fusion — merge two states",
    "⇌":   "bidirectional exchange",
    "→":   "projection or transformation toward",
    "Z₁":  "minimal compression operator — atomic level",
    "Z₂":  "horizon compression operator — edge layer",
    "Z₃":  "zenith compression operator — foundation layer",
}


# =============================================================================
# TOKENIZER
# =============================================================================

class LAMAGUETokenizer:
    """
    Tokenizes LAMAGUE expressions into a stream of typed tokens.

    Handles multi-character symbols (Ao, Z₁, Φ↑) and subscripts (_inv, _t).
    """

    def tokenize(self, text: str) -> List[Token]:
        tokens = []
        i = 0
        text = text.strip()

        while i < len(text):
            ch = text[i]

            # Skip whitespace (any Unicode space, so CRLF text and NBSP separate tokens)
            if ch.isspace():
                i += 1
                continue

            # Multi-character: Ao
            if text[i:i+2] == "Ao":
                tokens.append(Token(TokenType.FIELD, "Ao", i))
                i += 2
                # Check for subscript: Ao_something
                i = self._eat_subscript(text, i, tokens)
                continue

            # Meta operators Z₁ Z₂ Z₃
            if ch == 'Z' and i+1 < len(text) and text[i+1] in ('₁', '₂', '₃'):
                tok = text[i:i+2]
                tokens.append(Token(TokenType.META, tok, i))
                i += 2
                continue

            # Invariants
            if ch in INVARIANTS:
                tokens.append(Token(TokenType.INVARIANT, ch, i))
                i += 1
                continue

            # Fields
            if ch in FIELDS:
                tokens.append(Token(TokenType.FIELD, ch, i))
                i += 1
                # Check for ↑ modifier (Φ↑)
                if i < len(text) and text[i] == '↑':
                    # Merge into compound Φ↑
                    tokens[-1] = Token(TokenType.FIELD, tokens[-1].value + '↑', tokens[-1].position)
                    i += 1
                # Check for subscript
                i = self._eat_subscript(text, i, tokens)
                continue

            # Dynamics (some overlap with operators)
            if ch in DYNAMICS:
                # → is both a dynamic and an operator — classify by context
                # For now, mark as OPERATOR if it stands between two expressions
                # Simple heuristic: treat as operator
                if ch == '→':
                    tokens.append(Token(TokenType.OPERATOR, ch, i))
                elif ch == '⟲':
                    tokens.append(Token(TokenType.OPERATOR, ch, i))
                elif ch == '⊗':
                    tokens.append(Token(TokenType.OPERATOR, ch, i))
                elif ch == '⇌':
                    tokens.append(Token(TokenType.OPERATOR, ch, i))
                elif ch == '↯':
                    tokens.append(Token(TokenType.OPERATOR, ch, i))
                elif ch == '↑':
                    tokens.append(Token(TokenType.MODIFIER, ch, i))
                else:
                    tokens.append(Token(TokenType.DYNAMIC, ch, i))
                i += 1
                continue

            # Parentheses and pipe
            if ch == '(':
                tokens.append(Token(TokenType.LPAREN, ch, i))
                i += 1
                continue
            if ch == ')':
                tokens.append(Token(TokenType.RPAREN, ch, i))
                i += 1
                continue
            if ch == '|':
                tokens.append(Token(TokenType.PIPE, ch, i))
                i += 1
                continue

            # Subscript _ prefix
            if ch == '_':
                i = self._eat_subscript(text, i, tokens, standalone=True)
                continue

            # Unknown
            tokens.append(Token(TokenType.UNKNOWN, ch, i))
            i += 1

        return tokens

    def _eat_subscript(self, text: str, i: int, tokens: List[Token],
                       standalone: bool = False) -> int:
        """Consume a subscript like _inv, _t, _0 and attach it to the previous token.

        The body is letters and digits only. Anything else ends it and is tokenized
        on its own, so an operator or unknown symbol can never hide inside a name.
        """
        if i < len(text) and text[i] == '_':
            j = i + 1
            while j < len(text) and text[j].isalnum():
                j += 1
            subscript = text[i:j]
            if j == i + 1:
                tokens.append(Token(TokenType.UNKNOWN, '_', i))  # empty subscript
            elif tokens and not standalone:
                tokens[-1] = Token(tokens[-1].type, tokens[-1].value + subscript, tokens[-1].position)
            else:
                tokens.append(Token(TokenType.SUBSCRIPT, subscript, i))
            return j
        return i


# =============================================================================
# PARSE TREE
# =============================================================================

@dataclass
class ParseNode:
    """A node in the LAMAGUE parse tree."""
    node_type: str          # 'expression', 'composition', 'leaf'
    symbol_class: str       # 'invariant', 'field', 'dynamic', 'meta', 'composition'
    value: str
    children: List['ParseNode'] = field(default_factory=list)

    def to_dict(self) -> dict:
        d = {"type": self.node_type, "class": self.symbol_class, "value": self.value}
        if self.children:
            d["children"] = [c.to_dict() for c in self.children]
        return d

    def symbols(self) -> List[str]:
        """All leaf symbols in this subtree."""
        if not self.children:
            return [self.value]
        result = []
        for c in self.children:
            result.extend(c.symbols())
        return result


@dataclass
class ParseResult:
    """Result of parsing a LAMAGUE expression."""
    expression: str
    tokens: List[Token]
    tree: Optional[ParseNode]
    valid: bool
    errors: List[str] = field(default_factory=list)
    natural_language: str = ""       # Reference natural language equivalent
    compression_ratio: Optional[float] = None


# =============================================================================
# PARSER
# =============================================================================

class LAMAGUEParser:
    """
    Recursive descent parser for the grammar in the module docstring:
      expression  := leaf (operator leaf)*
      leaf        := invariant | field | meta | modifier | '(' expression ')'
    """

    LEAF_CLASSES = {
        TokenType.INVARIANT: "invariant",
        TokenType.FIELD: "field",
        TokenType.DYNAMIC: "dynamic",
        TokenType.META: "meta",
        TokenType.MODIFIER: "modifier",
    }

    def parse(self, tokens: List[Token]) -> Tuple[Optional[ParseNode], List[str]]:
        """Parse token list into a parse tree. Returns (tree, errors)."""
        if not tokens:
            return None, ["Empty expression"]

        # Limits are checked before any recursion (see MAX_OPERATORS).
        operators = sum(1 for t in tokens if t.type == TokenType.OPERATOR)
        nesting = deepest = 0
        for t in tokens:
            if t.type == TokenType.LPAREN:
                nesting += 1
                deepest = max(deepest, nesting)
            elif t.type == TokenType.RPAREN:
                nesting -= 1
        if operators > MAX_OPERATORS or deepest > MAX_NESTING:
            return None, [f"Expression exceeds parser limits: {operators} operators "
                          f"(max {MAX_OPERATORS}), nesting depth {deepest} (max {MAX_NESTING})"]

        # Split on the constraint pipe. Unknown symbols are reported in every
        # segment: text after '|' is validated, never skipped. 04_BNF_GRAMMAR.md
        # has no production for '|' yet, so each constraint is checked as an
        # ordinary expression and is not attached to the returned tree.
        errors = []
        segments: List[List[Token]] = [[]]
        for t in tokens:
            if t.type == TokenType.PIPE:
                segments.append([])
            elif t.type == TokenType.UNKNOWN:
                errors.append(f"Unknown symbol '{t.value}' at position {t.position}")
            else:
                segments[-1].append(t)

        clean = segments[0]
        if not clean:
            return None, errors or ["No valid tokens"]

        node, parse_errors = self._parse_complete(clean)
        errors.extend(parse_errors)

        for constraint in segments[1:]:
            if not constraint:
                errors.append("Empty constraint after '|'")
                continue
            _, constraint_errors = self._parse_complete(constraint)
            errors.extend(f"Constraint: {e}" for e in constraint_errors)

        return node, errors

    def _parse_complete(self, tokens: List[Token]
                        ) -> Tuple[Optional[ParseNode], List[str]]:
        """Parse one expression that must consume every token it is given."""
        node, remaining, errors = self._parse_expression(tokens, 0)
        # Catch trailing unparsed input rather than silently ignoring it
        if remaining < len(tokens):
            trailing_str = " ".join(t.value for t in tokens[remaining:])
            errors.append(f"Unexpected trailing tokens after complete expression: {trailing_str}")
        return node, errors

    def _parse_expression(self, tokens: List[Token], pos: int
                          ) -> Tuple[Optional[ParseNode], int, List[str]]:
        """Parse: leaf (operator leaf)*"""
        errors = []

        left, pos, errs = self._parse_leaf(tokens, pos)
        errors.extend(errs)

        if left is None:
            return None, pos, errors

        # Consume operator + right-hand-side pairs
        while pos < len(tokens) and tokens[pos].type == TokenType.OPERATOR:
            op_tok = tokens[pos]
            pos += 1

            right, pos, errs = self._parse_leaf(tokens, pos)
            errors.extend(errs)

            if right is None:
                errors.append(f"Expected expression after operator '{op_tok.value}'")
                break

            # Build composition node
            left = ParseNode(
                node_type="composition",
                symbol_class="composition",
                value=f"{left.value} {op_tok.value} {right.value}",
                children=[left, ParseNode("operator", "operator", op_tok.value), right]
            )

        return left, pos, errors

    def _parse_leaf(self, tokens: List[Token], pos: int
                    ) -> Tuple[Optional[ParseNode], int, List[str]]:
        """Parse: invariant | field | meta | modifier | '(' expression ')'"""
        if pos >= len(tokens):
            return None, pos, ["Unexpected end of expression"]

        tok = tokens[pos]

        if tok.type == TokenType.LPAREN:
            pos += 1
            node, pos, errors = self._parse_expression(tokens, pos)
            if node is not None and node.node_type == "composition":
                # Keep the written grouping: "Ao → (Φ → Ψ)" must not render as
                # "Ao → Φ → Ψ", which reparses left-associatively into another tree.
                node.value = f"({node.value})"
            if pos < len(tokens) and tokens[pos].type == TokenType.RPAREN:
                pos += 1
            else:
                errors.append("Missing closing parenthesis")
            return node, pos, errors

        if tok.type in self.LEAF_CLASSES:
            node = ParseNode(
                node_type="leaf",
                symbol_class=self.LEAF_CLASSES[tok.type],
                value=tok.value
            )
            return node, pos + 1, []

        # A subscript must belong to a symbol; on its own it is not an expression
        if tok.type == TokenType.SUBSCRIPT:
            return None, pos, [f"Subscript '{tok.value}' is not attached to a symbol"]

        return None, pos, [f"Unexpected token '{tok.value}' of type {tok.type.value}"]


# =============================================================================
# COMPRESSION MEASURER
# =============================================================================

class CompressionMeasurer:
    """
    Measures the actual compression ratio of a LAMAGUE expression
    against its natural language equivalent.

    This is the primary empirical tool for testing the compression claim.
    """

    def __init__(self):
        self.tokenizer = LAMAGUETokenizer()
        self.parser = LAMAGUEParser()

    def measure(self, lamague_expr: str, natural_language: str) -> Dict:
        """
        Measure compression of a LAMAGUE expression vs its natural language equivalent.

        Args:
            lamague_expr: The LAMAGUE expression (e.g. "Ao → Φ↑ → Ψ_inv")
            natural_language: The equivalent in plain English

        Returns:
            Dict with compression metrics
        """
        # Tokenize
        tokens = self.tokenizer.tokenize(lamague_expr)
        tree, errors = self.parser.parse(tokens)

        # Token counts
        lamague_tokens = [t for t in tokens
                         if t.type not in (TokenType.UNKNOWN, TokenType.PIPE)]
        nl_words = natural_language.split()

        # Character counts
        lamague_chars = len(lamague_expr.replace(' ', ''))
        nl_chars = len(natural_language.replace(' ', ''))

        # Ratios
        token_ratio = len(nl_words) / max(1, len(lamague_tokens))
        char_ratio = nl_chars / max(1, lamague_chars)

        return {
            "lamague_expression": lamague_expr,
            "natural_language": natural_language,
            "lamague_tokens": len(lamague_tokens),
            "nl_words": len(nl_words),
            "lamague_chars": lamague_chars,
            "nl_chars": nl_chars,
            "token_ratio": round(token_ratio, 2),
            "char_ratio": round(char_ratio, 2),
            "parse_valid": len(errors) == 0,
            "parse_errors": errors,
            "symbol_classes": {tt.value: sum(1 for x in lamague_tokens if x.type == tt)
                               for tt in TokenType} if lamague_tokens else {},
        }

    def build_expansion(self, lamague_expr: str) -> str:
        """
        Expand a LAMAGUE expression to natural language using symbol dictionary.
        Useful when no reference text is provided.
        """
        tokens = self.tokenizer.tokenize(lamague_expr)
        parts = []
        for tok in tokens:
            if tok.value in LAMAGUE_EXPANSIONS:
                parts.append(LAMAGUE_EXPANSIONS[tok.value])
            elif tok.type not in (TokenType.UNKNOWN, TokenType.PIPE):
                parts.append(tok.value)
        return " | ".join(parts)


# =============================================================================
# LAMAGUE VALIDATOR
# =============================================================================

class LAMAGUEValidator:
    """
    Validates LAMAGUE expressions and provides structured feedback.
    """

    def __init__(self):
        self.tokenizer = LAMAGUETokenizer()
        self.parser = LAMAGUEParser()

    def validate(self, expression: str) -> ParseResult:
        """Validate a LAMAGUE expression and return structured result."""
        tokens = self.tokenizer.tokenize(expression)
        tree, errors = self.parser.parse(tokens)
        valid = len(errors) == 0 and tree is not None

        result = ParseResult(
            expression=expression,
            tokens=tokens,
            tree=tree,
            valid=valid,
            errors=errors
        )

        # Auto-expand to natural language
        if tree:
            measurer = CompressionMeasurer()
            result.natural_language = measurer.build_expansion(expression)

        return result


# =============================================================================
# DEMO
# =============================================================================

CANONICAL_EXAMPLES = [
    {
        "expr": "Ao → Φ↑ → Ψ_inv",
        "nl": "Start from your baseline ethical anchor, reorient toward your intended purpose direction, and return to the invariant attractor trajectory"
    },
    {
        "expr": "Ψ ↯ Ao → Φ↑ → Ψ_inv",
        "nl": "Detect drift state, then collapse entropy to anchor, reorient toward purpose, and return to invariant trajectory"
    },
    {
        "expr": "Φ↑ ⊗ Ψ → ⟟",
        "nl": "Fuse the orientation field with the drift field, transform toward the fixed point stable attractor"
    },
    {
        "expr": "∅ → Ao → Φ↑ → ⟟",
        "nl": "From the null state, anchor to baseline, ascend toward orientation, and arrive at the fixed stable attractor"
    },
    {
        "expr": "Ψ → Ao",
        "nl": "Apply drift correction to return system to anchor state"
    },
]


def demo():
    """Demonstrate the LAMAGUE parser and measure actual compression ratios."""

    print("LAMAGUE BNF PARSER + COMPRESSION MEASURER")
    print("=" * 65)
    print("Status: [ACTIVE] parser | [SCAFFOLD] compression ratio measurement")
    print()

    validator = LAMAGUEValidator()
    measurer = CompressionMeasurer()

    # Validation demo
    print("PART 1: EXPRESSION VALIDATION")
    print("-" * 40)

    test_expressions = [
        ("Ao → Φ↑ → Ψ_inv",       True,  "canonical TRIAD cycle"),
        ("Ψ ↯ Ao → Φ↑",           True,  "drift correction"),
        ("Φ↑ ⊗ Ψ → ⟟",           True,  "fusion to fixed point"),
        ("∅ → ⟟",                  True,  "null to attractor"),
        ("→ Φ↑",                   False, "operator without left operand"),
        ("Ao → → Ψ",               False, "double operator"),
    ]

    for expr, expected_valid, description in test_expressions:
        result = validator.validate(expr)
        status = "✓ VALID" if result.valid else "✗ INVALID"
        match = "✓" if result.valid == expected_valid else "✗ UNEXPECTED"
        print(f"  {status}  {match}  '{expr}' ({description})")
        if not result.valid:
            for err in result.errors:
                print(f"            → {err}")

    print()
    print("PART 2: COMPRESSION MEASUREMENT")
    print("-" * 40)
    print("Measuring actual compression ratios (this tests the source claim):")
    print()

    ratios_token = []
    ratios_char = []

    for example in CANONICAL_EXAMPLES:
        m = measurer.measure(example["expr"], example["nl"])
        ratios_token.append(m["token_ratio"])
        ratios_char.append(m["char_ratio"])

        print(f"  LAMAGUE: {example['expr']}")
        print(f"  English: {example['nl'][:70]}{'...' if len(example['nl']) > 70 else ''}")
        print(f"  Tokens:  {m['lamague_tokens']} LAMAGUE vs {m['nl_words']} English words → {m['token_ratio']}:1")
        print(f"  Chars:   {m['lamague_chars']} vs {m['nl_chars']} → {m['char_ratio']}:1")
        print(f"  Valid:   {'Yes' if m['parse_valid'] else 'No — ' + str(m['parse_errors'])}")
        print()

    avg_token = sum(ratios_token) / len(ratios_token)
    avg_char  = sum(ratios_char)  / len(ratios_char)

    print("=" * 65)
    print(f"MEASURED COMPRESSION (across {len(CANONICAL_EXAMPLES)} canonical examples):")
    print(f"  Average token ratio: {avg_token:.1f}:1")
    print(f"  Average char ratio:  {avg_char:.1f}:1")
    print()
    print("SOURCE CLAIM: '~500:1 compression for alignment concepts'")
    print(f"MEASURED:     ~{avg_token:.0f}:1 (token) / ~{avg_char:.0f}:1 (character)")
    print()
    print("INTERPRETATION:")
    if avg_token >= 100:
        print("  Token ratio supports a strong compression claim [approaching source figure]")
    elif avg_token >= 10:
        print("  Token ratio shows substantial compression but well below 500:1")
        print("  Source claim was likely a design aspiration, not a measured result")
        print("  Honest label: 'LAMAGUE achieves substantial compression — typically ~{:.0f}:1'.".format(avg_token))
    else:
        print("  Token ratio shows moderate compression; 500:1 claim requires revision")
    print()
    print("STATUS: [SCAFFOLD] — compression is real and substantial;")
    print("        exact ratio depends on domain and reference text length.")
    print("        This parser enables systematic measurement across domains.")

    print()
    print("PART 3: SYMBOL CLASS DISTRIBUTION")
    print("-" * 40)
    print("Parsing 'Ψ ↯ Ao → Φ↑ → Ψ_inv':")
    result = validator.validate("Ψ ↯ Ao → Φ↑ → Ψ_inv")
    if result.tree:
        symbols = result.tree.symbols()
        print(f"  Symbols: {symbols}")
        print(f"  Natural language expansion:")
        print(f"  {result.natural_language}")


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")  # script runs only; importing never touches stdout
    demo()
