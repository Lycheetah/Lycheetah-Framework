"""mTLS ingress for the quorum-guarded spent-challenge registry.

Reference-only adapter: it exposes the existing AnchoredRegistryHTTPServer
handler through TLS with coordinator client identity pinning. It does not alter
the registry's business logic and is not a production deployment blueprint.
"""
from __future__ import annotations

import ipaddress
import math
import re
import socket
import ssl
import sys
import threading
import time
from http.server import ThreadingHTTPServer
from typing import Iterable

from registry_checkpoint_quorum import AnchoredRegistryRequestHandler
from remote_anchor_http import canonical
from shared_coordinator_quota import SharedCoordinatorQuotaStore, SharedQuotaError
from shared_ingress_quota import (
    SharedIngressQuotaStore, SharedIngressQuotaError,
    DEFAULT_IPV6_PREFIX_LENGTH, canonical_peer_identity, canonical_peer_aggregate_identity,
)

MAX_GATEWAY_BODY = 128 * 1024
REQ_ID_RE = re.compile(r"^[A-Za-z0-9_-]{16,128}$")
DEFAULT_MAX_ACTIVE_CONNECTIONS = 32
DEFAULT_MAX_CONNECTIONS_PER_IP = 16
DEFAULT_MAX_NEW_CONNECTIONS_PER_MINUTE = 120
DEFAULT_MAX_ACTIVE_REQUESTS_PER_COORDINATOR = 8
DEFAULT_MAX_REQUESTS_PER_COORDINATOR_PER_MINUTE = 60
DEFAULT_ACCEPT_BACKLOG = 64


def _numeric_bind_host(host: str, allow_nonloopback: bool) -> str:
    """Validate a single numeric IPv4 or IPv6 listener address.

    Wildcard binds and scoped IPv6 literals are deliberately unsupported. Use a
    separately reviewed network/proxy configuration for wildcard exposure.
    """
    if not isinstance(host, str) or not host:
        raise ValueError("gateway-bind-host-required")
    if '%' in host:
        raise ValueError("gateway-bind-host-scoped-ipv6-not-supported")
    try:
        addr = ipaddress.ip_address(host)
    except ValueError:
        raise ValueError("gateway-bind-host-must-be-numeric-ipv4-or-ipv6") from None
    if addr.is_unspecified or addr.is_multicast or (addr.is_reserved and not addr.is_loopback):
        raise ValueError("gateway-bind-host-wildcard-or-reserved")
    if isinstance(addr, ipaddress.IPv6Address) and addr.is_link_local:
        raise ValueError("gateway-bind-host-link-local-not-supported")
    if not addr.is_loopback and not allow_nonloopback:
        raise ValueError("gateway-nonloopback-bind-requires-opt-in")
    return str(addr)


def _numeric_ipv4_bind(host: str, allow_nonloopback: bool) -> str:
    """Compatibility validator retained for existing callers/tests."""
    if not isinstance(host, str) or not host:
        raise ValueError("gateway-bind-host-required")
    try:
        addr = ipaddress.ip_address(host)
    except ValueError:
        raise ValueError("gateway-bind-host-must-be-numeric-ipv4") from None
    if not isinstance(addr, ipaddress.IPv4Address):
        raise ValueError("gateway-bind-host-must-be-ipv4")
    return _numeric_bind_host(host, allow_nonloopback)


def _uri_sans(cert_dict) -> set[str]:
    if not isinstance(cert_dict, dict):
        return set()
    return {value for kind, value in cert_dict.get("subjectAltName", ()) if kind == "URI"}


class MTLSAnchoredRegistryHTTPServer(ThreadingHTTPServer):
    """TLS 1.2+ server with bounded pre-authentication resource admission.

    Global, per-peer-bucket, and connection-rate bounds apply before TLS handshake
    so unauthenticated peers cannot create unbounded request threads. After mTLS,
    the exact allow-listed SPIFFE URI SAN receives independent active-request and
    request-rate quotas. Principal quotas begin after HTTP headers have parsed, so
    they do not replace the pre-authentication slow-header bounds. Every quota is
    process-local; none replaces a shared proxy/firewall quota in deployment.
    """
    daemon_threads = True
    allow_reuse_address = True
    request_queue_size = DEFAULT_ACCEPT_BACKLOG

    def __init__(self, address, *, service, anchor, server_cert_path: str,
                 server_key_path: str, client_ca_path: str,
                 allowed_coordinator_uri_sans: Iterable[str],
                 allow_nonloopback: bool = False,
                 handshake_timeout_seconds: float = 3.0,
                 request_timeout_seconds: float = 10.0,
                 max_concurrent_connections: int = DEFAULT_MAX_ACTIVE_CONNECTIONS,
                 max_connections_per_ip: int = DEFAULT_MAX_CONNECTIONS_PER_IP,
                 max_new_connections_per_minute: int = DEFAULT_MAX_NEW_CONNECTIONS_PER_MINUTE,
                 ipv6_prefix_length: int = DEFAULT_IPV6_PREFIX_LENGTH,
                 ipv6_aggregate_prefix_length: int | None = None,
                 max_connections_per_ipv6_aggregate: int | None = None,
                 max_active_requests_per_coordinator: int = DEFAULT_MAX_ACTIVE_REQUESTS_PER_COORDINATOR,
                 max_requests_per_coordinator_per_minute: int = DEFAULT_MAX_REQUESTS_PER_COORDINATOR_PER_MINUTE,
                 shared_coordinator_quota_db_path: str | None = None,
                 coordinator_quota_lease_ttl_seconds: float = 120.0,
                 shared_ingress_quota_db_path: str | None = None,
                 ingress_quota_lease_ttl_seconds: float = 120.0,
                 request_queue_size: int = DEFAULT_ACCEPT_BACKLOG):
        host, port = address
        normalized_host = _numeric_bind_host(host, allow_nonloopback)
        bind_address = ipaddress.ip_address(normalized_host)
        if (isinstance(ipv6_prefix_length, bool) or not isinstance(ipv6_prefix_length, int)
                or not 32 <= ipv6_prefix_length <= 128):
            raise ValueError("gateway-ipv6-prefix-length-invalid")
        if (ipv6_aggregate_prefix_length is None) != (max_connections_per_ipv6_aggregate is None):
            raise ValueError("gateway-ipv6-aggregate-prefix-and-limit-must-be-configured-together")
        if ipv6_aggregate_prefix_length is not None:
            if (isinstance(ipv6_aggregate_prefix_length, bool)
                    or not isinstance(ipv6_aggregate_prefix_length, int)
                    or not 32 <= ipv6_aggregate_prefix_length < ipv6_prefix_length):
                raise ValueError("gateway-ipv6-aggregate-prefix-length-invalid")
            if (isinstance(max_connections_per_ipv6_aggregate, bool)
                    or not isinstance(max_connections_per_ipv6_aggregate, int)
                    or max_connections_per_ipv6_aggregate < 1
                    or isinstance(max_concurrent_connections, bool)
                    or not isinstance(max_concurrent_connections, int)
                    or max_concurrent_connections < 1
                    or max_connections_per_ipv6_aggregate > max_concurrent_connections):
                raise ValueError("gateway-ipv6-aggregate-limit-invalid")
        uri_sans = tuple(allowed_coordinator_uri_sans)
        if not uri_sans or any(not isinstance(u, str) or not u.startswith("spiffe://") for u in uri_sans):
            raise ValueError("gateway-coordinator-uri-san-allowlist-invalid")
        if len(set(uri_sans)) != len(uri_sans):
            raise ValueError("gateway-coordinator-uri-san-allowlist-duplicate")
        for value, name in ((server_cert_path, "server-cert"), (server_key_path, "server-key"),
                            (client_ca_path, "client-ca")):
            if not isinstance(value, str) or not value:
                raise ValueError(f"gateway-{name}-path-required")
        for value, name in ((handshake_timeout_seconds, "handshake"),
                            (request_timeout_seconds, "request")):
            if (isinstance(value, bool) or not isinstance(value, (int, float))
                    or not math.isfinite(value) or value <= 0):
                raise ValueError(f"gateway-{name}-timeout-invalid")
        for value, name in ((max_concurrent_connections, "max-concurrent-connections"),
                            (max_connections_per_ip, "max-connections-per-ip"),
                            (max_new_connections_per_minute, "max-new-connections-per-minute"),
                            (max_active_requests_per_coordinator, "max-active-requests-per-coordinator"),
                            (max_requests_per_coordinator_per_minute, "max-requests-per-coordinator-per-minute"),
                            (request_queue_size, "request-queue-size")):
            if isinstance(value, bool) or not isinstance(value, int) or value < 1:
                raise ValueError(f"gateway-{name}-invalid")
        if max_connections_per_ip > max_concurrent_connections:
            raise ValueError("gateway-per-ip-limit-exceeds-global-limit")
        if (isinstance(coordinator_quota_lease_ttl_seconds, bool)
                or not isinstance(coordinator_quota_lease_ttl_seconds, (int, float))
                or not math.isfinite(coordinator_quota_lease_ttl_seconds)
                or coordinator_quota_lease_ttl_seconds <= request_timeout_seconds):
            raise ValueError("gateway-coordinator-quota-lease-ttl-must-exceed-request-timeout")
        if shared_coordinator_quota_db_path is not None and (
                not isinstance(shared_coordinator_quota_db_path, str)
                or not shared_coordinator_quota_db_path):
            raise ValueError("gateway-shared-coordinator-quota-db-path-invalid")
        if shared_ingress_quota_db_path is not None and (
                not isinstance(shared_ingress_quota_db_path, str)
                or not shared_ingress_quota_db_path):
            raise ValueError("gateway-shared-ingress-quota-db-path-invalid")
        if (isinstance(ingress_quota_lease_ttl_seconds, bool)
                or not isinstance(ingress_quota_lease_ttl_seconds, (int, float))
                or not math.isfinite(ingress_quota_lease_ttl_seconds)
                or ingress_quota_lease_ttl_seconds <= handshake_timeout_seconds + request_timeout_seconds):
            raise ValueError("gateway-ingress-quota-lease-ttl-must-exceed-handshake-plus-request-timeouts")

        context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        context.minimum_version = ssl.TLSVersion.TLSv1_2
        context.options |= getattr(ssl, "OP_NO_COMPRESSION", 0)
        context.load_cert_chain(server_cert_path, server_key_path)
        context.load_verify_locations(cafile=client_ca_path)
        context.verify_mode = ssl.CERT_REQUIRED

        self.service = service
        self.anchor = anchor
        self.address_family = socket.AF_INET6 if isinstance(bind_address, ipaddress.IPv6Address) else socket.AF_INET
        self.ipv6_prefix_length = ipv6_prefix_length
        self.ipv6_aggregate_prefix_length = ipv6_aggregate_prefix_length
        self.max_connections_per_ipv6_aggregate = max_connections_per_ipv6_aggregate
        self.allowed_coordinator_uri_sans = frozenset(uri_sans)
        self.tls_context = context
        self.handshake_timeout_seconds = float(handshake_timeout_seconds)
        self.request_timeout_seconds = float(request_timeout_seconds)
        self.max_concurrent_connections = max_concurrent_connections
        self.max_connections_per_ip = max_connections_per_ip
        self.max_new_connections_per_minute = max_new_connections_per_minute
        self.max_active_requests_per_coordinator = max_active_requests_per_coordinator
        self.max_requests_per_coordinator_per_minute = max_requests_per_coordinator_per_minute
        self.shared_coordinator_quota_db_path = shared_coordinator_quota_db_path
        self.coordinator_quota_store = (
            SharedCoordinatorQuotaStore(
                shared_coordinator_quota_db_path,
                max_active_per_coordinator=max_active_requests_per_coordinator,
                max_requests_per_minute=max_requests_per_coordinator_per_minute,
                active_lease_ttl_seconds=coordinator_quota_lease_ttl_seconds,
            ) if shared_coordinator_quota_db_path is not None else None
        )
        self.shared_ingress_quota_db_path = shared_ingress_quota_db_path
        self.ingress_quota_lease_ttl_seconds = float(ingress_quota_lease_ttl_seconds)
        self.shared_ingress_quota_store = (
            SharedIngressQuotaStore(
                shared_ingress_quota_db_path,
                max_active_connections=max_concurrent_connections,
                max_connections_per_ip=max_connections_per_ip,
                max_new_connections_per_minute=max_new_connections_per_minute,
                ipv6_prefix_length=ipv6_prefix_length,
                ipv6_aggregate_prefix_length=ipv6_aggregate_prefix_length,
                max_connections_per_ipv6_aggregate=max_connections_per_ipv6_aggregate,
                active_lease_ttl_seconds=ingress_quota_lease_ttl_seconds,
            ) if shared_ingress_quota_db_path is not None else None
        )
        self._pending_ingress_leases = {}
        self._pending_ingress_lock = threading.Lock()
        self.request_queue_size = request_queue_size
        self._admission_lock = threading.Lock()
        self._active_connections = 0
        self._active_by_ip: dict[str, int] = {}
        self._active_by_ipv6_aggregate: dict[str, int] = {}
        self._rate_tokens = float(max_new_connections_per_minute)
        self._rate_updated_at = time.monotonic()
        self._active_by_coordinator: dict[str, int] = {}
        self._coordinator_rate: dict[str, tuple[float, float]] = {}
        self._admission_rejections = {
            "active-connection-limit": 0,
            "per-ip-connection-limit": 0,
            "ipv6-aggregate-connection-limit": 0,
            "connection-rate-limit": 0,
            "peer-address-invalid": 0,
            "coordinator-active-request-limit": 0,
            "coordinator-request-rate-limit": 0,
            "coordinator-identity-ambiguous": 0,
        }
        super().__init__((normalized_host, port), MTLSAnchoredRegistryRequestHandler)

    def admission_snapshot(self) -> dict[str, object]:
        """Small operational snapshot; never returns client IPs or request data."""
        with self._admission_lock:
            shared_snapshot = self.coordinator_quota_store.snapshot() if self.coordinator_quota_store else None
            return {
                "active_connections": self._active_connections,
                "active_peer_count": len(self._active_by_ip),
                "active_coordinator_count": (int(shared_snapshot["active_principal_count"])
                                              if shared_snapshot else len(self._active_by_coordinator)),
                "coordinator_quota_mode": ("shared-sqlite-same-host" if shared_snapshot else "process-local"),
                "shared_quota": ({k: v for k, v in shared_snapshot.items() if k != "mode"}
                                 if shared_snapshot else None),
                "shared_ingress_quota": (
                    {k: v for k, v in self.shared_ingress_quota_store.snapshot().items() if k != "mode"}
                    if self.shared_ingress_quota_store else None
                ),
                "rejections": dict(self._admission_rejections),
                "rate_tokens_approx": round(self._rate_tokens, 3),
                "max_concurrent_connections": self.max_concurrent_connections,
                "max_connections_per_ip": self.max_connections_per_ip,
                "ipv6_prefix_length": self.ipv6_prefix_length,
                "ipv6_aggregate_prefix_length": self.ipv6_aggregate_prefix_length,
                "max_connections_per_ipv6_aggregate": self.max_connections_per_ipv6_aggregate,
                "active_ipv6_aggregate_buckets": len(self._active_by_ipv6_aggregate),
                "max_new_connections_per_minute": self.max_new_connections_per_minute,
                "max_active_requests_per_coordinator": self.max_active_requests_per_coordinator,
                "max_requests_per_coordinator_per_minute": self.max_requests_per_coordinator_per_minute,
            }

    @staticmethod
    def _canonical_client_ip(client_address) -> str | None:
        """Canonical direct socket peer; never trust forwarding headers here."""
        if not isinstance(client_address, (tuple, list)) or not client_address:
            return None
        try:
            address = ipaddress.ip_address(str(client_address[0]))
        except ValueError:
            return None
        if isinstance(address, ipaddress.IPv6Address) and address.ipv4_mapped is not None:
            address = address.ipv4_mapped
        return address.compressed

    def _reserve_admission(self, client_address) -> str | None:
        raw_peer = self._canonical_client_ip(client_address)
        if raw_peer is None:
            with self._admission_lock:
                self._admission_rejections["peer-address-invalid"] += 1
            return "peer-address-invalid"
        peer = canonical_peer_identity(raw_peer, self.ipv6_prefix_length)
        aggregate = canonical_peer_aggregate_identity(raw_peer, self.ipv6_aggregate_prefix_length)
        now = time.monotonic()
        with self._admission_lock:
            # Treat the rate limiter as an attempt budget. Charge it before
            # active-slot decisions so excess attempts still consume global
            # admission budget rather than hammering saturated quota checks free.
            elapsed = max(0.0, now - self._rate_updated_at)
            refill_per_second = self.max_new_connections_per_minute / 60.0
            self._rate_tokens = min(
                float(self.max_new_connections_per_minute),
                self._rate_tokens + elapsed * refill_per_second,
            )
            self._rate_updated_at = now
            if self._rate_tokens < 1.0:
                self._admission_rejections["connection-rate-limit"] += 1
                return "connection-rate-limit"
            self._rate_tokens -= 1.0
            if self._active_connections >= self.max_concurrent_connections:
                self._admission_rejections["active-connection-limit"] += 1
                return "active-connection-limit"
            if self._active_by_ip.get(peer, 0) >= self.max_connections_per_ip:
                self._admission_rejections["per-ip-connection-limit"] += 1
                return "per-ip-connection-limit"
            if (aggregate is not None and self.max_connections_per_ipv6_aggregate is not None
                    and self._active_by_ipv6_aggregate.get(aggregate, 0) >= self.max_connections_per_ipv6_aggregate):
                self._admission_rejections["ipv6-aggregate-connection-limit"] += 1
                return "ipv6-aggregate-connection-limit"
            self._active_connections += 1
            self._active_by_ip[peer] = self._active_by_ip.get(peer, 0) + 1
            if aggregate is not None:
                self._active_by_ipv6_aggregate[aggregate] = self._active_by_ipv6_aggregate.get(aggregate, 0) + 1
            return None

    def _release_admission(self, client_address) -> None:
        raw_peer = self._canonical_client_ip(client_address)
        peer = canonical_peer_identity(raw_peer, self.ipv6_prefix_length) if raw_peer is not None else None
        aggregate = canonical_peer_aggregate_identity(raw_peer, self.ipv6_aggregate_prefix_length) if raw_peer is not None else None
        with self._admission_lock:
            self._active_connections = max(0, self._active_connections - 1)
            if peer is not None:
                current = self._active_by_ip.get(peer, 0)
                if current <= 1:
                    self._active_by_ip.pop(peer, None)
                else:
                    self._active_by_ip[peer] = current - 1
            if aggregate is not None:
                current_aggregate = self._active_by_ipv6_aggregate.get(aggregate, 0)
                if current_aggregate <= 1:
                    self._active_by_ipv6_aggregate.pop(aggregate, None)
                else:
                    self._active_by_ipv6_aggregate[aggregate] = current_aggregate - 1

    def _reserve_coordinator_request(self, principal: str) -> str | None:
        """Bound authenticated work by one exact SPIFFE URI SAN.

        The global pre-TLS controls still bound unauthenticated resource use. This
        second gate adds fairness after the certificate identity is known; it is
        process-local, not a distributed quota.
        """
        now = time.monotonic()
        with self._admission_lock:
            active = self._active_by_coordinator.get(principal, 0)
            if active >= self.max_active_requests_per_coordinator:
                self._admission_rejections["coordinator-active-request-limit"] += 1
                return "coordinator-active-request-limit"
            previous_tokens, previous_at = self._coordinator_rate.get(
                principal, (float(self.max_requests_per_coordinator_per_minute), now)
            )
            elapsed = max(0.0, now - previous_at)
            refill = self.max_requests_per_coordinator_per_minute / 60.0
            tokens = min(float(self.max_requests_per_coordinator_per_minute), previous_tokens + elapsed * refill)
            if tokens < 1.0:
                self._coordinator_rate[principal] = (tokens, now)
                self._admission_rejections["coordinator-request-rate-limit"] += 1
                return "coordinator-request-rate-limit"
            self._coordinator_rate[principal] = (tokens - 1.0, now)
            self._active_by_coordinator[principal] = active + 1
            return None

    def _release_coordinator_request(self, principal: str) -> None:
        with self._admission_lock:
            active = self._active_by_coordinator.get(principal, 0)
            if active <= 1:
                self._active_by_coordinator.pop(principal, None)
            else:
                self._active_by_coordinator[principal] = active - 1

    def process_request(self, request, client_address):
        # This executes before creating a request thread and before the TLS
        # handshake. Shared ingress quotas are also reserved here, so a same-host
        # fleet cannot multiply its pre-authentication budget by replica count.
        ingress_lease = None
        peer = self._canonical_client_ip(client_address)
        if peer is None:
            self._record_rejection("peer-address-invalid")
            self._drop_request(request)
            return
        if self.shared_ingress_quota_store is not None:
            try:
                ingress_lease, rejection = self.shared_ingress_quota_store.reserve(peer)
            except SharedIngressQuotaError:
                self._record_rejection("shared-ingress-quota-authority-unavailable")
                self._drop_request(request)
                return
            if rejection is not None:
                self._record_rejection(rejection)
                self._drop_request(request)
                return

        rejection = self._reserve_admission(client_address)
        if rejection is not None:
            if ingress_lease is not None:
                try:
                    ingress_lease.close()
                except SharedIngressQuotaError:
                    pass
            self._drop_request(request)
            return
        if ingress_lease is not None:
            with self._pending_ingress_lock:
                self._pending_ingress_leases[id(request)] = ingress_lease
        try:
            super().process_request(request, client_address)
        except Exception:
            self._release_admission(client_address)
            lease = self._pop_ingress_lease(request)
            if lease is not None:
                try:
                    lease.close()
                except SharedIngressQuotaError:
                    pass
            self._drop_request(request)
            raise

    def _record_rejection(self, reason: str) -> None:
        with self._admission_lock:
            self._admission_rejections[reason] = self._admission_rejections.get(reason, 0) + 1

    @staticmethod
    def _drop_request(request) -> None:
        try:
            request.shutdown(2)
        except Exception:
            pass
        try:
            request.close()
        except Exception:
            pass

    def _pop_ingress_lease(self, request):
        with self._pending_ingress_lock:
            return self._pending_ingress_leases.pop(id(request), None)

    def process_request_thread(self, request, client_address):
        ingress_lease = self._pop_ingress_lease(request)
        try:
            super().process_request_thread(request, client_address)
        finally:
            self._release_admission(client_address)
            if ingress_lease is not None:
                try:
                    ingress_lease.close()
                except SharedIngressQuotaError:
                    # The lease expires if storage release fails; store failures are
                    # visible operationally and never bypass new admissions.
                    pass

    def get_request(self):
        raw, address = super().get_request()
        try:
            wrapped = self.tls_context.wrap_socket(raw, server_side=True, do_handshake_on_connect=False)
            wrapped.settimeout(self.handshake_timeout_seconds)
            return wrapped, address
        except Exception:
            raw.close()
            raise

    def handle_error(self, request, client_address):
        # Invalid TLS and interrupted connections are expected hostile inputs;
        # do not emit exception text or request material to logs.
        return


class MTLSAnchoredRegistryRequestHandler(AnchoredRegistryRequestHandler):
    server: MTLSAnchoredRegistryHTTPServer

    def setup(self):
        try:
            self.request.settimeout(self.server.handshake_timeout_seconds)
            self.request.do_handshake()
            self.request.settimeout(self.server.request_timeout_seconds)
        except Exception:
            self.request.close()
            raise
        super().setup()

    def _write_signed_error(self, status: int, code: str):
        rid = self.headers.get("X-Lyc-Registry-Request-Id", "invalid-request-id")
        if not REQ_ID_RE.fullmatch(rid):
            rid = "invalid-request-id"
        payload = canonical(self.server.service._sign(status, {"error": code}, rid))
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(payload)))
        self.send_header("Connection", "close")
        self.end_headers()
        try:
            self.wfile.write(payload)
        except (BrokenPipeError, ConnectionResetError, OSError):
            pass
        self.close_connection = True

    def _dispatch(self):
        # The coordinator identity is the exact allow-listed SPIFFE URI SAN.
        # Zero matches is unauthenticated at the application-principal layer;
        # more than one match is ambiguous and must not silently pick a role.
        try:
            cert = self.connection.getpeercert()
            identities = _uri_sans(cert)
        except Exception:
            identities = set()
        matches = identities.intersection(self.server.allowed_coordinator_uri_sans)
        if not matches:
            self._write_signed_error(403, "coordinator-identity-invalid")
            return
        if len(matches) != 1:
            with self.server._admission_lock:
                self.server._admission_rejections["coordinator-identity-ambiguous"] += 1
            self._write_signed_error(403, "coordinator-identity-ambiguous")
            return

        principal = next(iter(matches))
        if self.server.coordinator_quota_store is not None:
            try:
                lease, rejection = self.server.coordinator_quota_store.reserve(principal)
            except SharedQuotaError:
                # Quota authority is part of admission. Never dispatch when it is
                # unavailable or inconsistent across replicas.
                self._write_signed_error(503, "coordinator-quota-authority-unavailable")
                return
            if rejection is not None:
                with self.server._admission_lock:
                    self.server._admission_rejections[rejection] = self.server._admission_rejections.get(rejection, 0) + 1
                self._write_signed_error(429, rejection)
                return
            try:
                self._dispatch_authenticated()
            finally:
                try:
                    lease.close()
                except SharedQuotaError:
                    # The lease expires if release fails; availability is secondary
                    # to not bypassing the shared quota authority.
                    pass
            return
        rejection = self.server._reserve_coordinator_request(principal)
        if rejection is not None:
            self._write_signed_error(429, rejection)
            return
        try:
            self._dispatch_authenticated()
        finally:
            self.server._release_coordinator_request(principal)

    def _dispatch_authenticated(self):
        if self.command != "POST":
            self._write_signed_error(405, "method-not-allowed")
            return
        if self.path != "/v1/challenges" and not re.fullmatch(
            r"/v1/challenges/[A-Za-z0-9_-]{16,128}/consume", self.path
        ):
            self._write_signed_error(404, "route-not-found")
            return
        hosts = self.headers.get_all("Host", [])
        server_host = self.server.server_address[0]
        if self.server.address_family == socket.AF_INET6:
            # HTTP authority syntax requires brackets around IPv6 literals;
            # e.g. `[::1]:8443`. A bare `::1:8443` is ambiguous and is not a
            # valid Host authority for the IPv6 listener.
            expected_host = f"[{server_host}]:{self.server.server_address[1]}"
        else:
            expected_host = f"{server_host}:{self.server.server_address[1]}"
        if len(hosts) != 1 or hosts[0].strip().lower() != expected_host.lower():
            self._write_signed_error(400, "host-header-invalid")
            return
        if self.headers.get("Transfer-Encoding") is not None:
            self._write_signed_error(400, "transfer-encoding-not-supported")
            return
        lengths = self.headers.get_all("Content-Length", [])
        if len(lengths) != 1 or not re.fullmatch(r"[0-9]+", lengths[0]):
            self._write_signed_error(400, "content-length-invalid")
            return
        if int(lengths[0]) > MAX_GATEWAY_BODY:
            self._write_signed_error(413, "request-body-too-large")
            return
        content_types = self.headers.get_all("Content-Type", [])
        if len(content_types) != 1 or content_types[0].strip().lower() != "application/json":
            self._write_signed_error(415, "content-type-invalid")
            return
        super()._dispatch()

    # Restrict the ingress surface to POST requests only.
    do_POST = _dispatch
    do_GET = _dispatch
    do_PUT = _dispatch
    do_PATCH = _dispatch
    do_DELETE = _dispatch
    do_OPTIONS = _dispatch

    def log_message(self, *_args):
        return
