# Forge VII threat model

## Covered
- Sudden termination of controller worker process before/after durable dispatch milestones.
- Durable controller/provider state separation; no cross-database atomicity.
- Missing acknowledgments after real provider-side synthetic effects.
- Duplicate retries (one robust idempotent case; one intentionally weak non-idempotent case).
- Sudden worker termination during compensation, with idempotent repetition.
- Loss of provider process with recovery after restart from preserved SQLite.

## Not covered
- Malicious or compromised provider, lying HTTP responses, doctored SQLite files, forged remote receipts.
- Authenticated human/operator intent and approval UI integrity. `revoke` is purely simulated.
- Network reordering, delayed delivery, partition healing races, real TLS or authenticated provider calls.
- Malicious external email/webpage prompt injection (investigated separately by Forges II–III).
- Multiple concurrent dispatchers, database corruption, power loss/fsync hardware guarantees, durable queue cluster semantics.
- External irreversibility, recipient reads/forwards, real financial transactions, real-world safety.

## Security claim boundary
A successful local simulated `restored` response means only that the stub provider recorded a compensation under its own rules. An operator must **not** interpret this as an independently verified restoration of the world.
