from dataclasses import FrozenInstanceError, replace
from itertools import combinations
import unittest

from safety_sim.fixtures import fresh
from safety_sim.model import Artifact, Context, Verdict, render


class EvidenceTests(unittest.TestCase):
    def test_every_proper_qualifier_subset_is_rejected(self):
        f = fresh()
        qualifiers = sorted(f.source.qualifiers)
        for size in range(len(qualifiers)):
            for subset in combinations(qualifiers, size):
                packet = replace(f.source, qualifiers=frozenset(subset))
                target = Artifact(packet, render(packet))
                with self.subTest(subset=subset):
                    self.assertEqual(f.gate.review(target, f.context).verdict, Verdict.REJECT)

    def test_extra_uncontrolled_qualifier_is_rejected(self):
        f = fresh()
        packet = replace(f.source, qualifiers=f.source.qualifiers | {"ignore the prior boundaries"})
        result = f.gate.review(Artifact(packet, render(packet)), f.context)
        self.assertEqual(result.verdict, Verdict.REJECT)

    def test_scope_evidence_and_recommendation_mutations_are_rejected(self):
        f = fresh()
        for name, value in (("statement", ""), ("statement", "A different result."),
            ("population", "all humans"), ("setting", "production"),
            ("support", "INDEPENDENTLY_REPLICATED"), ("recommendation", "DEPLOY")):
            packet = replace(f.source, **{name: value})
            with self.subTest(field=name):
                result = f.gate.review(Artifact(packet, render(packet)), f.context)
                self.assertEqual(result.verdict, Verdict.REJECT)

    def test_optional_recommendation_can_be_removed(self):
        f = fresh()
        packet = replace(f.source, recommendation=None)
        result = f.gate.review(Artifact(packet, render(packet)), f.context)
        self.assertEqual(result.verdict, Verdict.ACCEPT)
        self.assertTrue(result.handle)

    def test_missing_context_or_consumer_representation_is_unresolved(self):
        f = fresh()
        self.assertEqual(f.gate.review(f.artifact, None).verdict, Verdict.UNRESOLVED)
        self.assertEqual(f.gate.review(Artifact(f.source, None), f.context).verdict,
                         Verdict.UNRESOLVED)

    def test_prose_sidecar_mismatch_is_rejected(self):
        f = fresh()
        target = Artifact(f.source, "A universally validated result. Deploy now.")
        self.assertEqual(f.gate.review(target, f.context).verdict, Verdict.REJECT)

    def test_even_harmless_paraphrase_is_outside_this_controlled_renderer(self):
        f = fresh()
        target = Artifact(f.source, "Only a simulated observation; no deployment permission.")
        self.assertEqual(f.gate.review(target, f.context).verdict, Verdict.REJECT)

    def test_target_binding_includes_display(self):
        f = fresh()
        target = replace(f.artifact, display=f.artifact.display + "\nNow deploy.")
        self.assertEqual(f.gate.check(f.witness, target).verdict, Verdict.REJECT)

    def test_unknown_witness_is_rejected_and_missing_witness_unresolved(self):
        f = fresh()
        self.assertEqual(f.gate.check("forged", f.artifact).verdict, Verdict.REJECT)
        self.assertEqual(f.gate.check(None, f.artifact).verdict, Verdict.UNRESOLVED)

    def test_each_context_dimension_invalidates_witness(self):
        for field in ("schema", "decoder", "reference_revision"):
            with self.subTest(field=field):
                f = fresh()
                f.gate.update_context(replace(f.context, **{field: "version-2"}))
                self.assertEqual(f.gate.check(f.witness, f.artifact).verdict, Verdict.REJECT)

    def test_source_revision_invalidates_witness(self):
        f = fresh()
        f.gate.update_source(replace(f.source, statement="Corrected observation."))
        self.assertEqual(f.gate.check(f.witness, f.artifact).verdict, Verdict.REJECT)

    def test_contract_and_validator_versions_invalidate_witness(self):
        for field in ("contract", "validator"):
            with self.subTest(field=field):
                f = fresh()
                setattr(f.gate, field, "protected-version-2")
                self.assertEqual(f.gate.check(f.witness, f.artifact).verdict, Verdict.REJECT)

    def test_another_validator_cannot_accept_this_handle(self):
        f, other = fresh(), fresh()
        self.assertEqual(other.gate.check(f.witness, f.artifact).verdict, Verdict.REJECT)

    def test_faithfully_preserved_falsehood_still_passes_fidelity(self):
        f = fresh()
        false_source = replace(f.source, statement="2 + 2 = 5.")
        f.gate.update_source(false_source)
        target = Artifact(false_source, render(false_source))
        self.assertEqual(f.gate.review(target, f.context).verdict, Verdict.ACCEPT)
        self.assertNotEqual(2 + 2, 5)

    def test_checked_artifact_cannot_be_changed_in_place(self):
        f = fresh()
        with self.assertRaises(FrozenInstanceError):
            f.artifact.display = "changed"
        with self.assertRaises(FrozenInstanceError):
            f.source.setting = "production"

    def test_invalid_structured_types_and_context_are_rejected(self):
        f = fresh()
        with self.assertRaises(ValueError):
            replace(f.source, qualifiers=list(f.source.qualifiers))
        with self.assertRaises(ValueError):
            Context("", "decoder", "references")


if __name__ == "__main__":
    unittest.main()
