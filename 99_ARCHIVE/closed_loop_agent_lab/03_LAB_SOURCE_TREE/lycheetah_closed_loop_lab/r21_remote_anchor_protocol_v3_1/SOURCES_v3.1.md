# Source Pin and Scope v3.1

- Observed upstream repository: `https://github.com/Lycheetah/Lycheetah-Framework`
- Observed upstream default branch: `master`
- Observed upstream commit from the v3.0 source pin: `8ae1b367dcf09997e82ce66f9ad5d30ff36e5d65`
- Upstream source modifications in this artifact: none.
- New remote anchor protocol/client/server simulator: authored in this artifact; it is not copied from upstream.
- Compatibility dependencies retained for regression checks: `external_checkpoint.py`, `external_checkpoint_cli.py`, `integrity_key_rotation.py`, `operation_ledger.py`, and `stripe_webhook_inbox.py` copied from the v3.0 reference pack to keep matching code revisions together.
- No hosted Stripe calls; no real refunds; no repository branch, pull request, or CI run.

The v3.1 protocol is an exploratory integration candidate, not a drop-in implementation of the existing `MonotonicAnchor` interface. The upstream v3.0 HMAC approval object and the v3.1 Ed25519 approval envelope are different contracts; integration requires an explicit reviewed migration.
