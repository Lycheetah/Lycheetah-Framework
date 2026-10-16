"""Self-contained local demo of a primary-signed checkpoint plus witness quorum.
All keys and SQLite files are ephemeral; no external service is contacted.
"""
from __future__ import annotations
from contextlib import closing
import tempfile
import uuid
from pathlib import Path

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from remote_anchor_http import DOMAIN_RECORD, b64, canonical, iso, make_snapshot, sha_json, utc_now
from checkpoint_witness_quorum import (
    CheckpointWitness, SQLiteCASGuard, create_certificate, new_freshness_challenge,
    verify_certificate_chain, verify_current_chain, verify_fresh_head_quorum,
)

DBID = "lycheetah.demo.operations"
ANCHOR_KEY_ID = "demo-primary-anchor"


def make_record(anchor_key, *, sequence, parent_hash, variant):
    snap = make_snapshot(
        ("a" if variant == "first" else "d") * 64,
        ("b" if variant == "first" else "e") * 64,
        {"operations": sequence}, {"signed": sequence},
    )
    body = {
        "sequence": sequence, "database_id": DBID, **snap,
        "approval_id": "approval_" + uuid.uuid4().hex,
        "approval_nonce": "nonce_" + uuid.uuid4().hex,
        "reason_code": "approved.demo.checkpoint",
        "created_at": iso(utc_now()), "previous_record_sha256": parent_hash,
        "request_id": "req_" + uuid.uuid4().hex,
        "request_sha256": ("c" if variant == "first" else "f") * 64,
        "server_key_id": ANCHOR_KEY_ID,
    }
    digest = sha_json(body)
    signature = anchor_key.sign(DOMAIN_RECORD + canonical({"body": body, "record_sha256": digest, "server_key_id": ANCHOR_KEY_ID}))
    return {"body": body, "record_sha256": digest, "server_key_id": ANCHOR_KEY_ID, "signature_b64": b64(signature)}


def main():
    with tempfile.TemporaryDirectory(prefix="lyc-v32-demo-") as tmp:
        root = Path(tmp)
        anchor_private = Ed25519PrivateKey.generate()
        anchor_keys = {ANCHOR_KEY_ID: anchor_private.public_key()}
        private_keys = {f"witness-{i}": Ed25519PrivateKey.generate() for i in range(1, 5)}
        public_keys = {wid: key.public_key() for wid, key in private_keys.items()}
        witnesses = {
            wid: CheckpointWitness(wid, key, root / f"{wid}-votes.sqlite",
                                   SQLiteCASGuard(root / f"{wid}-guard.sqlite"), anchor_keys)
            for wid, key in private_keys.items()
        }
        record1 = make_record(anchor_private, sequence=1, parent_hash=None, variant="first")
        votes1 = [w.attest(record1) for w in witnesses.values()]
        cert1 = create_certificate(record1, votes1, anchor_keys, public_keys)

        record2 = make_record(anchor_private, sequence=2, parent_hash=record1["record_sha256"], variant="second")
        votes2 = [w.attest(record2) for w in witnesses.values()]
        cert2 = create_certificate(record2, votes2, anchor_keys, public_keys)
        chain = verify_certificate_chain([cert1, cert2], anchor_keys, public_keys)

        nonce = new_freshness_challenge()
        reports = [w.report_head(DBID, nonce) for w in witnesses.values()]
        fresh = verify_fresh_head_quorum(reports, public_keys, database_id=DBID, challenge_nonce=nonce)
        verify_current_chain([cert1, cert2], reports, anchor_keys, public_keys,
                             database_id=DBID, challenge_nonce=nonce)

        print("LYCHEETAH_V3_3_DEMO=PASS")
        print(f"database_id={DBID}")
        print(f"verified_chain_length={len(chain)}")
        print(f"current_sequence={fresh.sequence}")
        print(f"current_head_sha256={fresh.record_sha256}")
        print(f"matching_fresh_witnesses={len(fresh.agreeing_witness_ids)} / {len(public_keys)}")
        print("external_network_calls=0")


if __name__ == "__main__":
    main()
