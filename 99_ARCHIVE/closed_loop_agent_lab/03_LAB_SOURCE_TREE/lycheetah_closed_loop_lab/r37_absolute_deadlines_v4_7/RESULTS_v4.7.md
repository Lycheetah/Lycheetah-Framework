# Verification Results v4.7 — Absolute HTTP Socket Deadline

## Outcome

| Suite / check | Methods | Result |
|---|---:|---|
| Shared ingress quota store | 24 | PASS |
| Shared coordinator quota store | 13 | PASS |
| Checkpoint quorum | 38 | PASS |
| Gateway mTLS and remote-witness integration | 56 | PASS |
| Focused deadline/handshake controls (included in gateway suite) | 3 | PASS |
| **Unique combined suite total** | **131** | **PASS** |
| Source fingerprint verification | 21 files | PASS |
| Python compilation | all packaged Python files | PASS |
| Archive CRC | built during packaging | PASS |

The focused three-test run was also repeated independently: header slow drip, body slow drip, and the existing partial TLS-record handshake-timeout control all passed. The gateway suite completed 56 tests in 56.947 seconds with `LIFECYCLE_SUMMARY tests=56 errors=0 failures=0 surviving_non_main_threads=[]`.

## Measured v4.6/v4.7 delta

The latest paired same-host mTLS HTTP header probe observed:

- v4.6 baseline: 1 active connection at 1.227 seconds, after 15 slowly delivered bytes.
- v4.7 candidate: 0 active connections at 0.971 seconds, after 12 slowly delivered bytes.
- Inter-byte gap: 80 ms, below the 550 ms inactivity timeout.

Earlier repeats varied slightly in time but showed the same qualitative behavior. These measurements cover a deliberately incomplete HTTP request only; no registry dispatch or hosted API call occurred. They are not an overall throughput or production-load benchmark.

## Diagnostic anomaly retained

During one full gateway run, the lifecycle runner emitted its scheduled faulthandler diagnostic at 45 seconds while a request handler was awaiting a fresh remote quorum head during a gateway dispatch. The suite subsequently completed all 56 tests successfully in 56.947 seconds and reported no surviving Python threads. This confirms an important limitation of the feature: the socket deadline does not cancel in-progress application/quorum work. The client may lose its response while server-side mutation processing continues. A real integration must preserve idempotency/reconciliation and may need cooperative operation deadlines; this research change does not claim to solve that separate problem.

## Claims deliberately not made

- No new TLS handshake guarantee: the paired partial-TLS-record check showed no delta from v4.6's existing Python/OpenSSL timeout.
- No cancellation of application logic after request parsing.
- No remote/hosted service calls, no upstream CI result, and no upstream source mutation.
- No proof against SYN floods, multi-host quota multiplication, or distributed transaction failures.

## Reproduction

From this directory:

```bash
./run_v4.7_tests.sh checks
./run_v4.7_tests.sh ingress
./run_v4.7_tests.sh coordinator
./run_v4.7_tests.sh quorum
./run_v4.7_tests.sh gateway
python baseline_http_deadline_probe_v4.7.py
```

Run suites sequentially rather than concurrently because the gateway tests start four local witness processes and use shared SQLite/quorum state.
