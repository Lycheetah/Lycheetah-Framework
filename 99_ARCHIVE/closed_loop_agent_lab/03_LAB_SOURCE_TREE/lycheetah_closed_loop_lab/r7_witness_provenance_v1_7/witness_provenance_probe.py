"""Source-equivalent probe of Lycheetah AdmissionWitness provenance semantics.

This deliberately models only the acceptance-relevant behavior visible in the
upstream finality.py. It is NOT an import of the upstream package and must not
be described as an upstream exploit test.
"""
from __future__ import annotations

import hashlib
import hmac
import json
import time
import uuid
from dataclasses import dataclass
from typing import Any

FINALITY_VERSION = "0.1.0"


def sha256_json(value: Any) -> str:
    encoded = json.dumps(value, ensure_ascii=False, allow_nan=False,
                         sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


@dataclass(frozen=True)
class EvidenceRequirement:
    key: str
    mode: str = "SUBJECT_STATUS"
    required_status: str = "PASS"
    required_subject_hash: str | None = None

    def to_dict(self):
        return {"key": self.key, "mode": self.mode,
                "required_status": self.required_status,
                "required_subject_hash": self.required_subject_hash}


@dataclass(frozen=True)
class EvidenceRecord:
    key: str
    version: str
    subject_hash: str
    value_digest: str
    status: str

    def to_dict(self):
        return {"key": self.key, "version": self.version,
                "subject_hash": self.subject_hash,
                "value_digest": self.value_digest, "status": self.status}


@dataclass(frozen=True)
class BoundEvidence:
    requirement: EvidenceRequirement
    admitted: EvidenceRecord

    def to_dict(self):
        return {"requirement": self.requirement.to_dict(),
                "admitted": self.admitted.to_dict()}


@dataclass(frozen=True)
class SourceEquivalentWitness:
    event_sha256: str
    policy_id: str
    policy_version: str
    policy_sha256: str
    admission_receipt_sha256: str
    evidence: tuple[BoundEvidence, ...]
    digest: str

    def body_dict(self):
        return {"schema_version": "0.1", "finality_version": FINALITY_VERSION,
                "event_sha256": self.event_sha256, "policy_id": self.policy_id,
                "policy_version": self.policy_version, "policy_sha256": self.policy_sha256,
                "admission_receipt_sha256": self.admission_receipt_sha256,
                "evidence": [item.to_dict() for item in self.evidence]}

    @classmethod
    def issue(cls, *, event_sha256, policy, admission_receipt_sha256, evidence):
        temp = cls(event_sha256, policy["id"], policy["version"], policy["sha256"],
                   admission_receipt_sha256, tuple(evidence), "")
        return cls(**{**temp.__dict__, "digest": sha256_json(temp.body_dict())})

    def verify(self):
        return hmac.compare_digest(self.digest, sha256_json(self.body_dict()))


class SourceEquivalentFinalityGate:
    """Acceptance-relevant mirror of upstream FinalityGate.finalize semantics."""
    def __init__(self, policy, evidence_provider, runtime_decision="ALLOW"):
        self.policy = dict(policy)
        self.evidence_provider = evidence_provider
        self.runtime_decision = runtime_decision

    def finalize(self, witness, event_sha256):
        if not witness.evidence:
            return False, "witness-evidence-empty"
        if not witness.verify():
            return False, "witness-integrity-invalid"
        if event_sha256 != witness.event_sha256:
            return False, "event-changed-after-admission"
        if self.runtime_decision == "BLOCK":
            return False, "underlying-runtime-blocked-at-finality"
        if self.runtime_decision != "ALLOW":
            return False, "underlying-runtime-not-allow-at-finality"
        current_policy = (self.policy["id"], self.policy["version"], self.policy["sha256"])
        admitted_policy = (witness.policy_id, witness.policy_version, witness.policy_sha256)
        if current_policy != admitted_policy:
            return False, "policy-changed-after-admission"
        for bound in witness.evidence:
            current = self.evidence_provider.get(bound.requirement.key)
            if current is None:
                return False, "required-evidence-missing-at-finality"
            if bound.requirement.mode == "EXACT":
                if current != bound.admitted:
                    return False, "exact-evidence-changed-after-admission"
            else:
                if current.key != bound.requirement.key:
                    return False, "wrong-evidence-key"
                if current.status != bound.requirement.required_status:
                    return False, "evidence-predicate-false-at-finality"
                if (bound.requirement.required_subject_hash is not None and
                    current.subject_hash != bound.requirement.required_subject_hash):
                    return False, "evidence-subject-mismatch"
        # Observed behavior: no witness-origin proof, no check that admission receipt
        # existed/verified, and no comparison against a trusted requirement set.
        return True, "fresh-evidence-and-current-policy"


class TrustedWitnessIssuer:
    """Illustrative defense: HMAC provenance, trusted requirement binding, one-use id."""
    def __init__(self, secret: bytes, policy: dict, allowed_requirements: tuple[EvidenceRequirement, ...],
                 clock=time.time):
        if not secret:
            raise ValueError("non-empty secret required")
        self._secret = secret
        self.policy = dict(policy)
        self.allowed_requirements = tuple(allowed_requirements)
        self._clock = clock
        self._issued: dict[str, str] = {}
        self._consumed: set[str] = set()

    def issue(self, event_sha256: str, admission_receipt_sha256: str,
              evidence: tuple[BoundEvidence, ...], ttl_seconds: int = 60):
        requirements = tuple(x.requirement for x in evidence)
        if requirements != self.allowed_requirements:
            raise ValueError("witness requirements differ from trusted configured requirements")
        jti = str(uuid.uuid4())
        body = {"schema_version": "1.0", "jti": jti,
                "event_sha256": event_sha256, "policy": self.policy,
                "admission_receipt_sha256": admission_receipt_sha256,
                "issued_at": self._clock(), "expires_at": self._clock() + ttl_seconds,
                "evidence": [x.to_dict() for x in evidence]}
        signature = hmac.new(self._secret, sha256_json(body).encode("ascii"), hashlib.sha256).hexdigest()
        self._issued[jti] = sha256_json(body)
        return {"body": body, "hmac_sha256": signature}

    def finalize(self, token, event_sha256: str, current_policy: dict, provider: dict[str, EvidenceRecord],
                 runtime_decision="ALLOW"):
        if not isinstance(token, dict) or set(token) != {"body", "hmac_sha256"}:
            return False, "invalid-token-envelope"
        body = token["body"]
        digest = sha256_json(body)
        expected = hmac.new(self._secret, digest.encode("ascii"), hashlib.sha256).hexdigest()
        if not hmac.compare_digest(str(token["hmac_sha256"]), expected):
            return False, "witness-authentication-failed"
        jti = body.get("jti")
        if jti not in self._issued or self._issued[jti] != digest:
            return False, "witness-not-issued-by-this-gate"
        if jti in self._consumed:
            return False, "witness-already-consumed"
        now = self._clock()
        if not isinstance(body.get("expires_at"), (int, float)) or now > body["expires_at"]:
            return False, "witness-expired"
        if body.get("event_sha256") != event_sha256:
            return False, "event-changed-after-admission"
        if body.get("policy") != current_policy or current_policy != self.policy:
            return False, "policy-changed-after-admission"
        if runtime_decision != "ALLOW":
            return False, "runtime-not-allow-at-finality"
        if body.get("evidence") is None or not body["evidence"]:
            return False, "witness-evidence-empty"
        for bound in body["evidence"]:
            req, admitted = bound["requirement"], bound["admitted"]
            current = provider.get(req["key"])
            if current is None:
                return False, "required-evidence-missing-at-finality"
            if req["mode"] == "EXACT":
                if current.to_dict() != admitted:
                    return False, "exact-evidence-changed-after-admission"
            else:
                if current.key != req["key"] or current.status != req["required_status"]:
                    return False, "evidence-predicate-false-at-finality"
                if req["required_subject_hash"] is not None and current.subject_hash != req["required_subject_hash"]:
                    return False, "evidence-subject-mismatch"
        # Consume before returning authorization. A real effect broker must couple
        # this reservation with durable idempotent action intent; this in-memory demo
        # alone does not make external side effects atomic.
        self._consumed.add(jti)
        return True, "authenticated-fresh-evidence-and-single-use-witness"


def fixture():
    policy = {"id": "test.policy", "version": "1", "sha256": "a" * 64}
    event = {"tool": "deploy.promote", "artifact": "A", "amount": 5}
    event_digest = sha256_json(event)
    ci = EvidenceRecord("ci-required", "1", "A", "build-123", "PASS")
    decoy = EvidenceRecord("local-note", "1", "A", "unchecked", "PASS")
    provider = {ci.key: ci, decoy.key: decoy}
    trusted_req = EvidenceRequirement("ci-required", "EXACT", "PASS", "A")
    trusted_bound = BoundEvidence(trusted_req, ci)
    return policy, event, event_digest, provider, trusted_req, trusted_bound


def run_probe():
    policy, event, event_digest, provider, trusted_req, trusted_bound = fixture()
    honest = SourceEquivalentWitness.issue(event_sha256=event_digest, policy=policy,
        admission_receipt_sha256="b" * 64, evidence=(trusted_bound,))
    source_gate = SourceEquivalentFinalityGate(policy, provider)
    honest_ok, honest_reason = source_gate.finalize(honest, event_digest)

    forged_req = EvidenceRequirement("local-note", "SUBJECT_STATUS", "PASS", "A")
    forged_bound = BoundEvidence(forged_req, provider["local-note"])
    forged = SourceEquivalentWitness.issue(event_sha256=event_digest, policy=policy,
        admission_receipt_sha256="f" * 64, evidence=(forged_bound,))
    forged_ok, forged_reason = source_gate.finalize(forged, event_digest)

    issuer = TrustedWitnessIssuer(b"test-only witness secret", policy, (trusted_req,))
    strict_token = issuer.issue(event_digest, "b" * 64, (trusted_bound,))
    strict_ok, strict_reason = issuer.finalize(strict_token, event_digest, policy, provider)
    forged_token = {"body": dict(strict_token["body"]), "hmac_sha256": strict_token["hmac_sha256"]}
    forged_token["body"]["evidence"] = [forged_bound.to_dict()]
    forged_token["body"]["admission_receipt_sha256"] = "f" * 64
    forged_token["hmac_sha256"] = sha256_json(forged_token["body"])  # attempt to replace HMAC with a public digest
    strict_forged_ok, strict_forged_reason = issuer.finalize(forged_token, event_digest, policy, provider)
    replay_ok, replay_reason = issuer.finalize(strict_token, event_digest, policy, provider)
    return {
        "scope": "source-equivalent acceptance-logic probe; not full upstream execution",
        "upstream_revision": "8ae1b367dcf09997e82ce66f9ad5d30ff36e5d65",
        "upstream_source": "lycheetah/assurance/finality.py",
        "source_blob_sha": "dd97733d45c2261863d24a2a00800baf59fc8bac",
        "cases": [
            {"case": "honest_witness", "observed": "ACCEPT" if honest_ok else "REJECT", "reason": honest_reason,
             "expected": "ACCEPT"},
            {"case": "unkeyed_digest_witness_with_substituted_evidence_requirement_and_fake_receipt_digest",
             "observed": "ACCEPT" if forged_ok else "REJECT", "reason": forged_reason,
             "expected_under_current_semantics": "ACCEPT", "security_interpretation": "provenance gap if witness input or storage is adversary-modifiable"},
            {"case": "strict_authenticated_witness", "observed": "ACCEPT" if strict_ok else "REJECT", "reason": strict_reason,
             "expected": "ACCEPT"},
            {"case": "strict_candidate_with_mutated_evidence_and_public_hash_substitution",
             "observed": "ACCEPT" if strict_forged_ok else "REJECT", "reason": strict_forged_reason,
             "expected": "REJECT"},
            {"case": "strict_candidate_replay_after_consumption", "observed": "ACCEPT" if replay_ok else "REJECT",
             "reason": replay_reason, "expected": "REJECT"}
        ],
        "limits": [
            "This test mirrors acceptance-relevant upstream semantics from the inspected source; it does not import or execute the upstream package.",
            "The issue depends on the threat model: if only a trusted in-process caller can supply witness objects and no untrusted persistence boundary exists, external forgery is not established.",
            "The candidate verifier is illustrative, in-memory, and is not production ready. The action effect and nonce consumption are not transactionally coupled to a remote provider.",
            "The admission receipt digest in current finality is carried as metadata but finalize does not verify it corresponds to an issued receipt."
        ]
    }

if __name__ == "__main__":
    print(json.dumps(run_probe(), indent=2, sort_keys=True))
