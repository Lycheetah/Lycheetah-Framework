# Lycheetah mTLS Registry Gateway Reference Pack v4.1

v4.1 closes the resource-admission gap identified in v4.0 by bounding connections before TLS handshake and before request worker creation.

## Verify

From this directory:

```sh
./run_v4.1_tests.sh checks
./run_v4.1_tests.sh quorum
./run_v4.1_tests.sh gateway
```

Run the suite commands as separate invocations. The retained quorum suite has 38 methods and the mTLS witness/gateway suite has 44 methods. The latter starts four witness subprocesses and a local gateway. Final successful per-suite logs are included.

## Resource defaults

- 32 total active connections
- 16 concurrent connections per direct peer IP
- 120 new connections per minute in a process-local global token bucket
- 64 socket listen backlog
- 3-second TLS handshake timeout, 10-second request socket timeout
- 128 KiB body limit retained from v4.0

The rate bucket is a burst limiter, not distributed or identity-aware rate control. One peer can exhaust the global bucket; production deployment needs an upstream identity-aware limiter and network-level flood controls.

## Boundary statement

The local tests use ephemeral certificates, four witness subprocesses and one host/operator. They do not establish independent trust domains or production DDoS resilience. No hosted service was contacted; upstream source and CI were not modified.
