import json
import unittest

from lamague_core import Lexer, parse_source, run_source
from lamague_core.errors import LexError, ParseError, SemanticError
from lamague_core.graph import semantic_graph
from lamague_core.normalizer import canonical, equivalent, normalize
from lamague_core.model import ModifiedAtom
from lamague_core.ontology import CoreType, is_subtype, ontology_export
from lamague_core.contracts import (
    LawStatus, OPERATOR_CONTRACTS, contract_hash, contract_record,
    law_result, structurally_composable, composition_matrix,
    contracts_export,
)
from lamague_core.normalizer import normalize_with_trace


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
        self.assertEqual(result["statements"][0]["type"], "Path")

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
        self.assertEqual(result["invariants"]["stable"]["normal_form"], "(Ao → Ψ_inv)")

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


class OntologyTests(unittest.TestCase):
    def test_phi_ascent_is_derived(self):
        program, _ = parse_source("Φ↑;")
        expr = program.statements[0].expression
        self.assertIsInstance(expr, ModifiedAtom)
        self.assertEqual(expr.base.name, "Φ")
        self.assertEqual(expr.modifier, "↑")
        self.assertEqual(expr.core_type, CoreType.MODIFIED_FIELD)

    def test_psi_inv_is_derived(self):
        program, _ = parse_source("Ψ_inv;")
        expr = program.statements[0].expression
        self.assertIsInstance(expr, ModifiedAtom)
        self.assertEqual(expr.base.name, "Ψ")
        self.assertEqual(expr.modifier, "inv")
        self.assertEqual(expr.core_type, CoreType.INVARIANT_FIELD)

    def test_modified_normal_form_preserved(self):
        _, _, result = run_source("Φ↑; Ψ_inv;")
        self.assertEqual(result["expressions"], ["Φ↑", "Ψ_inv"])

    def test_null_type(self):
        _, _, result = run_source("describe ∅;")
        desc = result["descriptions"][0]
        self.assertEqual(desc["type"], "NullState")
        self.assertEqual(desc["ontology"]["role"], "intentional_null")

    def test_null_is_invariant_subtype(self):
        self.assertTrue(is_subtype(CoreType.NULL_STATE, CoreType.INVARIANT))

    def test_null_not_field(self):
        self.assertFalse(is_subtype(CoreType.NULL_STATE, CoreType.FIELD))

    def test_invariant_field_multiple_inheritance(self):
        self.assertTrue(is_subtype(CoreType.INVARIANT_FIELD, CoreType.FIELD))
        self.assertTrue(is_subtype(CoreType.INVARIANT_FIELD, CoreType.INVARIANT))

    def test_modified_field_subtype(self):
        self.assertTrue(is_subtype(CoreType.MODIFIED_FIELD, CoreType.FIELD))
        self.assertTrue(is_subtype(CoreType.MODIFIED_FIELD, CoreType.STATE_LIKE))

    def test_composite_subtype(self):
        self.assertTrue(is_subtype(CoreType.PATH, CoreType.COMPOSITE))
        self.assertTrue(is_subtype(CoreType.PATH, CoreType.STATE_LIKE))

    def test_ontology_export(self):
        payload = ontology_export()
        self.assertEqual(payload["version"], "0.3.0")
        self.assertIn("Φ↑", payload["derived_atoms"])
        self.assertIn("Ψ_inv", payload["derived_atoms"])


class TypeAnnotationTests(unittest.TestCase):
    def test_exact_annotation(self):
        _, _, result = run_source("let x: Field = Ao;")
        self.assertEqual(result["bindings"]["x"]["type"], "Field")

    def test_subtype_annotation(self):
        _, _, result = run_source("let x: Field = Φ↑;")
        self.assertEqual(result["bindings"]["x"]["type"], "ModifiedField")

    def test_invariant_field_as_field(self):
        _, _, result = run_source("let x: Field = Ψ_inv;")
        self.assertEqual(result["bindings"]["x"]["type"], "InvariantField")

    def test_invariant_field_as_invariant(self):
        _, _, result = run_source("let x: Invariant = Ψ_inv;")
        self.assertEqual(result["bindings"]["x"]["type"], "InvariantField")

    def test_bad_annotation_rejected(self):
        with self.assertRaises(SemanticError):
            run_source("let x: Field = ⟟;")

    def test_bad_composite_annotation_rejected(self):
        with self.assertRaises(SemanticError):
            run_source("let x: Fusion = Ao → Φ;")

    def test_invariant_annotation(self):
        _, _, result = run_source(
            "invariant stable: Path = Ao → Ψ_inv;"
        )
        self.assertEqual(result["invariants"]["stable"]["type"], "Path")

    def test_macro_annotation(self):
        _, _, result = run_source(
            "macro Z₁ RETURN: Path = Ao → Φ; RETURN;"
        )
        self.assertEqual(result["macros"]["RETURN"]["type"], "Path")

    def test_unknown_type_name_rejected(self):
        with self.assertRaises(ParseError):
            parse_source("let x: Consciousness = Ao;")


class TypeCheckTests(unittest.TestCase):
    def test_check_type_exact(self):
        _, _, result = run_source("check type(Ao, Field);")
        self.assertTrue(result["checks"][0]["matches"])

    def test_check_type_subtype(self):
        _, _, result = run_source("check type(Φ↑, Field);")
        self.assertTrue(result["checks"][0]["matches"])

    def test_check_type_false(self):
        _, _, result = run_source("check type(⟟, Field);")
        self.assertFalse(result["checks"][0]["matches"])

    def test_check_psi_inv_field(self):
        _, _, result = run_source("check type(Ψ_inv, Field);")
        self.assertTrue(result["checks"][0]["matches"])

    def test_check_psi_inv_invariant(self):
        _, _, result = run_source("check type(Ψ_inv, Invariant);")
        self.assertTrue(result["checks"][0]["matches"])

    def test_check_subtype_true(self):
        _, _, result = run_source(
            "check subtype(ModifiedField, Field);"
        )
        self.assertTrue(result["checks"][0]["is_subtype"])

    def test_check_subtype_false(self):
        _, _, result = run_source(
            "check subtype(InvariantMarker, Field);"
        )
        self.assertFalse(result["checks"][0]["is_subtype"])


class DescribeTests(unittest.TestCase):
    def test_describe_primitive(self):
        _, _, result = run_source("describe Ao;")
        desc = result["descriptions"][0]
        self.assertEqual(desc["type"], "Field")
        self.assertEqual(desc["ontology"]["role"], "anchor")

    def test_describe_modified(self):
        _, _, result = run_source("describe Φ↑;")
        desc = result["descriptions"][0]
        self.assertEqual(desc["decomposition"], {"base": "Φ", "modifier": "↑"})

    def test_describe_binary_signature(self):
        _, _, result = run_source("describe Ao → Φ;")
        desc = result["descriptions"][0]
        self.assertEqual(desc["type"], "Path")
        self.assertEqual(desc["signature"]["returns"], "Path")

    def test_graph_exposes_modifier(self):
        _, runtime, _ = run_source("Φ↑;")
        graph = semantic_graph(runtime.expressions[0])
        self.assertTrue(any(n["kind"] == "Modifier" for n in graph["nodes"]))


class BoundaryLockTests(unittest.TestCase):
    def test_null_boundary_present(self):
        _, _, result = run_source("∅;")
        self.assertTrue(result["ontology_lock"]["null_is_not_missing"])
        self.assertTrue(any("intentional null" in x for x in result["claim_boundary"]))

    def test_tim_still_rejected(self):
        with self.assertRaises(ParseError):
            parse_source("observe evidence;")

    def test_microorcim_still_rejected(self):
        with self.assertRaises(ParseError):
            parse_source("intent state;")


class OperatorContractTests(unittest.TestCase):
    def test_all_six_contracts_exist(self):
        self.assertEqual(set(OPERATOR_CONTRACTS), {"⊗", "→", "⇌", "⟲", "↯", "↗"})

    def test_contract_hash_deterministic(self):
        self.assertEqual(contract_hash("⊗"), contract_hash("⊗"))
        self.assertEqual(len(contract_hash("⊗")), 64)

    def test_fusion_commutative_proven(self):
        self.assertEqual(
            law_result("⊗", "commutative")["status"],
            LawStatus.PROVEN.value,
        )

    def test_fusion_associative_proven(self):
        self.assertEqual(
            law_result("⊗", "associative")["status"],
            LawStatus.PROVEN.value,
        )

    def test_fusion_idempotent_refuted(self):
        record = law_result("⊗", "idempotent")
        self.assertEqual(record["status"], LawStatus.REFUTED.value)
        self.assertIn("A ⊗ A", record["counterexample"])

    def test_projection_commutative_refuted(self):
        self.assertEqual(
            law_result("→", "commutative")["status"],
            LawStatus.REFUTED.value,
        )

    def test_projection_associative_proven(self):
        self.assertEqual(
            law_result("→", "associative")["status"],
            LawStatus.PROVEN.value,
        )

    def test_exchange_structural_inverse_self(self):
        record = law_result("⇌", "inverse")
        self.assertEqual(record["status"], LawStatus.PROVEN.value)
        self.assertEqual(record["value"], "SELF")

    def test_exchange_operational_reversibility_domain_dependent(self):
        self.assertEqual(
            law_result("⇌", "reversible")["status"],
            LawStatus.DOMAIN_DEPENDENT.value,
        )

    def test_recurrence_termination_domain_dependent(self):
        self.assertEqual(
            law_result("⟲", "terminating")["status"],
            LawStatus.DOMAIN_DEPENDENT.value,
        )

    def test_no_identity_declared(self):
        for symbol in OPERATOR_CONTRACTS:
            self.assertEqual(
                law_result(symbol, "identity")["status"],
                LawStatus.UNDECLARED.value,
            )

    def test_no_annihilator_declared(self):
        for symbol in OPERATOR_CONTRACTS:
            self.assertEqual(
                law_result(symbol, "annihilator")["status"],
                LawStatus.UNDECLARED.value,
            )

    def test_all_operator_pairs_structurally_composable(self):
        for first in OPERATOR_CONTRACTS:
            for second in OPERATOR_CONTRACTS:
                self.assertTrue(
                    structurally_composable(first, second)[
                        "structurally_composable"
                    ]
                )

    def test_composition_matrix_has_36_cells(self):
        matrix = composition_matrix()
        count = sum(len(row) for row in matrix["cells"].values())
        self.assertEqual(count, 36)

    def test_contract_export_json_serializable(self):
        json.dumps(contracts_export(), ensure_ascii=False)


class OperatorSyntaxTests(unittest.TestCase):
    def test_describe_operator(self):
        _, _, result = run_source("describe operator ⊗;")
        record = result["descriptions"][0]
        self.assertEqual(record["kind"], "operator_contract")
        self.assertEqual(record["symbol"], "⊗")

    def test_check_law(self):
        _, _, result = run_source("check law(⊗, commutative);")
        record = result["checks"][0]
        self.assertEqual(record["status"], "PROVEN")

    def test_check_undeclared_law(self):
        _, _, result = run_source("check law(↯, identity);")
        self.assertEqual(result["checks"][0]["status"], "UNDECLARED")

    def test_check_domain_dependent_law(self):
        _, _, result = run_source("check law(⟲, terminating);")
        self.assertEqual(result["checks"][0]["status"], "DOMAIN_DEPENDENT")

    def test_check_composition(self):
        _, _, result = run_source("check composition(↯, ⟲);")
        record = result["checks"][0]
        self.assertTrue(record["structurally_composable"])
        self.assertEqual(record["semantic_legality"], "DOMAIN_DEPENDENT")

    def test_unknown_law_rejected(self):
        with self.assertRaises(SemanticError):
            run_source("check law(⊗, magical);")

    def test_describe_requires_operator(self):
        with self.assertRaises(ParseError):
            parse_source("describe operator Ao;")


class RewriteTraceTests(unittest.TestCase):
    def test_fusion_sort_trace(self):
        _, _, result = run_source("describe Ψ ⊗ Ao;")
        rules = [x["rule"] for x in result["descriptions"][0]["rewrite_trace"]]
        self.assertIn("FUSION_COMMUTATIVE_SORT", rules)

    def test_fusion_flatten_trace(self):
        _, _, result = run_source("describe (Ao ⊗ Φ) ⊗ Ψ;")
        rules = [x["rule"] for x in result["descriptions"][0]["rewrite_trace"]]
        self.assertIn("FUSION_ASSOCIATIVE_FLATTEN", rules)

    def test_projection_flatten_trace(self):
        _, _, result = run_source("describe (Ao → Φ) → Ψ;")
        rules = [x["rule"] for x in result["descriptions"][0]["rewrite_trace"]]
        self.assertIn("PROJECTION_ASSOCIATIVE_FLATTEN", rules)

    def test_exchange_order_trace(self):
        _, _, result = run_source("describe Ψ ⇌ Ao;")
        rules = [x["rule"] for x in result["descriptions"][0]["rewrite_trace"]]
        self.assertIn("EXCHANGE_SYMMETRIC_ORDER", rules)

    def test_directed_operator_has_no_reorder_trace(self):
        _, _, result = run_source("describe Ψ ↯ Ao;")
        rules = [x["rule"] for x in result["descriptions"][0]["rewrite_trace"]]
        self.assertNotIn("EXCHANGE_SYMMETRIC_ORDER", rules)
        self.assertNotIn("FUSION_COMMUTATIVE_SORT", rules)

    def test_derived_atom_trace(self):
        _, _, result = run_source("describe Φ↑;")
        rules = [x["rule"] for x in result["descriptions"][0]["rewrite_trace"]]
        self.assertIn("DERIVED_ATOM_DECOMPOSITION", rules)

    def test_reference_expansion_trace(self):
        _, _, result = run_source("let x = Ao → Φ; describe x;")
        rules = [x["rule"] for x in result["descriptions"][0]["rewrite_trace"]]
        self.assertIn("REFERENCE_EXPANSION", rules)

    def test_equivalence_reports_traces(self):
        _, _, result = run_source(
            "check equivalent(Ψ ⊗ Ao, Ao ⊗ Ψ);"
        )
        record = result["checks"][0]
        self.assertEqual(record["method"], "canonical_normal_form")
        self.assertIn("left_rewrite_trace", record)
        self.assertIn("right_rewrite_trace", record)


class ContractBoundaryTests(unittest.TestCase):
    def test_null_not_simplified_after_collapse(self):
        _, _, result = run_source("Ψ ↯ ∅;")
        self.assertEqual(result["expressions"][0], "(Ψ ↯ ∅)")

    def test_fixed_point_not_identity(self):
        self.assertEqual(
            law_result("⊗", "identity")["status"],
            LawStatus.UNDECLARED.value,
        )
        _, _, result = run_source("check equivalent(Ao ⊗ ⟟, Ao);")
        self.assertFalse(result["checks"][0]["equivalent"])

    def test_null_not_annihilator(self):
        _, _, result = run_source("check equivalent(Ao ⊗ ∅, ∅);")
        self.assertFalse(result["checks"][0]["equivalent"])

    def test_ascent_does_not_normalize_direction(self):
        _, _, result = run_source(
            "check equivalent(Ao ↗ Φ, Φ ↗ Ao);"
        )
        self.assertFalse(result["checks"][0]["equivalent"])

    def test_collapse_grouping_preserved(self):
        _, _, result = run_source(
            "check equivalent((Ao ↯ Φ) ↯ Ψ, Ao ↯ (Φ ↯ Ψ));"
        )
        self.assertFalse(result["checks"][0]["equivalent"])

    def test_recurrence_grouping_preserved(self):
        _, _, result = run_source(
            "check equivalent((Ao ⟲ Φ) ⟲ Ψ, Ao ⟲ (Φ ⟲ Ψ));"
        )
        self.assertFalse(result["checks"][0]["equivalent"])

    def test_result_contract_lock(self):
        _, _, result = run_source("Ao;")
        lock = result["operator_contract_lock"]
        self.assertFalse(lock["identity_elements_declared"])
        self.assertTrue(
            lock[
                "structural_inverse_separated_from_operational_reversibility"
            ]
        )


if __name__ == "__main__":
    unittest.main()
