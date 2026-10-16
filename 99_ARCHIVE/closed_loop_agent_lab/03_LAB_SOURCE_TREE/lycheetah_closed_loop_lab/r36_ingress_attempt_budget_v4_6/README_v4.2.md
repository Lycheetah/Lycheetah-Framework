# Lycheetah mTLS Registry Gateway Reference Pack v4.2

v4.2 adds authenticated coordinator-level dispatch quotas to the v4.1 bounded-ingress gateway. The gateway now uses the exact allow-listed SPIFFE URI SAN as the quota identity and rejects a certificate if more than one allow-listed coordinator identity appears in that certificate.

## Verify

Run the suites as separate invocations:

```sh
./run_v4.2_tests.sh checks
./run_v4.2_tests.sh quorum
./run_v4.2_tests.sh gateway
```

Completed local results: 38 quorum suite tests and 47 remote-witness/gateway tests passed. The gateway suite runs four witness subprocesses and a local coordinator gateway.

## Limits

- 32 total active connections before TLS, 16 active connections per direct peer IP, and a process-local global token bucket for new TCP connections.
- 8 active dispatches per authenticated coordinator and 60 authenticated request tokens per minute per coordinator by default.
- 64 listen backlog, 3-second TLS handshake timeout, 10-second request timeout, and 128 KiB request-body limit.
- Per-coordinator quotas are process-local and begin only after HTTP headers have parsed; they do not provide distributed quotas, pre-header identity fairness, or protection from distributed-source floods.
- Production deployment still requires a trusted ingress/rate-control layer, OS resource limits, CA governance and revocation, multi-host tests and upstream CI.

## Boundary

Ephemeral local certificates and four witness subprocesses share one host and operator. This is an executable reference harness, not formal verification or production certification. No hosted services were contacted; upstream source and CI were not changed.
