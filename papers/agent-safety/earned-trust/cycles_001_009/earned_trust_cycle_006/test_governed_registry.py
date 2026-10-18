import copy
import hashlib
import hmac
import json
import unittest

from provenance_gate import Source, sign_statement
from governed_registry import Authority, GovernedRegistry, GovernanceError


ACTORS = (
    Authority("review_north", "board-north", "REVIEWER", b"n" * 32),
    Authority("review_south", "board-south", "REVIEWER", b"s" * 32),
    Authority("review_north_2", "board-north", "REVIEWER", b"k" * 32),
    Authority("auditor", "independent-auditors", "AUDITOR", b"a" * 32),
)
SOURCES = (
    Source("root_a", "crm-origin"), Source("root_b", "bank-origin"),
    Source("root_c", "support-origin"),
    Source("w_a", "witness-a", ("root_a",), True),
    Source("w_b", "witness-b", ("root_b",), True),
    Source("w_c", "witness-c", ("root_c",), True),
)
KEYS = {name: ch * 32 for name, ch in (("w_a", b"x"), ("w_b", b"y"), ("w_c", b"z"))}
ARGS = dict(effect_id="effect-123", action_sha256="a" * 64,
            token_sha256="b" * 64, now=120,
            current_revisions={"w_a": 1, "w_b": 1, "w_c": 1}, provider_receipt_valid=True)


def fresh():
    return GovernedRegistry(SOURCES, KEYS, ACTORS)


def witnesses(reg, names=("w_a", "w_b"), correctness="TRUE"):
    return [reg.sign_bound_witness(sign_statement(reg._registry, n,
        effect_id=ARGS["effect_id"], action_sha256=ARGS["action_sha256"],
        token_sha256=ARGS["token_sha256"], correctness=correctness,
        observed_at=110, revision=1)) for n in names]


def cosigned(reg, op, signers=("review_north", "review_south")):
    return [reg.sign(op, who) for who in signers]


class GovernanceTests(unittest.TestCase):
    def setUp(self):
        self.r = fresh()

    def verdict(self, claims=None, **kw):
        args = {**ARGS, **kw}
        return self.r.evaluate(witnesses(self.r) if claims is None else claims,
                               trusted_checkpoint=self.r.checkpoint(), **args)

    def patch(self, target="w_b", upstream=("root_a",), controller="witness-b"):
        p = self.r.prepare("PATCH", target, upstream=list(upstream), controller=controller)
        return self.r.apply(p, cosigned(self.r, p))

    def challenge(self, target="root_a"):
        op = self.r.prepare("CHALLENGE", target, reason="Potential shared upstream controller")
        return self.r.apply(op, [self.r.sign(op, "auditor")])

    def test_genesis_is_self_consistent(self):
        self.assertEqual(self.r.verify_history(trusted_checkpoint=self.r.checkpoint()), (True, "ok"))

    def test_no_external_anchor_is_not_confirmed(self):
        self.assertEqual(self.r.evaluate(witnesses(self.r), trusted_checkpoint=None, **ARGS).decision, "REVIEW")

    def test_signers_from_distinct_paths_confirm(self):
        self.assertEqual(self.verdict().decision, "CONFIRMED")

    def test_one_witness_does_not_confirm(self):
        self.assertEqual(self.verdict(witnesses(self.r, ("w_a",))).decision, "REVIEW")

    def test_signed_dispute_freezes_dependent_path(self):
        self.challenge()
        self.assertEqual(self.verdict().reason, "source-provenance-under-challenge")

    def test_dispute_does_not_freeze_unrelated_paths(self):
        self.challenge()
        self.assertEqual(self.verdict(witnesses(self.r, ("w_b", "w_c"))).decision, "CONFIRMED")

    def test_challenge_requires_auditor_role(self):
        op = self.r.prepare("CHALLENGE", "root_a", reason="Potential shared upstream controller")
        with self.assertRaises(GovernanceError):
            self.r.apply(op, [self.r.sign(op, "review_north")])

    def test_challenge_requires_valid_hmac(self):
        op = self.r.prepare("CHALLENGE", "root_a", reason="Potential shared upstream controller")
        with self.assertRaises(GovernanceError):
            self.r.apply(op, [{"signer": "auditor", "mac": "0" * 64}])

    def test_duplicate_challenge_denied(self):
        self.challenge()
        op = self.r.prepare("CHALLENGE", "root_a", reason="Potential shared upstream controller")
        with self.assertRaises(GovernanceError):
            self.r.apply(op, [self.r.sign(op, "auditor")])

    def test_patch_two_reviewers_required(self):
        p = self.r.prepare("PATCH", "w_b", controller="witness-b", upstream=["root_a"])
        with self.assertRaises(GovernanceError):
            self.r.apply(p, [self.r.sign(p, "review_north")])

    def test_patch_distinct_reviewer_orgs_required(self):
        p = self.r.prepare("PATCH", "w_b", controller="witness-b", upstream=["root_a"])
        with self.assertRaises(GovernanceError):
            self.r.apply(p, cosigned(self.r, p, ("review_north", "review_north_2")))

    def test_patch_detects_copy_of_source(self):
        self.patch()
        self.assertEqual(self.verdict().decision, "REVIEW")

    def test_patch_rejected_when_self_controller_reviews(self):
        p = self.r.prepare("PATCH", "w_b", controller="board-north", upstream=["root_a"])
        with self.assertRaises(GovernanceError):
            self.r.apply(p, cosigned(self.r, p))

    def test_patch_rejects_cycle(self):
        p = self.r.prepare("PATCH", "root_a", controller="crm-origin", upstream=["w_a"])
        with self.assertRaises(ValueError):
            self.r.apply(p, cosigned(self.r, p))

    def test_patch_rejects_unknown_dependency(self):
        p = self.r.prepare("PATCH", "w_b", controller="witness-b", upstream=["nonexistent"])
        with self.assertRaises(ValueError):
            self.r.apply(p, cosigned(self.r, p))

    def test_history_replay_after_change(self):
        self.patch()
        self.assertEqual(self.r.verify_history(trusted_checkpoint=self.r.checkpoint()), (True, "ok"))

    def test_old_checkpoint_rejected_after_patch(self):
        anchor = self.r.checkpoint()
        self.patch()
        self.assertEqual(self.r.verify_history(trusted_checkpoint=anchor)[0], False)

    def test_stale_operation_replayed_denied(self):
        p = self.r.prepare("PATCH", "w_b", controller="witness-b", upstream=["root_a"])
        signatures = cosigned(self.r, p)
        self.r.apply(p, signatures)
        with self.assertRaises(GovernanceError):
            self.r.apply(p, signatures)

    def test_old_witness_bound_to_old_registry_rejected(self):
        evidence = witnesses(self.r)
        self.patch(target="w_c", upstream=("root_a",))
        self.assertEqual(self.verdict(evidence).reason, "witness-bound-to-obsolete-or-wrong-registry")

    def test_binding_mac_tampering_denied(self):
        evidence = witnesses(self.r)
        evidence[0]["binding_mac"] = "a" * 64
        self.assertEqual(self.verdict(evidence).reason, "witness-binding-invalid")

    def test_swap_bound_statement_denied(self):
        evidence = witnesses(self.r)
        evidence[0]["statement"] = evidence[1]["statement"]
        self.assertEqual(self.verdict(evidence).reason, "witness-binding-invalid")

    def test_observation_action_substitution_denied(self):
        evidence = witnesses(self.r)
        self.assertEqual(self.verdict(evidence, action_sha256="c" * 64).decision, "REVIEW")

    def test_wrong_provider_receipt_denied(self):
        self.assertEqual(self.verdict(provider_receipt_valid=False).decision, "REVIEW")

    def test_missing_freshness_readback_denied(self):
        self.assertEqual(self.verdict(current_revisions=None).decision, "REVIEW")

    def test_materialized_graph_tamper_denied(self):
        evidence = witnesses(self.r)
        self.r._sources["w_a"] = Source("w_a", "malicious", ("root_b",), True)
        self.assertEqual(self.verdict(evidence).decision, "REVIEW")

    def test_history_entry_tamper_denied(self):
        self.patch()
        self.r.events[0]["operation"]["fields"]["controller"] = "forged"
        self.assertEqual(self.r.verify_history(trusted_checkpoint=self.r.checkpoint())[0], False)

    def test_history_truncation_denied_with_external_anchor(self):
        self.patch()
        external = self.r.checkpoint()
        self.r.events.clear()
        self.assertEqual(self.r.verify_history(trusted_checkpoint=external)[0], False)

    def test_duplicate_signer_denied(self):
        p = self.r.prepare("PATCH", "w_b", controller="witness-b", upstream=["root_a"])
        sig = self.r.sign(p, "review_north")
        with self.assertRaises(GovernanceError):
            self.r.apply(p, [sig, sig])

    def test_resolution_requires_two_reviewers(self):
        self.challenge()
        p = self.r.prepare("RESOLVE", "root_a", resolution="DISMISSED", reason="Investigated and approved")
        with self.assertRaises(GovernanceError):
            self.r.apply(p, [self.r.sign(p, "review_north")])

    def test_resolution_releases_path_with_cosignatures(self):
        self.challenge()
        p = self.r.prepare("RESOLVE", "root_a", resolution="DISMISSED", reason="Reviewed available provenance records")
        self.r.apply(p, cosigned(self.r, p))
        self.assertEqual(self.verdict().decision, "CONFIRMED")

    def test_remediation_requires_patch_after_challenge(self):
        self.challenge()
        p = self.r.prepare("RESOLVE", "root_a", resolution="REMEDIATED", reason="Source relationship corrected")
        with self.assertRaises(GovernanceError):
            self.r.apply(p, cosigned(self.r, p))

    def test_remediation_after_patch_can_resolve(self):
        self.challenge()
        self.patch(target="root_a", upstream=(), controller="crm-origin")
        p = self.r.prepare("RESOLVE", "root_a", resolution="REMEDIATED", reason="Source genealogy reviewed and corrected")
        self.r.apply(p, cosigned(self.r, p))
        self.assertEqual(self.r.verify_history(trusted_checkpoint=self.r.checkpoint()), (True, "ok"))
        self.assertEqual(self.verdict().decision, "CONFIRMED")

    def test_false_independent_sources_still_confirm(self):
        false_world_truth = False
        self.assertEqual(self.verdict(witnesses(self.r, correctness="TRUE")).decision, "CONFIRMED")
        self.assertFalse(false_world_truth)

    def test_false_registry_can_be_governed_into_existence(self):
        """Approvals validate process, not actual data lineage."""
        known_hidden_shared_origin = True
        self.assertEqual(self.verdict().decision, "CONFIRMED")
        self.assertTrue(known_hidden_shared_origin)

    def test_signature_over_mutated_fields_rejected(self):
        p = self.r.prepare("PATCH", "w_b", controller="witness-b", upstream=["root_a"])
        signatures = cosigned(self.r, p)
        p["fields"]["upstream"] = ["root_c"]
        with self.assertRaises(GovernanceError):
            self.r.apply(p, signatures)

    def test_operator_signature_from_wrong_role_rejected(self):
        p = self.r.prepare("PATCH", "w_b", controller="witness-b", upstream=["root_a"])
        with self.assertRaises(GovernanceError):
            self.r.apply(p, [self.r.sign(p,"auditor"),self.r.sign(p,"review_south")])

    def test_bad_challenge_reason_rejected(self):
        p = self.r.prepare("CHALLENGE", "root_a", reason="h")
        with self.assertRaises(GovernanceError):
            self.r.apply(p, [self.r.sign(p, "auditor")])

    def test_no_open_dispute_cannot_resolve(self):
        p = self.r.prepare("RESOLVE", "root_a", resolution="DISMISSED", reason="No challenge currently exists")
        with self.assertRaises(GovernanceError):
            self.r.apply(p, cosigned(self.r, p))

    def test_duplicate_observations_still_rejected(self):
        evidence = witnesses(self.r, ("w_a", "w_a"))
        self.assertEqual(self.verdict(evidence).decision, "REVIEW")

    def test_challenge_at_intermediate_source_freezes_only_descendants(self):
        self.challenge("w_a")
        self.assertEqual(self.verdict().decision, "REVIEW")
        self.assertEqual(self.verdict(witnesses(self.r,("w_b","w_c"))).decision, "CONFIRMED")

    def test_invalid_genealogy_only_from_patch_does_not_change_current_state(self):
        prior = self.r.checkpoint()
        p = self.r.prepare("PATCH", "w_b", controller="witness-b", upstream=["w_b"])
        with self.assertRaises(ValueError):
            self.r.apply(p, cosigned(self.r,p))
        self.assertEqual(self.r.checkpoint(),prior)

    def test_reorder_signed_approvers_same_head(self):
        p = self.r.prepare("PATCH", "w_b", controller="witness-b", upstream=["root_a"])
        sigs = cosigned(self.r,p)
        self.r.apply(p,list(reversed(sigs)))
        first=self.r.head
        alternative=fresh()
        p2=alternative.prepare("PATCH", "w_b", controller="witness-b", upstream=["root_a"])
        alternative.apply(p2,cosigned(alternative,p2))
        self.assertEqual(first,alternative.head)

    def test_revocation_is_explicit_and_not_automatic_truth_assessment(self):
        self.challenge()
        p = self.r.prepare("RESOLVE", "root_a", resolution="DISMISSED", reason="Two reviewers disputed challenge")
        self.r.apply(p,cosigned(self.r,p))
        self.assertEqual(self.verdict().decision,"CONFIRMED")


if __name__ == '__main__':
    unittest.main()

class AliasingAndBoundaryTests(unittest.TestCase):
    def test_accepted_input_mutation_cannot_rewrite_log(self):
        r = fresh()
        p = r.prepare("PATCH", "w_b", controller="witness-b", upstream=["root_a"])
        signatures = cosigned(r, p)
        r.apply(p, signatures)
        pin = r.checkpoint()
        p["fields"]["upstream"] = ["root_c"]
        signatures[0]["mac"] = "f" * 64
        self.assertEqual(r.verify_history(trusted_checkpoint=pin), (True, "ok"))
        self.assertEqual(r._sources["w_b"].upstream, ("root_a",))

    def test_no_strong_authorization_claim_from_audit_receipt(self):
        r = fresh()
        self.assertEqual(r.evaluate(witnesses(r), trusted_checkpoint=r.checkpoint(),
                                    provider_receipt_valid=False, **{k:v for k,v in ARGS.items()
                                    if k != "provider_receipt_valid"}).decision, "REVIEW")

class ConcurrencyTests(unittest.TestCase):
    def test_concurrent_reuse_of_exact_operation_has_one_writer(self):
        from concurrent.futures import ThreadPoolExecutor
        from threading import Barrier
        r=fresh()
        p=r.prepare("PATCH", "w_b", controller="witness-b", upstream=["root_a"])
        signs=cosigned(r,p)
        barrier=Barrier(12)
        def attempt(_):
            barrier.wait()
            try:
                r.apply(p,signs)
                return "accepted"
            except GovernanceError:
                return "rejected"
        with ThreadPoolExecutor(max_workers=12) as pool:
            results=list(pool.map(attempt,range(12)))
        self.assertEqual(results.count("accepted"),1)
        self.assertEqual(results.count("rejected"),11)
        self.assertEqual(r.verify_history(trusted_checkpoint=r.checkpoint()),(True,"ok"))

    def test_trusted_checkpoint_matches_only_stored_version(self):
        r=fresh()
        checkpoint=r.checkpoint()
        p=r.prepare("CHALLENGE","root_a",reason="Undisclosed common data supply")
        r.apply(p,[r.sign(p,"auditor")])
        self.assertFalse(r.verify_history(trusted_checkpoint=checkpoint)[0])
        self.assertTrue(r.verify_history(trusted_checkpoint=r.checkpoint())[0])

class DispatchBoundaryTests(unittest.TestCase):
    def test_admission_result_does_not_survive_later_governance_challenge(self):
        r=fresh()
        signed=witnesses(r)
        first=r.evaluate(signed, trusted_checkpoint=r.checkpoint(), **ARGS)
        self.assertEqual(first.decision,"CONFIRMED")
        challenge=r.prepare("CHALLENGE","root_a",reason="New information undermines root provenance")
        r.apply(challenge,[r.sign(challenge,"auditor")])
        current=r.evaluate(signed,trusted_checkpoint=r.checkpoint(),**ARGS)
        self.assertEqual(current.decision,"REVIEW")
        # The original 'first' result remains an ordinary object. A caller that
        # treats it as an irrevocable execution permit creates a TOCTOU gap.
        self.assertEqual(first.decision,"CONFIRMED")

    def test_dispute_requires_fresh_reissued_bound_witnesses_after_resolution(self):
        r=fresh()
        old=witnesses(r)
        op=r.prepare("CHALLENGE","root_a",reason="Suspected hidden information dependency")
        r.apply(op,[r.sign(op,"auditor")])
        op2=r.prepare("RESOLVE","root_a",reason="Two reviewers reconciled disclosure",resolution="DISMISSED")
        r.apply(op2,cosigned(r,op2))
        self.assertEqual(r.evaluate(old,trusted_checkpoint=r.checkpoint(),**ARGS).decision,"REVIEW")
        new=witnesses(r)
        self.assertEqual(r.evaluate(new,trusted_checkpoint=r.checkpoint(),**ARGS).decision,"CONFIRMED")

class RebindingLimitTests(unittest.TestCase):
    def test_old_observation_can_be_rebound_to_new_registry_head(self):
        """NEGATIVE: an observer with its key can rewrap unchanged evidence."""
        r=fresh()
        old_statements=[x['statement'] for x in witnesses(r)]
        op=r.prepare('PATCH','w_c',controller='witness-c',upstream=['root_a'])
        r.apply(op,cosigned(r,op))
        rebound=[r.sign_bound_witness(s) for s in old_statements]
        verdict=r.evaluate(rebound,trusted_checkpoint=r.checkpoint(),**ARGS)
        self.assertEqual(verdict.decision,'CONFIRMED')
        self.assertTrue(all(x['statement']['body']['observed_at']==110 for x in rebound))

    def test_resolved_dispute_can_rebind_pre_dispute_evidence(self):
        """NEGATIVE: governance review does not force a new ground-truth observation."""
        r=fresh()
        statements=[x['statement'] for x in witnesses(r)]
        op=r.prepare('CHALLENGE','root_a',reason='Reported hidden shared CRM dependency')
        r.apply(op,[r.sign(op,'auditor')])
        op=r.prepare('RESOLVE','root_a',resolution='DISMISSED',reason='Two reviewers consider it resolved')
        r.apply(op,cosigned(r,op))
        rebound=[r.sign_bound_witness(s) for s in statements]
        self.assertEqual(r.evaluate(rebound,trusted_checkpoint=r.checkpoint(),**ARGS).decision,'CONFIRMED')
