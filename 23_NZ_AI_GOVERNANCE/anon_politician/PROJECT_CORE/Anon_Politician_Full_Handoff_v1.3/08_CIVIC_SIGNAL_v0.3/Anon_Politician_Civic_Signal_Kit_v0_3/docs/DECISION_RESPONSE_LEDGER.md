# Public Decision-Response Ledger

The response ledger connects participation to accountable action. The aim is not to promise every suggestion will be adopted; it is to show whether the suggestion was heard, what the decision owner did with it and why.

## Recommended row fields

- `theme_id`: stable identifier for the issue/theme, not a participant identity.
- `theme_summary`: plain-language summary reviewed against the source inputs.
- `input_channels`: open pulse, representative survey, deliberative panel, targeted consultation, formal submission, or other.
- `evidence_refs`: public source IDs supporting factual statements; never publish private participant links.
- `minority_or_high_severity_concern`: whether the issue must remain visible even if few participants raised it.
- `decision_status`: `accepted`, `partially_accepted`, `not_adopted`, `deferred`, `outside_authority`, `needs_more_evidence`, `unresolved`.
- `decision_rationale`: explanation including evidence, values, trade-offs and uncertainty.
- `policy_change`: specific edit, budget/design change or `no_change`.
- `change_basis`: `public_input`, `evidence`, `legal_requirement`, `implementation_learning`, `value_judgment`, `other` (multiple allowed).
- `decision_owner`: role/office, not an AI agent.
- `response_date`: date of public response.
- `follow_up_owner` and `follow_up_due`: who reports next and when.
- `reopen_trigger`: what future evidence or change should cause review.
- `audit_history`: version/change metadata.

## Sample entry (illustrative only)

```json
{
  "theme_id": "DL-TRANSPARENCY-001",
  "theme_summary": "People need to understand how a levy was calculated and what happens if forecast infrastructure is delayed or not delivered.",
  "input_channels": ["open_pulse", "stakeholder_submissions"],
  "evidence_refs": ["S001", "S002"],
  "minority_or_high_severity_concern": true,
  "decision_status": "needs_more_evidence",
  "decision_rationale": "The supplied official materials describe future methodology and information-disclosure work, but this case packet does not yet contain the final calculation method or a published evaluation of impacts.",
  "policy_change": "No policy change claimed at this stage; request transparent worked examples and failure/recalculation rules for the formal process.",
  "change_basis": ["public_input", "evidence"],
  "decision_owner": "Relevant accountable public authority",
  "response_date": "TBD",
  "follow_up_owner": "Relevant accountable public authority",
  "follow_up_due": "TBD",
  "reopen_trigger": "Publication of the draft calculation methodology or evidence of systematic forecast error",
  "audit_history": []
}
```

The sample is not a statement that any real authority made this decision. Never fill `policy_change` with an impact unless it is evidenced by the document history.
