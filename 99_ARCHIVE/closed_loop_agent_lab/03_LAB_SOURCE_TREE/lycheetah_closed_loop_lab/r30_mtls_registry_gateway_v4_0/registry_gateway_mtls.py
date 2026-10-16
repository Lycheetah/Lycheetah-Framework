"""mTLS ingress for the quorum-guarded spent-challenge registry.

Reference-only adapter: it exposes the existing AnchoredRegistryHTTPServer
handler through TLS with coordinator client identity pinning. It does not alter
the registry's business logic and is not a production deployment blueprint.
"""
from __future__ import annotations

import ipaddress
import re
import socket
import ssl
import sys
from http.server import ThreadingHTTPServer
from typing import Iterable

from registry_checkpoint_quorum import AnchoredRegistryRequestHandler
from remote_anchor_http import canonical

MAX_GATEWAY_BODY = 128 * 1024
REQ_ID_RE = re.compile(r"^[A-Za-z0-9_-]{16,128}$")


def _numeric_ipv4_bind(host: str, allow_nonloopback: bool) -> str:
    if not isinstance(host, str) or not host:
        raise ValueError("gateway-bind-host-required")
    try:
        addr = ipaddress.ip_address(host)
    except ValueError:
        raise ValueError("gateway-bind-host-must-be-numeric-ipv4") from None
    if not isinstance(addr, ipaddress.IPv4Address):
        raise ValueError("gateway-bind-host-must-be-ipv4")
    if addr.is_unspecified or addr.is_multicast or addr.is_reserved:
        raise ValueError("gateway-bind-host-wildcard-or-reserved")
    if not addr.is_loopback and not allow_nonloopback:
        raise ValueError("gateway-nonloopback-bind-requires-opt-in")
    return str(addr)


def _uri_sans(cert_dict) -> set[str]:
    if not isinstance(cert_dict, dict):
        return set()
    return {value for kind, value in cert_dict.get("subjectAltName", ()) if kind == "URI"}


class MTLSAnchoredRegistryHTTPServer(ThreadingHTTPServer):
    """TLS 1.2+ server that requires a CA-trusted client and exact URI SAN."""
    daemon_threads = True
    allow_reuse_address = True

    def __init__(self, address, *, service, anchor, server_cert_path: str,
                 server_key_path: str, client_ca_path: str,
                 allowed_coordinator_uri_sans: Iterable[str],
                 allow_nonloopback: bool = False,
                 handshake_timeout_seconds: float = 3.0,
                 request_timeout_seconds: float = 10.0):
        host, port = address
        normalized_host = _numeric_ipv4_bind(host, allow_nonloopback)
        uri_sans = tuple(allowed_coordinator_uri_sans)
        if not uri_sans or any(not isinstance(u, str) or not u.startswith("spiffe://") for u in uri_sans):
            raise ValueError("gateway-coordinator-uri-san-allowlist-invalid")
        if len(set(uri_sans)) != len(uri_sans):
            raise ValueError("gateway-coordinator-uri-san-allowlist-duplicate")
        for value, name in ((server_cert_path, "server-cert"), (server_key_path, "server-key"),
                            (client_ca_path, "client-ca")):
            if not isinstance(value, str) or not value:
                raise ValueError(f"gateway-{name}-path-required")
        if not isinstance(handshake_timeout_seconds, (int, float)) or handshake_timeout_seconds <= 0:
            raise ValueError("gateway-handshake-timeout-invalid")
        if not isinstance(request_timeout_seconds, (int, float)) or request_timeout_seconds <= 0:
            raise ValueError("gateway-request-timeout-invalid")

        context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        context.minimum_version = ssl.TLSVersion.TLSv1_2
        context.options |= getattr(ssl, "OP_NO_COMPRESSION", 0)
        context.load_cert_chain(server_cert_path, server_key_path)
        context.load_verify_locations(cafile=client_ca_path)
        context.verify_mode = ssl.CERT_REQUIRED

        self.service = service
        self.anchor = anchor
        self.allowed_coordinator_uri_sans = frozenset(uri_sans)
        self.tls_context = context
        self.handshake_timeout_seconds = float(handshake_timeout_seconds)
        self.request_timeout_seconds = float(request_timeout_seconds)
        super().__init__((normalized_host, port), MTLSAnchoredRegistryRequestHandler)

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
        # Check the certificate identity before reading the body. TLS verifies the
        # chain; this pins the application principal to the configured coordinator.
        try:
            cert = self.connection.getpeercert()
            identities = _uri_sans(cert)
        except Exception:
            identities = set()
        if not identities.intersection(self.server.allowed_coordinator_uri_sans):
            self._write_signed_error(403, "coordinator-identity-invalid")
            return

        if self.command != "POST":
            self._write_signed_error(405, "method-not-allowed")
            return
        if self.path != "/v1/challenges" and not re.fullmatch(
            r"/v1/challenges/[A-Za-z0-9_-]{16,128}/consume", self.path
        ):
            self._write_signed_error(404, "route-not-found")
            return
        hosts = self.headers.get_all("Host", [])
        expected_host = f"{self.server.server_address[0]}:{self.server.server_address[1]}"
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
