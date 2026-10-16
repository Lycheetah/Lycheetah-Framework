# Lycheetah Closed-Loop Agent Lab v3.4

**New focus:** durable one-use freshness challenges. v3.4 persists each nonce, binds it to the verifier policy (protocol version, trusted anchor/witness keys, fault budget, report clock-skew limit and TTL), HMAC-authenticates the state record, and atomically consumes it after raw signed reports and certificate chain verify.

## Result

- Combined v3.3 + v3.4 focused suite: 56 test methods passed.
- Includes one intentional negative-control test showing a restored pre-consumption SQLite snapshot permits replay under the same HMAC key. This is a documented limitation, not a security pass.
- Five v3.2 baseline acceptance cases were reproduced with the frozen historical source. The copied historical reproduction harness had a malformed docstring; it was corrected in this pack before rerunning.
- No-network demo verifies the live current head once and then rejects the same challenge as consumed.

## Download-ready packages

- `lycheetah_durable_freshness_challenge_v3.4.zip` — standalone source + frozen v3.2 baseline + test harness and docs.
- `lycheetah_closed_loop_agent_lab_v3.4.zip` — complete lab history through v3.4.

## Residual limits

Local SQLite state and HMAC cannot provide rollback resistance against restoring the entire database snapshot. Production needs an independently administered, non-rollbackable challenge-consumption store, protected key custody and authenticated roster governance. No upstream source changes or hosted service calls were made. Read the v3.4 threat model before using this as a deployment design.
