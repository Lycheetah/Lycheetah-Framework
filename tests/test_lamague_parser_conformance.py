"""
Tests for lamague_parser.py input handling found in review RV14 (batch 13).

Each defect test failed on the committed parser; the controls pass on both.
Grammar questions the BNF leaves open (↯, precedence, the constraint language)
are not decided here.
"""

import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '12_IMPLEMENTATIONS', 'core'))

from lamague_parser import (
    LAMAGUE_EXPANSIONS,
    CompressionMeasurer,
    LAMAGUETokenizer,
    LAMAGUEValidator,
    TokenType,
)

V = LAMAGUEValidator()
OPERATOR_SYMBOLS = ["→", "⊗", "⇌", "⟲", "↯"]


def kinds(expr):
    return [(t.type, t.value) for t in LAMAGUETokenizer().tokenize(expr)]


class TestSubscripts:
    @pytest.mark.active
    @pytest.mark.parametrize("op", OPERATOR_SYMBOLS)
    def test_subscript_ends_at_every_operator(self, op):
        assert kinds(f"Ψ_inv{op}Ao") == [
            (TokenType.FIELD, "Ψ_inv"), (TokenType.OPERATOR, op), (TokenType.FIELD, "Ao")]

    @pytest.mark.active
    @pytest.mark.parametrize("expr", ["Ψ_inv@#$", "Ao_x;y"])
    def test_subscript_cannot_hide_unknown_symbols(self, expr):
        result = V.validate(expr)
        assert not result.valid
        assert any(e.startswith("Unknown symbol") for e in result.errors)

    @pytest.mark.active
    @pytest.mark.parametrize("expr", ["Ψ_", "Ψ_ → Ao"])
    def test_empty_subscript_is_refused(self, expr):
        assert not V.validate(expr).valid

    @pytest.mark.active
    @pytest.mark.parametrize("expr", ["_inv", "Ao → _x"])
    def test_detached_subscript_is_refused(self, expr):
        assert not V.validate(expr).valid

    @pytest.mark.active
    @pytest.mark.parametrize("expr", ["Ψ_inv", "Φ↑_inv", "Ψ_t → Ao_0"])
    def test_ordinary_subscripts_still_attach(self, expr):
        result = V.validate(expr)
        assert result.valid, result.errors
        assert all(t.type != TokenType.SUBSCRIPT for t in result.tokens)


class TestWhitespace:
    @pytest.mark.active
    @pytest.mark.parametrize("expr", ["Ao →\r\nΨ", "Ao → Ψ", "Ao → Ψ"])
    def test_any_unicode_whitespace_separates_tokens(self, expr):
        assert V.validate(expr).valid


class TestLimits:
    """Input past the parser's limits is reported, never raised as RecursionError."""

    @pytest.mark.active
    def test_deep_nesting_is_refused_not_crashed(self):
        result = V.validate("(" * 1000 + "Ao" + ")" * 1000)
        assert not result.valid
        assert "nesting depth" in result.errors[0]

    @pytest.mark.active
    def test_overlong_chain_is_refused_before_its_tree_overflows(self):
        # Committed parser: valid, but tree.symbols() and to_dict() then raised RecursionError
        result = V.validate(" → ".join(["Ao"] * 1500))
        assert not result.valid and result.tree is None

    @pytest.mark.active
    def test_ordinary_depth_and_length_still_parse(self):
        nested = V.validate("(" * 20 + "Ao → Ψ" + ")" * 20)
        chain = V.validate(" → ".join(["Ao"] * 100))
        assert nested.valid and chain.valid
        assert len(chain.tree.symbols()) == 199
        assert chain.tree.to_dict()["type"] == "composition"


class TestGrouping:
    @pytest.mark.active
    def test_parenthesised_grouping_survives_in_the_rendered_value(self):
        left = V.validate("(Ao → Φ) → Ψ").tree
        right = V.validate("Ao → (Φ → Ψ)").tree
        assert left.value != right.value
        for tree in (left, right):
            assert V.validate(tree.value).tree.to_dict() == tree.to_dict()


class TestExpansion:
    @pytest.mark.active
    @pytest.mark.parametrize("op", OPERATOR_SYMBOLS)
    def test_each_operator_expands_to_its_own_meaning(self, op):
        assert LAMAGUE_EXPANSIONS[op] in CompressionMeasurer().build_expansion(f"Ψ {op} Ao")
