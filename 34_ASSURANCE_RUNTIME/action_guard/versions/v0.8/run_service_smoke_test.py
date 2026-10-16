"""Start checkpoint_authority.py as a separate OS process and verify persistence.

Uses only loopback HTTP and a temporary directory. It does not contact GitHub or
any external service, and it makes no repository changes.
"""
from __future__ import annotations
import json
import os
import secrets
import socket
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from urllib.request import urlopen

from checkpoint_authority import CheckpointHTTPClient
from action_guard_v07 import AUDIT_GENESIS


def free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return int(s.getsockname()[1])


def wait_for_health(url: str, process: subprocess.Popen, timeout: float = 5.0) -> None:
    deadline = time.monotonic() + timeout
    last_error = None
    while time.monotonic() < deadline:
        if process.poll() is not None:
            raise RuntimeError(f"checkpoint process exited early: {process.returncode}")
        try:
            with urlopen(url + "/health", timeout=0.4) as response:
                if response.status == 200:
                    return
        except Exception as exc:
            last_error = exc
            time.sleep(0.05)
    raise RuntimeError(f"checkpoint service did not become healthy: {last_error}")


def main() -> None:
    with tempfile.TemporaryDirectory(prefix="lycheetah-authority-smoke-") as td:
        root = Path(td)
        db, private_key, public_key = root / "authority.sqlite3", root / "private.pem", root / "public.raw"
        port = free_port()
        token = secrets.token_urlsafe(32)
        env = os.environ.copy()
        env["LYCHEETAH_CHECKPOINT_TOKEN"] = token
        command = [sys.executable, str(Path(__file__).with_name("checkpoint_authority.py")),
                   "--db", str(db), "--key", str(private_key), "--public-key-out", str(public_key),
                   "--host", "127.0.0.1", "--port", str(port)]
        result = {"classification": "separate-process loopback smoke test", "live_github_calls": 0}
        process = subprocess.Popen(command, env=env, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
        try:
            url = f"http://127.0.0.1:{port}"
            wait_for_health(url, process)
            pinned_key = public_key.read_bytes()
            client = CheckpointHTTPClient(url, token, pinned_key)
            first = client.publish("process-smoke", {"event_count": 0, "last_seq": None,
                                                      "root_hash": AUDIT_GENESIS}, [])
            result["first_process_checkpoint_signature_valid"] = True
            result["generation_before_restart"] = first["generation"]
            result["private_key_permissions_octal"] = oct(private_key.stat().st_mode & 0o777)
            process.terminate(); process.wait(timeout=3)
            process = subprocess.Popen(command, env=env, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
            wait_for_health(url, process)
            second = client.get_latest("process-smoke")
            result["checkpoint_survived_process_restart"] = second["envelope_hash"] == first["envelope_hash"]
            result["same_public_key_after_restart"] = public_key.read_bytes() == pinned_key
            result["generation_after_restart"] = second["generation"]
            if not result["checkpoint_survived_process_restart"] or not result["same_public_key_after_restart"]:
                raise RuntimeError("persistence_or_signing_identity_check_failed")
            print(json.dumps(result, indent=2, sort_keys=True))
        finally:
            if process.poll() is None:
                process.terminate()
                try: process.wait(timeout=3)
                except subprocess.TimeoutExpired:
                    process.kill(); process.wait(timeout=3)


if __name__ == "__main__":
    main()
