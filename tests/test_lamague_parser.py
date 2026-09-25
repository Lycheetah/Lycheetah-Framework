"""
Tests for lamague_parser.py — LAMAGUE BNF tokenizer, parser, validator, compression.

Claim coverage:
  [ACTIVE] Tokenizer classifies invariants / dynamics / fields / meta / operators
  [ACTIVE] Validator accepts well-formed expressions and rejects ill-formed ones
  [ACTIVE] CompressionMeasurer returns computable token/char ratios
  [SCAFFOLD] Compression magnitude (~500:1) is NOT asserted — ratio claim unverified
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '12_IMPLEMENTATIONS', 'core'))

from lamague_parser import (
    LAMAGUETokenizer,
    LAMAGUEParser,
    LAMAGUEValidator,
    CompressionMeasurer,
    TokenType,
    CANONICAL_EXAMPLES,
)


# ── Tokenizer ─────────────────────────────────────────────────────────────────

class TestTokenizer:
    @pytest.mark.active
    def test_tokenizes_field_symbols(self):
        tok = LAMAGUETokenizer()
        tokens = tok.tokenize("Ψ Φ S Δ")
        assert all(t.type == TokenType.FIELD for t in tokens)
        assert [t.value for t in tokens] == ["Ψ", "Φ", "S", "Δ"]

    @pytest.mark.active
    def test_tokenizes_invariants(self):
        tok = LAMAGUETokenizer()
        tokens = tok.tokenize("⟟ ∅ ⟐ ⟁ ∞")
        assert all(t.type == TokenType.INVARIANT for t in tokens)
        assert len(tokens) == 5

    @pytest.mark.active
    def test_tokenizes_multi_char_ao(self):
        tok = LAMAGUETokenizer()
        tokens = tok.tokenize("Ao")
        assert len(tokens) == 1
        assert tokens[0].type == TokenType.FIELD
        assert tokens[0].value == "Ao"

    @pytest.mark.active
    def test_tokenizes_meta_operators(self):
        tok = LAMAGUETokenizer()
        tokens = tok.tokenize("Z₁ Z₂ Z₃")
        assert all(t.type == TokenType.META for t in tokens)
        assert [t.value for t in tokens] == ["Z₁", "Z₂", "Z₃"]

    @pytest.mark.active
    def test_phi_ascent_compound(self):
        """Φ↑ merges into a single FIELD token."""
        tok = LAMAGUETokenizer()
        tokens = tok.tokenize("Φ↑")
        assert len(tokens) == 1
        assert tokens[0].type == TokenType.FIELD
        assert tokens[0].value == "Φ↑"

    @pytest.mark.active
    def test_arrow_classified_as_operator(self):
        tok = LAMAGUETokenizer()
        tokens = tok.tokenize("Ψ → Φ")
        types = [t.type for t in tokens]
        assert types == [TokenType.FIELD, TokenType.OPERATOR, TokenType.FIELD]

    @pytest.mark.active
    def test_empty_string_yields_no_tokens(self):
        tok = LAMAGUETokenizer()
        assert tok.tokenize("") == []
        assert tok.tokenize("   ") == []

    @pytest.mark.active
    def test_positions_are_non_decreasing(self):
        tok = LAMAGUETokenizer()
        tokens = tok.tokenize("Ao → Φ↑ → Ψ")
        positions = [t.position for t in tokens]
        assert positions == sorted(positions)


# ── Parser ────────────────────────────────────────────────────────────────────

class TestParser:
    @pytest.mark.active
    def test_parse_simple_composition(self):
        tok = LAMAGUETokenizer()
        parser = LAMAGUEParser()
        tree, errors = parser.parse(tok.tokenize("Ψ → Φ"))
        assert errors == []
        assert tree is not None
        assert tree.node_type == "composition"

    @pytest.mark.active
    def test_parse_single_leaf(self):
        tok = LAMAGUETokenizer()
        parser = LAMAGUEParser()
        tree, errors = parser.parse(tok.tokenize("Ψ"))
        assert errors == []
        assert tree is not None
        assert tree.node_type == "leaf"
        assert tree.value == "Ψ"

    @pytest.mark.active
    def test_parse_empty_tokens(self):
        parser = LAMAGUEParser()
        tree, errors = parser.parse([])
        assert tree is None
        assert any("Empty" in e for e in errors)

    @pytest.mark.active
    def test_parse_operator_without_left_operand(self):
        tok = LAMAGUETokenizer()
        parser = LAMAGUEParser()
        tree, errors = parser.parse(tok.tokenize("→ Φ"))
        assert tree is None or errors  # must surface as invalid


# ── Validator ─────────────────────────────────────────────────────────────────

class TestValidator:
    @pytest.mark.active
    def test_canonical_expressions_valid(self):
        v = LAMAGUEValidator()
        for example in CANONICAL_EXAMPLES:
            result = v.validate(example["expr"])
            assert result.valid, f"Expected valid: {example['expr']!r} errors={result.errors}"

    @pytest.mark.active
    def test_rejects_leading_operator(self):
        v = LAMAGUEValidator()
        result = v.validate("→ Φ↑")
        assert result.valid is False
        assert result.errors

    @pytest.mark.active
    def test_rejects_double_operator(self):
        v = LAMAGUEValidator()
        result = v.validate("Ao → → Ψ")
        assert result.valid is False

    @pytest.mark.active
    def test_result_carries_tokens_and_expression(self):
        v = LAMAGUEValidator()
        result = v.validate("Ψ → Ao")
        assert result.expression == "Ψ → Ao"
        assert len(result.tokens) >= 3
        assert result.natural_language  # auto-expansion when tree exists

    @pytest.mark.active
    def test_null_to_attractor_valid(self):
        v = LAMAGUEValidator()
        result = v.validate("∅ → ⟟")
        assert result.valid is True


# ── Compression measurer ──────────────────────────────────────────────────────

class TestCompressionMeasurer:
    @pytest.mark.active
    def test_measure_returns_required_keys(self):
        m = CompressionMeasurer()
        ex = CANONICAL_EXAMPLES[0]
        out = m.measure(ex["expr"], ex["nl"])
        for key in ("lamague_tokens", "nl_words", "token_ratio", "char_ratio",
                    "parse_valid", "lamague_chars", "nl_chars"):
            assert key in out

    @pytest.mark.active
    def test_token_ratio_positive_for_canonical(self):
        """NL has more words than LAMAGUE tokens — ratio > 1 (direction only)."""
        m = CompressionMeasurer()
        ex = CANONICAL_EXAMPLES[0]
        out = m.measure(ex["expr"], ex["nl"])
        assert out["parse_valid"] is True
        assert out["token_ratio"] > 1.0
        assert out["nl_words"] > out["lamague_tokens"]

    @pytest.mark.active
    def test_build_expansion_nonempty(self):
        m = CompressionMeasurer()
        expansion = m.build_expansion("Ψ → Ao")
        assert isinstance(expansion, str)
        assert len(expansion) > 0

    @pytest.mark.scaffold
    def test_compression_not_claiming_500_to_1(self):
        """Scaffold honesty: do NOT assert the unverified ~500:1 design estimate."""
        m = CompressionMeasurer()
        ratios = []
        for ex in CANONICAL_EXAMPLES:
            ratios.append(m.measure(ex["expr"], ex["nl"])["token_ratio"])
        # Observed ratios are modest; keep claim as SCAFFOLD by not asserting 500.
        assert all(r < 100 for r in ratios), f"Unexpected huge ratios: {ratios}"
