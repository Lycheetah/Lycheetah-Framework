# Baseline Comparison v4.7

## v4.6 comparison

The preserved v4.6 handler uses socket inactivity timeouts. Buffered HTTP request-line/header reads can consume several partial reads, so a client that sends bytes before each idle timeout may keep the handler occupied for longer than one inactivity interval.

## Paired slow-drip probe

The same-host mTLS HTTP header probe ran against a preserved local v4.6 gateway copy and the v4.7 candidate. In the latest repeat, the baseline still had one active connection at 1.227 seconds after receiving 15 dripped bytes; v4.7 had released the active connection by 0.971 seconds after 12 bytes. Bytes arrived every 80 ms, below the configured 550 ms inactivity timeout. Earlier repeats showed the same qualitative delta with slightly different elapsed times.

This was a local request-header test only: no full HTTP request completed, no registry dispatch occurred, and no hosted service was contacted. This demonstrates the specific slow-drip resource case; it is not a production load test.

## Controls and non-claims

The partial TLS-record control does **not** show a v4.7 improvement. Both v4.6 and v4.7 were bounded by the existing Python/OpenSSL handshake timeout for the tested input, so v4.7 retains that behavior without claiming a new TLS-handshake deadline.

The request deadline closes the transport socket, but cannot preempt application code already running after the request has been parsed. A slow quorum dispatch may therefore continue after the client has lost its connection; idempotency and reconciliation remain required.
