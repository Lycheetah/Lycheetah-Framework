"""Failure museum: executable demonstrations of claims this gateway CANNOT make.

These are tests of documented limitations: pass = limitation reproduced.
"""
import unittest
from hybrid_gateway import HybridGateway, SourceDocument, ClaimProposal, refund_window_quote_validator


class KnownFailureTests(unittest.TestCase):
    def test_quote_presence_does_not_prove_semantic_entailment(self):
        g = HybridGateway()
        src = SourceDocument("unrelated", "demo", "urn:fictional:loyalty",
                             "Customers earn 21 points. Refunds are allowed within 14 days.")
        g.register_source(src)
        p = ClaimProposal("incorrect-binding", "demo", "refunds", "window_days", "online", "21",
                          "2026-01-01T00:00:00Z", "unrelated", "Customers earn 21 points.")
        # A mistaken trusted reviewer can approve this misinterpretation. The
        # text-only anchor cannot protect against semantic role confusion.
        self.assertEqual(g.ingest(p, recorded_at="2026-01-02T00:00:00Z", reviewer_approved=True).disposition,
                         "ALLOW")
        q = g.query(tenant="demo", subject="refunds", predicate="window_days", scope="online",
                    effective_at="2026-01-03T00:00:00Z", known_at="2026-01-03T00:00:00Z")
        self.assertEqual(q.value, "21")  # deliberately incorrect versus source meaning

    def test_strict_domain_rule_recovers_from_known_misbinding(self):
        g = HybridGateway(semantic_validator=refund_window_quote_validator)
        s = SourceDocument("unrelated", "demo", "urn:fictional:loyalty",
                           "Customers earn 21 points. Refunds are allowed within 14 days.")
        g.register_source(s)
        p = ClaimProposal("incorrect-binding", "demo", "refunds", "window_days", "online", "21",
                          "2026-01-01T00:00:00Z", "unrelated", "Customers earn 21 points.")
        result = g.ingest(p, recorded_at="2026-01-02T00:00:00Z", reviewer_approved=True)
        self.assertEqual(result.disposition, "REVIEW")
        self.assertEqual(g.claims, {})

    def test_self_recomputed_chain_is_not_authentication(self):
        g = HybridGateway()
        s = SourceDocument("s", "demo", "urn:fictional:s", "Refunds allowed within 14 days.")
        g.register_source(s)
        p = ClaimProposal("id", "demo", "refunds", "window_days", "online", "14",
                          "2026-01-01T00:00:00Z", "s", s.body)
        g.ingest(p, recorded_at="2026-01-02T00:00:00Z", reviewer_approved=True)
        # A self-consistent chain without an independently saved head can't
        # authenticate who created the history. The chain alone is not a signature.
        self.assertTrue(g.verify_chain())
        self.assertFalse(g.verify_chain(anchored_head="sha256:" + "0" * 64))


if __name__ == "__main__":
    unittest.main()
