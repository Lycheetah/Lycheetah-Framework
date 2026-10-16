# Threat Model v4.2 — Authenticated Coordinator Fairness

## Goals

- Retain bounded pre-TLS resource admission against unauthenticated connection bursts and slow headers.
- Limit active registry-facing dispatches and request rates independently for each approved coordinator principal after mTLS authentication.
- Avoid ambiguous identity mapping when one certificate contains multiple allow-listed SPIFFE URI SAN values.
- Keep diagnostic snapshots aggregate-only.

## Attacker capabilities considered

- Connect repeatedly from one or several direct peer IPs.
- Hold incomplete HTTP headers or bodies until a socket timeout.
- Present a CA-valid certificate with the wrong URI SAN, or a certificate containing multiple approved URI SANs.
- Use one approved coordinator identity to exhaust that identity's dispatch budget.
- Replay or alter signed request envelopes against inherited gateway controls.

## Controls

- Pre-TLS global and per-IP connection caps, global new-connection token bucket, finite listen backlog and socket timeouts.
- mTLS certificate-chain validation and exact URI-SAN allowlisting.
- Exactly-one-match identity rule for certificate-to-principal mapping.
- Per-principal active-dispatch semaphore-like counter and token bucket under one process lock.
- Signed 429 rate/concurrency response envelope, plus aggregate counters.
- Existing HMAC request validation, replay protection, signed responses, anchored registry and remote witness quorum checks.

## What this does not solve

- A process-local quota resets on restart and is not shared by multiple gateway replicas.
- The identity quota applies after HTTP header parsing; it cannot free slots already held by slow headers. Pre-TLS admission limits remain necessary.
- Source-IP spoofing is not generally a concern for established TCP connections, but NATs and trusted proxies may collapse many clients into one peer IP. Deployments behind proxies need trusted forwarding behavior and network-boundary controls rather than trusting arbitrary forwarded headers.
- A single coordinator can still consume its own quota; this pack has no reservation allocator or cross-principal QoS scheduler.
- No production CA lifecycle, revocation checking, OS-level file descriptor limits, external load balancer, multi-host topology, independent trust domain, or upstream CI was tested.

## Safe interpretation

This is a local executable resource/fairness reference. The passing tests establish the tested local schedules and code paths only, not deployment-level DDoS resilience or formal correctness.
