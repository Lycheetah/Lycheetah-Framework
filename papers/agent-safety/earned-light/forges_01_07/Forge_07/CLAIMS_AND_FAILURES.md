# Forge VII — Claims register and Failure Museum

| ID | Observed result / failure | What it does **not** prove |
|---|---|---|
| C7-01 | 31/31 local Python tests pass, including subprocess exit paths | Independent penetration testing, real-world safety, production readiness |
| C7-02 | 16 manually scripted crash cases yield 5 restored / 5 irreversible / 4 unresolved / 2 not dispatched | Statistical rate in any natural distribution of failures |
| C7-03 | Provider restart after loss of service permits delayed recovery in one synthetic scenario | All real providers expose trustworthy, durable operation receipts |
| C7-04 | Stable-ID idempotent retry causes one effect, non-idempotent retry two | Advantage over a sound conventional transactional outbox |
| FM7-01 | **False negative from reservation gap:** after reservation, provider never receives request yet controller cannot prove absence, reports unknown | That every unknown caused a remote side effect |
| FM7-02 | **Receipt trust-root gap:** provider DB may be falsified by privileged attacker; provider-reported != independent proof | Tamper-evident ground truth |
| FM7-03 | **Operator-authentication gap:** script's revoke call is not tied to verified human | Human sovereignty preserved under active adversaries |
| FM7-04 | **Delayed in-flight request:** revocation alone cannot cancel a transmitted request | Strong real-time revocation fencing |
| FM7-05 | **Non-idempotent retry:** a provider without stable dedup creates duplicate consequences | Exactly-once effects across arbitrary external APIs |
| FM7-06 | **Compensation semantics:** sample write restoration simply marks effect compensated; no third-party concurrent edits | Correct rollback in live mutable external systems |
| FM7-07 | **Counterfactual distance:** a perfect local receipt trail does not measure whether a human understood the result | Measured free will, autonomy, capability retention |
| FM7-08 | **Localhost and privileged test runner:** the controller controls the provider start, stop and inspection | Independent third-party attestation or Byzantine safety |

**Evidence labels:** tests=executed; failures=demonstrated; deployment=none; human trial=none; consciousness theory=speculative and outside this experiment.
