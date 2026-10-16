# API Contract v4.7 — IPv6 Prefix-Aware Ingress

## `canonical_peer_identity(peer_ip, ipv6_prefix_length=64)`

- Accepts a numeric direct socket peer address only.
- Rejects empty, malformed and non-IP strings.
- Maps IPv4-mapped IPv6 addresses to their IPv4 identity.
- Returns `ipv4:<address>/32` for IPv4.
- Returns `ipv6:<network-address>/<prefix-length>` for native IPv6, using the configured prefix length (valid range `/32`–`/128`, default `/64`).
- Does not parse or trust forwarding headers.

## `SharedIngressQuotaStore`

New optional constructor parameter:

```python
ipv6_prefix_length: int = 64
```

The value is included in the shared DB configuration fingerprint alongside `peer_semantics=ipv6-prefix-v1` and schema 4. Same-boot replicas with a different value fail closed. This change is an intentional policy semantics migration; it does not rewrite existing lease rows in place.

`max_connections_per_ip` is retained for API compatibility but means **per-peer identity bucket**: exact IPv4 address or native IPv6 network prefix.

## `MTLSAnchoredRegistryHTTPServer`

- Accepts one explicit numeric IPv4 or IPv6 listener address.
- IPv4 selects `AF_INET`; IPv6 selects `AF_INET6` for that server instance.
- Wildcard addresses and scoped/link-local IPv6 addresses are rejected.
- Non-loopback binds still require `allow_nonloopback=True`.
- IPv6 Host authority is expected as `[literal]:port`; IPv4 remains `literal:port`.

There is no implicit wildcard dual-stack listener. To expose both address families, deploy separately reviewed listeners and ensure the shared rate/active quota authority is configured consistently.
