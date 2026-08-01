import json
import unittest

from lamague_core import Lexer, parse_source, run_source
from lamague_core.errors import LexError, ParseError, SemanticError
from lamague_core.graph import semantic_graph
from lamague_core.normalizer import canonical, equivalent, normalize


class LexerTests(unittest.TestCase):
    def test_canonical_atoms(self):
        tokens, warnings = Lexer("Ao Φ↑ Ψ Ψ_inv ∅ ⟟;").tokenize()
        self.assertEqual([t.value for t in tokens[:6]], ["Ao", "Φ↑", "Ψ", "Ψ_inv", "∅", "⟟"])
        self.assertEqual(warnings, [])

    def test_anchor_alias(self):
        tokens, warnings = Lexer("A₀;").tokenize()
        self.assertEqual(tokens[0].value, "Ao")
        self.assertEqual(tokens[0].raw, "A₀")
        self.assertEqual(warnings[0].code, "LEGACY_ALIAS")

    def test_delta_alias(self):
        tokens, warnings = Lexer("∆;").tokenize()
        self.assertEqual(tokens[0].value, "Δ")
        self.assertEqual(warnings[0].canonical, "Δ")

    def test_infinity_alias(self):
        tokens, warnings = Lexer("♾;").tokenize()
        self.assertEqual(tokens[0].value, "∞")
        self.assertEqual(tokens[0].raw, "♾")

    def test_ascii_projection_alias(self):
        tokens, warnings = Lexer("Ao -> Φ;").tokenize()
        self.assertEqual(tokens[1].value, "→")
        self.assertEqual(warnings[0].code, "ASCII_ALIAS")

    def test_ascii_exchange_alias(self):
        tokens, warnings = Lexer("Ao <-> Φ;").tokenize()
        self.assertEqual(tokens[1].value, "⇌")

    def test_integral_reserved(self):
        with self.assertRaises(LexError):
            Lexer("Ao ∮ Φ;").tokenize()

    def test_comment(self):
        tokens, _ = Lexer("# comment\nAo;").tokenize()
        self.assertEqual(tokens[0].value, "Ao")


class ParserTests(unittest.TestCase):
    def test_expression_statement(self):
        program, _ = parse_source("Ao → Φ↑;")
        self.assertEqual(program.statements[0].kind, "expression")

    def test_let(self):
        program, _ = parse_source("let x = Ao;")
        self.assertEqual(program.statements[0].name, "x")

    def test_invariant(self):
        program, _ = parse_source("invariant x = Ψ_inv;")
        self.assertEqual(program.statements[0].kind, "invariant")

    def test_macro(self):
        program, _ = parse_source("macro Z₁ X = Ao → Φ;")
        self.assertEqual(program.statements[0].level, "Z₁")

    def test_meta_outside_macro_rejected(self):
        with self.assertRaises(ParseError):
            parse_source("Z₁;")

    def test_missing_semicolon(self):
        with self.assertRaises(ParseError):
            parse_source("Ao → Φ")

    def test_precedence(self):
        program, _ = parse_source("Ao → Φ ⊗ Ψ;")
        expr = program.statements[0].expression
        self.assertEqual(expr.operator, "→")
        self.assertEqual(expr.right.operator, "⊗")

    def test_parentheses(self):
        program, _ = parse_source("(Ao → Φ) ⊗ Ψ;")
        expr = program.statements[0].expression
        self.assertEqual(expr.operator, "⊗")
        self.assertEqual(expr.left.operator, "→")


class SemanticsTests(unittest.TestCase):
    def test_run_hello(self):
        _, runtime, result = run_source("Ao → Φ↑ → Ψ_inv;")
        self.assertEqual(result["status"], "ACCEPTED")
        self.assertEqual(result["statements"][0]["sort"], "Path")

    def test_unknown_reference(self):
        with self.assertRaises(SemanticError):
            run_source("missing;")

    def test_binding_immutable(self):
        with self.assertRaises(SemanticError):
            run_source("let x = Ao; let x = Φ;")

    def test_cross_namespace_immutable(self):
        with self.assertRaises(SemanticError):
            run_source("let x = Ao; invariant x = Φ;")

    def test_reference_resolution(self):
        _, _, result = run_source("let x = Ao → Φ; x;")
        self.assertEqual(result["expressions"][0], "(Ao → Φ)")

    def test_invariant_record(self):
        _, _, result = run_source("invariant stable = Ao → Ψ_inv;")
        self.assertEqual(result["invariants"]["stable"], "(Ao → Ψ_inv)")

    def test_requirement_record(self):
        _, _, result = run_source("require Ao → Φ;")
        self.assertEqual(result["requirements"], ["(Ao → Φ)"])

    def test_prohibition_record(self):
        _, _, result = run_source("forbid Ψ ↯ ∅;")
        self.assertEqual(result["prohibitions"], ["(Ψ ↯ ∅)"])

    def test_claim_boundary(self):
        _, _, result = run_source("Ao;")
        self.assertTrue(any("does not prove truth" in x for x in result["claim_boundary"]))


class AlgebraTests(unittest.TestCase):
    def check(self, source):
        _, _, result = run_source(source)
        return result["checks"][0]["equivalent"]

    def test_fusion_commutative(self):
        self.assertTrue(self.check("check equivalent(Ao ⊗ Φ, Φ ⊗ Ao);"))

    def test_fusion_associative(self):
        self.assertTrue(self.check("check equivalent((Ao ⊗ Φ) ⊗ Ψ, Ao ⊗ (Φ ⊗ Ψ));"))

    def test_fusion_not_idempotent(self):
        self.assertFalse(self.check("check equivalent(Ao ⊗ Ao, Ao);"))

    def test_projection_associative(self):
        self.assertTrue(self.check("check equivalent((Ao → Φ) → Ψ, Ao → (Φ → Ψ));"))

    def test_projection_not_commutative(self):
        self.assertFalse(self.check("check equivalent(Ao → Φ, Φ → Ao);"))

    def test_exchange_commutative(self):
        self.assertTrue(self.check("check equivalent(Ao ⇌ Φ, Φ ⇌ Ao);"))

    def test_exchange_not_associative(self):
        self.assertFalse(self.check("check equivalent((Ao ⇌ Φ) ⇌ Ψ, Ao ⇌ (Φ ⇌ Ψ));"))

    def test_collapse_directed(self):
        self.assertFalse(self.check("check equivalent(Ao ↯ Φ, Φ ↯ Ao);"))

    def test_ascent_directed(self):
        self.assertFalse(self.check("check equivalent(Ao ↗ Φ, Φ ↗ Ao);"))

    def test_recursion_directed(self):
        self.assertFalse(self.check("check equivalent(Ao ⟲ Φ, Φ ⟲ Ao);"))

    def test_duplicate_fusion_preserved(self):
        _, _, result = run_source("Ao ⊗ Ao ⊗ Φ;")
        self.assertEqual(result["expressions"][0].count("Ao"), 2)


class MacroTests(unittest.TestCase):
    def test_macro_expansion(self):
        _, _, result = run_source("macro Z₁ RETURN = Ao → Φ → Ψ_inv; RETURN;")
        self.assertEqual(result["expressions"][0], "(Ao → Φ → Ψ_inv)")

    def test_macro_roundtrip_law(self):
        _, _, result = run_source("macro Z₁ RETURN = Ao → Φ; RETURN;")
        report = result["macros"]["RETURN"]["compression"]
        self.assertEqual(report["roundtrip_law"], "expand(macro) = normalized_expression")

    def test_macro_immutable(self):
        with self.assertRaises(SemanticError):
            run_source("macro Z₁ X = Ao; macro Z₂ X = Φ;")

    def test_macro_level_recorded(self):
        _, _, result = run_source("macro Z₃ ARCH = Ao → Φ;")
        self.assertEqual(result["macros"]["ARCH"]["level"], "Z₃")

    def test_nested_macro(self):
        _, _, result = run_source("macro Z₁ A = Ao → Φ; macro Z₂ B = A → Ψ; B;")
        self.assertEqual(result["expressions"][0], "(Ao → Φ → Ψ)")


class GraphTests(unittest.TestCase):
    def test_graph_deterministic(self):
        _, runtime, _ = run_source("Ao → Φ → Ψ;")
        a = semantic_graph(runtime.expressions[0])
        b = semantic_graph(runtime.expressions[0])
        self.assertEqual(a, b)

    def test_graph_has_root(self):
        _, runtime, _ = run_source("Ao ⊗ Φ;")
        graph = semantic_graph(runtime.expressions[0])
        self.assertIn("root", graph)
        self.assertEqual(len(graph["nodes"]), 3)

    def test_graph_json_serializable(self):
        _, runtime, _ = run_source("Ao ↯ Φ;")
        json.dumps(semantic_graph(runtime.expressions[0]), ensure_ascii=False)


class SeparationTests(unittest.TestCase):
    def test_tim_keyword_not_in_core(self):
        with self.assertRaises(ParseError):
            parse_source('observe x;')

    def test_microorcim_keyword_not_in_core(self):
        with self.assertRaises(ParseError):
            parse_source('intent x;')

    def test_junction_not_silently_available(self):
        with self.assertRaises(ParseError):
            parse_source('condition ↯ (Ao, Φ);')


if __name__ == "__main__":
    unittest.main()
