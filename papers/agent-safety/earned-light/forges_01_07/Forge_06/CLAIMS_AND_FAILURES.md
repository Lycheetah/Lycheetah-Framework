# Forge VI: claims register and Failure Museum

| Claim | Classification | Test / evidence | Boundary |
|---|---|---|---|
| Revocation blocks a new mock-controller dispatch | Locally tested | `test_dispatch_after_revocation_blocked` | Already-reserved calls may execute; no real provider fence |
| Reversal restores two sequential AI writes | Locally tested | `test_multiple_recovery_reverse_sequence` | Only within causal simulated store |
| Return avoids overwriting a later human change | Locally tested | `test_human_intervened_same_value_detected` | Provider knows true last writer |
| Lost acknowledgement can be reconciled when provider has a durable operation record | Locally tested | `test_lost_ack_reconciles_before_return` | Provider is assumed honest and reachable |
| A missing acknowledgment proves no effect | Rejected | `test_unobserved_effect_not_declared_safe` | Unresolved ≠ absent |
| Already-sent notifications can be restored | Rejected | `test_notification_irreversible` | Side effects escape local database |
| Action-bound HMAC proves authenticated human understanding | Rejected | Compromised-key test + architecture | Real identity/UI ceremony absent |
| Strong saga matches compensating functionality | Locally demonstrated | Four cases in `experiment.py` | No independent benchmark |
| Right of Return measures human free will | **Not supported** | No human study | Operational prototype only |

Open findings: provider collusion; compromised key; network outage; time-of-check/time-of-use; crash-cut-point coverage; real approval usability; compensation-induced unintended effects; privacy of receipts; performance overhead; signed, independent receipts; longitudinal measurement.
