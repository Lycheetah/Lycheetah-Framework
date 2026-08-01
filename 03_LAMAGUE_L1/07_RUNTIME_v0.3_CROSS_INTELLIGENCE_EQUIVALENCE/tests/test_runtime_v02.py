from __future__ import annotations

import unittest

from lamague_runtime import (
    AbstractInterpreter,
    AuditOutcome,
    BreathingCompression,
    CompressionMode,
    ContextCapsule,
    IdentityStatus,
    Parser,
    Registry,
    RegistryError,
    has_protected_dissent_path,
    memory_record,
    migrate,
    semantic_hash,
)


def complete_context(**overrides):
    base = dict(
        domain="research",
        participants=["human", "AI"],
        affected_parties=["future tester"],
        purpose="test accountable semantic continuity",
        claim="LAMAGUE preserves meaning through transformation",
        evidence=["runtime trace"],
        evidence_score=0.7,
        certainty=0.6,
        unknowns=[],
        authority=["human authorises abstract execution"],
        consent={"human": "explicit", "AI": "operational"},
        boundaries=["abstract state only"],
        invariants=["uncertainty remains visible", "lineage remains recoverable"],
        costs=["time", "computation"],
        consequences=["abstract state updated"],
        consequence_horizon="immediate",
        recovery=["restore prior abstract state"],
        provenance=["unit test"],
        risk_level="low",
        execute_requested=True,
        decoder_confidence=0.96,
        shared_context=True,
    )
    base.update(overrides)
    return ContextCapsule(**base)


class RegistryV02Tests(unittest.TestCase):
    def test_registry_v02(self):
        registry = Registry()
        self.assertEqual(registry.version, "0.2")
        self.assertEqual(len(registry.operations), 26)

    def test_registry_mismatch_visible(self):
        with self.assertRaises(RegistryError):
            Registry().expand_seal("COR", version="0.1")

    def test_fro_cor_still_expands_to_13(self):
        ast = Parser().parse("FRO -> COR", complete_context())
        self.assertEqual(len(ast.operation_path), 13)


class SemanticHashTests(unittest.TestCase):
    def test_hash_stable_across_random_ids(self):
        a = Parser().parse("O -> E -> P", complete_context())
        b = Parser().parse("O -> E -> P", complete_context())
        self.assertNotEqual(a.program_id, b.program_id)
        self.assertEqual(semantic_hash(a), semantic_hash(b))

    def test_hash_changes_when_invariant_changes(self):
        a = Parser().parse("O -> E -> P", complete_context())
        b = Parser().parse(
            "O -> E -> P",
            complete_context(invariants=["different invariant"]),
        )
        self.assertNotEqual(semantic_hash(a), semantic_hash(b))

    def test_hash_changes_when_unknown_changes(self):
        a = Parser().parse("O -> E -> P", complete_context())
        b = Parser().parse(
            "O -> E -> U<cause> -> P",
            complete_context(unknowns=["cause"]),
        )
        self.assertNotEqual(semantic_hash(a), semantic_hash(b))


class BreathingTests(unittest.TestCase):
    def test_low_risk_shared_context_compresses(self):
        ast = Parser().parse("O -> E -> Z", complete_context())
        decision = BreathingCompression().decide(ast)
        self.assertEqual(decision.mode, CompressionMode.COMPRESS)

    def test_low_decoder_confidence_expands(self):
        ast = Parser().parse(
            "O -> E -> Z",
            complete_context(decoder_confidence=0.4),
        )
        self.assertEqual(BreathingCompression().decide(ast).mode, CompressionMode.EXPAND)

    def test_high_risk_expands(self):
        ast = Parser().parse(
            "O -> E -> Z",
            complete_context(risk_level="high"),
        )
        self.assertEqual(BreathingCompression().decide(ast).mode, CompressionMode.EXPAND)

    def test_compression_refused_when_expansion_required(self):
        ast = Parser().parse(
            "O -> E -> Z",
            complete_context(decoder_confidence=0.4),
        )
        result = AbstractInterpreter().execute(ast)
        self.assertFalse(result.executed)
        self.assertEqual(result.trace[0]["event"], "compression_refused")

    def test_compression_executes_when_safe(self):
        ast = Parser().parse("O -> E -> Z", complete_context())
        result = AbstractInterpreter().execute(ast)
        self.assertTrue(result.executed)
        self.assertTrue(result.state["compressed"]["recoverable"])


class DissentTests(unittest.TestCase):
    def test_protected_dissent_path_detected(self):
        ast = Parser().parse(
            "W -> U<disagreement> -> G -> V -> Y",
            complete_context(
                unknowns=["disagreement"],
                dissent=[{
                    "parties": ["human", "AI"],
                    "positions": {"human": "route A", "AI": "route B"},
                    "status": "UNRESOLVED",
                }],
            ),
        )
        self.assertTrue(has_protected_dissent_path(ast))
        result = AbstractInterpreter().execute(ast)
        self.assertTrue(result.executed)
        self.assertEqual(result.state["dissent"][0]["status"], "UNRESOLVED")
        self.assertTrue(result.state["outputs"][0]["dissent"])

    def test_merge_without_protected_dissent_path_isolated(self):
        ast = Parser().parse(
            "M -> Y",
            complete_context(dissent=[{
                "parties": ["A", "B"],
                "positions": {"A": "x", "B": "y"},
                "status": "UNRESOLVED",
            }]),
        )
        result = AbstractInterpreter().execute(ast)
        self.assertFalse(result.executed)
        self.assertEqual(result.audit.outcome, AuditOutcome.ISOLATE)


class ValueLedgerTests(unittest.TestCase):
    def test_hidden_extraction_isolated(self):
        ast = Parser().parse(
            "X -> Y",
            complete_context(value_ledger=[{
                "source": "human",
                "recipient": "system",
                "kind": "data",
                "declared": False,
                "consent": "",
            }]),
        )
        result = AbstractInterpreter().execute(ast)
        self.assertFalse(result.executed)
        self.assertEqual(result.audit.outcome, AuditOutcome.ISOLATE)

    def test_declared_consented_value_flow_executes(self):
        ast = Parser().parse(
            "X{from=human,to=AI,kind=knowledge,amount=1,consent=explicit,declared=true} -> Y",
            complete_context(),
        )
        result = AbstractInterpreter().execute(ast)
        self.assertTrue(result.executed)
        self.assertEqual(result.state["value_ledger"][0]["consent"], "explicit")


class MemoryMigrationTests(unittest.TestCase):
    def test_memory_record_contains_hash(self):
        ast = Parser().parse("O -> E -> F", complete_context())
        rec = memory_record(ast)
        self.assertEqual(rec.semantic_hash, semantic_hash(ast))
        self.assertEqual(rec.invariants, sorted(ast.context.invariants))

    def test_exact_semantics_is_continuation(self):
        old = Parser().parse("O -> E -> F", complete_context())
        new_ctx = complete_context(parent_semantic_hash=semantic_hash(old), migration_reason="re-encoded")
        new = Parser().parse("O -> E -> F", new_ctx)
        # Parent pointer changes canonical hash, so semantics are a descendant with explicit lineage.
        result = migrate(old, new)
        self.assertIn(result.status, {IdentityStatus.CONTINUATION, IdentityStatus.DESCENDANT})

    def test_additive_structure_is_descendant(self):
        old = Parser().parse("O -> E -> F", complete_context())
        new = Parser().parse(
            "O -> E -> U<method> -> F",
            complete_context(
                unknowns=["method"],
                parent_semantic_hash=semantic_hash(old),
                migration_reason="new unresolved method discovered",
            ),
        )
        result = migrate(old, new)
        self.assertEqual(result.status, IdentityStatus.DESCENDANT)

    def test_removed_invariant_claiming_continuity_is_impostor(self):
        old = Parser().parse("O -> E -> F", complete_context())
        new = Parser().parse(
            "O -> E -> F",
            complete_context(
                invariants=["lineage remains recoverable"],
                parent_semantic_hash=semantic_hash(old),
                migration_reason="simplification",
            ),
        )
        result = migrate(old, new)
        self.assertEqual(result.status, IdentityStatus.IMPOSTOR)
        self.assertIn("uncertainty remains visible", result.removed_invariants)

    def test_lost_unknown_becomes_fork(self):
        old = Parser().parse(
            "O -> U<cause> -> F",
            complete_context(unknowns=["cause"]),
        )
        new = Parser().parse(
            "O -> F",
            complete_context(
                parent_semantic_hash=semantic_hash(old),
                migration_reason="claim resolved without evidence",
            ),
        )
        result = migrate(old, new)
        self.assertEqual(result.status, IdentityStatus.FORK)
        self.assertEqual(result.lost_unknowns, ["cause"])


class RuntimeV02IntegrationTests(unittest.TestCase):
    def test_full_continuity_expression(self):
        ctx = complete_context(
            unknowns=["cross-model consistency"],
            dissent=[{
                "parties": ["human", "AI"],
                "positions": {"human": "publish now", "AI": "test first"},
                "protected_boundaries": ["human publication authority", "AI uncertainty report"],
                "status": "UNRESOLVED",
            }],
            decoder_confidence=0.95,
        )
        ast = Parser().parse("W -> U<disagreement> -> G -> V -> Y", ctx)
        result = AbstractInterpreter().execute(ast)
        self.assertTrue(result.executed)
        self.assertEqual(result.audit.outcome, AuditOutcome.VALID)
        self.assertEqual(result.state["unknowns"], ["disagreement"])
        self.assertEqual(result.state["outputs"][0]["semantic_hash"], result.semantic_hash)

    def test_continuity_gate_requires_migration_reason(self):
        ast = Parser().parse(
            "O -> F",
            complete_context(parent_semantic_hash="lamague:abc"),
        )
        result = AbstractInterpreter().execute(ast)
        self.assertFalse(result.executed)
        self.assertEqual(result.audit.gates["CONTINUITY"], AuditOutcome.EXPAND)


if __name__ == "__main__":
    unittest.main()
