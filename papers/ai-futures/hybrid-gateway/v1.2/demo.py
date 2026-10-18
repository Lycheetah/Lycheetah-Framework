"""No network calls, no external effects. Run: python demo.py"""
from hybrid_gateway import HybridGateway, SourceDocument, ClaimProposal, ScriptedNeuralAdapter, refund_window_quote_validator

D = lambda month_day: f"2026-{month_day}T00:00:00Z"

g = HybridGateway(semantic_validator=refund_window_quote_validator)
for sid, num in [("official-v1", 14), ("official-v2", 21)]:
    source = SourceDocument(sid, "fictional-merchant", f"urn:demo:{sid}",
                            f"Refunds allowed within {num} days.")
    g.register_source(source)
    proposal = ClaimProposal(sid, "fictional-merchant", "refunds", "window_days",
                             "NZ-online", str(num), D("01-01" if num == 14 else "02-01"),
                             sid, source.body,
                             supersedes=("official-v1",) if num == 21 else ())
    adapter = ScriptedNeuralAdapter(f"mock-provider-{num}", {sid: [proposal]})
    candidate = adapter.extract(source)[0]
    observed = D("01-02" if num == 14 else "02-10")
    print(f"Neural candidate [{adapter.name}]:", candidate.claim_id)
    print("Admission before review:", g.ingest(candidate, recorded_at=observed).disposition)
    print("After simulated human review:", g.ingest(candidate, recorded_at=observed, reviewer_approved=True).disposition)

for effective, known in [("01-20", "02-20"), ("02-05", "02-05"), ("02-05", "02-20"), ("02-15", "02-20")]:
    answer = g.query(tenant="fictional-merchant", subject="refunds", predicate="window_days",
                     scope="NZ-online", effective_at=D(effective), known_at=D(known))
    print(f"At {effective}, as known {known}:", answer.render())

print("Propose outgoing email:", g.propose_effect(tool="email.send", args={"to": "nobody@example.invalid"}).disposition)
print("Can verify ledger:", g.verify_chain(anchored_head=g.head_digest))
print("Anchored head digest:", g.head_digest)
