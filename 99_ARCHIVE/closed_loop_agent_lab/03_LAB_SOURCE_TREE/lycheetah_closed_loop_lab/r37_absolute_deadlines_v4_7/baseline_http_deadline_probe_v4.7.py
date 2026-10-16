#!/usr/bin/env python3
"""Paired HTTP slow-drip probe: v4.6 source copy versus v4.7 deadline handler."""
from __future__ import annotations
import json, socket, ssl, tempfile, threading, time, ipaddress
from pathlib import Path
from datetime import datetime, timedelta, timezone
from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509.oid import NameOID, ExtendedKeyUsageOID
from registry_gateway_mtls_v4_6_baseline import MTLSAnchoredRegistryHTTPServer as BaselineServer
from registry_gateway_mtls import MTLSAnchoredRegistryHTTPServer as DeadlineServer

URI = "spiffe://lycheetah.local/coordinator"

def _write_key(path: Path, key):
    path.write_bytes(key.private_bytes(serialization.Encoding.PEM, serialization.PrivateFormat.PKCS8, serialization.NoEncryption()))
    path.chmod(0o600)

def issue_test_certs(root: Path):
    now = datetime.now(timezone.utc)
    ca_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    ca_name = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, "Lycheetah Deadline Probe CA")])
    ca_cert = (x509.CertificateBuilder().subject_name(ca_name).issuer_name(ca_name)
        .public_key(ca_key.public_key()).serial_number(x509.random_serial_number())
        .not_valid_before(now-timedelta(minutes=1)).not_valid_after(now+timedelta(days=1))
        .add_extension(x509.BasicConstraints(ca=True,path_length=0),critical=True)
        .add_extension(x509.KeyUsage(digital_signature=True,content_commitment=False,key_encipherment=True,
            data_encipherment=False,key_agreement=False,key_cert_sign=True,crl_sign=True,
            encipher_only=None,decipher_only=None),critical=True)
        .add_extension(x509.SubjectKeyIdentifier.from_public_key(ca_key.public_key()),critical=False)
        .add_extension(x509.AuthorityKeyIdentifier.from_issuer_public_key(ca_key.public_key()),critical=False)
        .sign(ca_key,hashes.SHA256()))
    def leaf(name: str, san, eku):
        key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
        subject = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, name)])
        cert = (x509.CertificateBuilder().subject_name(subject).issuer_name(ca_name)
            .public_key(key.public_key()).serial_number(x509.random_serial_number())
            .not_valid_before(now-timedelta(minutes=1)).not_valid_after(now+timedelta(days=1))
            .add_extension(x509.SubjectAlternativeName(san),critical=False)
            .add_extension(x509.ExtendedKeyUsage([eku]),critical=True)
            .add_extension(x509.SubjectKeyIdentifier.from_public_key(key.public_key()),critical=False)
            .add_extension(x509.AuthorityKeyIdentifier.from_issuer_public_key(ca_key.public_key()),critical=False)
            .sign(ca_key,hashes.SHA256()))
        return cert,key
    server_cert,server_key=leaf("127.0.0.1",[x509.IPAddress(ipaddress.ip_address("127.0.0.1"))],ExtendedKeyUsageOID.SERVER_AUTH)
    client_cert,client_key=leaf("deadline-probe-coordinator",[x509.UniformResourceIdentifier(URI)],ExtendedKeyUsageOID.CLIENT_AUTH)
    ca_path,cert_path,key_path,client_cert_path,client_key_path=(root/n for n in ("ca.pem","server.pem","server-key.pem","client.pem","client-key.pem"))
    ca_path.write_bytes(ca_cert.public_bytes(serialization.Encoding.PEM))
    cert_path.write_bytes(server_cert.public_bytes(serialization.Encoding.PEM)); _write_key(key_path,server_key)
    client_cert_path.write_bytes(client_cert.public_bytes(serialization.Encoding.PEM)); _write_key(client_key_path,client_key)
    context=ssl.create_default_context(ssl.Purpose.SERVER_AUTH,cafile=str(ca_path))
    context.minimum_version=ssl.TLSVersion.TLSv1_2
    context.load_cert_chain(str(client_cert_path),str(client_key_path))
    return ca_path,cert_path,key_path,context

def make_server(cls, certs):
    ca,cert,key,_client_context=certs
    return cls(("127.0.0.1",0), service=object(), anchor=object(),
        server_cert_path=str(cert),server_key_path=str(key),client_ca_path=str(ca),
        allowed_coordinator_uri_sans=(URI,),handshake_timeout_seconds=1.0,
        request_timeout_seconds=0.55,**({"request_deadline_seconds":0.85} if cls is DeadlineServer else {}),
        max_concurrent_connections=1,max_connections_per_ip=1,max_new_connections_per_minute=600,
        max_active_requests_per_coordinator=1,max_requests_per_coordinator_per_minute=600)

def probe(server, client_context, duration=1.2):
    thread=threading.Thread(target=server.serve_forever,daemon=True,name="http-deadline-pair-probe")
    thread.start(); client=None
    try:
        raw=socket.create_connection(("127.0.0.1",server.server_address[1]),timeout=2)
        client=client_context.wrap_socket(raw,server_hostname="127.0.0.1")
        client.settimeout(0.8)
        client.sendall((f"POST /v1/challenges HTTP/1.1\r\nHost: 127.0.0.1:{server.server_address[1]}\r\n").encode("ascii"))
        start=time.monotonic(); stop=start+duration; sent=0
        while time.monotonic()<stop:
            try: client.sendall(b"X")
            except (OSError,ssl.SSLError): break
            sent+=1; time.sleep(0.08)  # Always below the 0.55s idle timeout.
        during=int(server.admission_snapshot()["active_connections"])
        elapsed=round(time.monotonic()-start,3)
        return {"elapsed_seconds":elapsed,"bytes_dripped":sent,"active_connection_at_observation":during}
    finally:
        if client is not None: client.close()
        deadline=time.monotonic()+1.0
        while server.admission_snapshot()["active_connections"] and time.monotonic()<deadline: time.sleep(0.01)
        after=int(server.admission_snapshot()["active_connections"])
        server.shutdown();server.server_close();thread.join(timeout=2)
        if thread.is_alive(): raise RuntimeError("probe server thread did not stop")
        probe.last_after_release=after

def main():
    with tempfile.TemporaryDirectory(prefix="lyc-http-deadline-pair-") as td:
        certs=issue_test_certs(Path(td))
        baseline=make_server(BaselineServer,certs); candidate=make_server(DeadlineServer,certs)
        before=probe(baseline,certs[3]); before["active_after_client_close"]=probe.last_after_release
        after=probe(candidate,certs[3]); after["active_after_client_close"]=probe.last_after_release
        result={"baseline":"v4.6 source copy with socket inactivity timeout only",
            "candidate":"v4.7 local handler with absolute HTTP exchange deadline",
            "baseline_observation":before,"v4_7_observation":after,
            "expected_delta":before["active_connection_at_observation"]==1 and after["active_connection_at_observation"]==0,
            "scope":"same-host mTLS HTTP header slow-drip experiment; no request body, registry dispatch, or hosted service"}
        print(json.dumps(result,indent=2))
        return 0 if result["expected_delta"] else 1
if __name__=="__main__": raise SystemExit(main())
