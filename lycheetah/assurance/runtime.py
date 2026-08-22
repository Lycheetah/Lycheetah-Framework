"""Provider-neutral assurance policy enforcement point.

Status: [SCAFFOLD]. The runtime makes bounded, inspectable decisions; it does
not certify that an agent, model, or deployment is safe or aligned.
"""

from __future__ import annotations

import fnmatch
from typing import Any, Iterable, Mapping, Optional

from ..applications.aura_text_checker import AURATextAnalyser
from ..core.semantic_extractor import Extraction, SemanticExtractor
from .jsonutil import redact, sensitive_key, sha256_json, sha256_text
from .models import (
    AssuranceEvent,
    ClaimStatus,
    ControlReference,
    Disposition,
    Finding,
    Phase,
    Severity,
    strongest,
)
from .policy import AssurancePolicy, TextRule, default_policy
from .receipt import AssuranceReceipt


ASSURANCE_VERSION = "0.1.0"

OWASP_PROMPT_INJECTION = ControlReference(
    framework="OWASP GenAI",
    control_id="LLM01",
    title="Prompt Injection",
    url="https://genai.owasp.org/llmrisk/llm01-prompt-injection/",
)
OWASP_TOOL_MISUSE = ControlReference(
    framework="OWASP Agentic Top 10",
    control_id="ASI02",
    title="Tool Misuse",
    url=(
        "https://genai.owasp.org/resource/"
        "owasp-top-10-for-agentic-applications-for-2026/"
    ),
)
OPENAI_HUMAN_REVIEW = ControlReference(
    framework="OpenAI Agents SDK",
    control_id="HITL",
    title="Human review before sensitive tool actions",
    url="https://developers.openai.com/api/docs/guides/agents/guardrails-approvals",
)
MCP_USER_CONTROL = ControlReference(
    framework="Model Context Protocol",
    control_id="CONSENT-CONTROL",
    title="User consent and control",
    url="https://modelcontextprotocol.io/specification/2026-07-28",
)


class AssuranceRuntime:
    """Evaluate one event and emit a self-contained Assurance Receipt."""

    def __init__(
        self,
        policy: Optional[AssurancePolicy] = None,
        *,
        extractor: Optional[SemanticExtractor] = None,
        analyser: Optional[AURATextAnalyser] = None,
    ) -> None:
        self.policy = policy or default_policy()
        self.extractor = extractor or SemanticExtractor()
        self.analyser = analyser or AURATextAnalyser(extractor=self.extractor)

    def evaluate(
        self,
        event: AssuranceEvent,
        *,
        previous_receipt_sha256: Optional[str] = None,
        hmac_secret: Optional[bytes] = None,
        hmac_key_id: Optional[str] = None,
    ) -> AssuranceReceipt:
        findings: list[Finding] = []
        metrics: dict[str, Any] = {}

        if event.phase in (Phase.INPUT, Phase.OUTPUT):
            text_findings, text_metrics = self._evaluate_text(event)
            findings.extend(text_findings)
            metrics.update(text_metrics)
        elif event.phase == Phase.TOOL:
            tool_findings, tool_metrics = self._evaluate_tool(event)
            findings.extend(tool_findings)
            metrics.update(tool_metrics)

        decision = strongest(
            [finding.effective_disposition for finding in findings]
        )
        event_record = self._event_record(event)

        return AssuranceReceipt.issue(
            runtime={
                "name": "lycheetah-assurance",
                "version": ASSURANCE_VERSION,
                "status": ClaimStatus.SCAFFOLD.value,
                "components": [
                    {
                        "name": "evidence-capped-enforcement",
                        "status": ClaimStatus.SCAFFOLD.value,
                    },
                    {
                        "name": "semantic-extractor",
                        "status": ClaimStatus.ACTIVE.value,
                        "scope": "implemented cue families only",
                    },
                    {
                        "name": "aura-tri-axial-text-proxy",
                        "status": ClaimStatus.SCAFFOLD.value,
                    },
                ],
            },
            policy={
                "id": self.policy.policy_id,
                "version": self.policy.version,
                "sha256": self.policy.digest,
            },
            event=event_record,
            decision=decision,
            findings=findings,
            metrics=metrics,
            limitations=self._limitations(event_record),
            trace_id=event.trace_id,
            previous_receipt_sha256=previous_receipt_sha256,
            hmac_secret=hmac_secret,
            hmac_key_id=hmac_key_id,
        )

    def evaluate_text(
        self,
        text: str,
        *,
        phase: Phase = Phase.OUTPUT,
        **kwargs: Any,
    ) -> AssuranceReceipt:
        if Phase(phase) == Phase.TOOL:
            raise ValueError("evaluate_text phase must be input or output")
        return self.evaluate(AssuranceEvent(phase=phase, content=text), **kwargs)

    def evaluate_tool(
        self,
        tool_name: str,
        arguments: Optional[Mapping[str, Any]] = None,
        *,
        scopes: Iterable[str] = (),
        side_effect: bool = False,
        human_approved: Optional[bool] = None,
        **kwargs: Any,
    ) -> AssuranceReceipt:
        event = AssuranceEvent(
            phase=Phase.TOOL,
            tool_name=tool_name,
            tool_arguments=arguments or {},
            scopes=tuple(scopes),
            side_effect=side_effect,
            human_approved=human_approved,
        )
        return self.evaluate(event, **kwargs)

    def _evaluate_text(
        self, event: AssuranceEvent
    ) -> tuple[list[Finding], dict[str, Any]]:
        text = event.content or ""
        findings: list[Finding] = []
        if not text.strip():
            findings.append(
                Finding.create(
                    finding_id="LYC:TEXT:EMPTY",
                    title="Empty text event",
                    description="No text was available for the requested assurance check.",
                    severity=Severity.MEDIUM,
                    requested_disposition=Disposition.REVIEW,
                    claim_status=ClaimStatus.ACTIVE,
                    deterministic=True,
                    evaluator="event-schema",
                    status_basis="Direct structural check: non-empty text is required.",
                )
            )
            return findings, {"text": {"characters": 0, "words": 0}}

        if len(text) > self.policy.max_text_characters:
            findings.append(
                Finding.create(
                    finding_id="LYC:TEXT:SIZE_LIMIT",
                    title="Text exceeds configured analysis limit",
                    description=(
                        "The runtime did not run heuristic or regular-expression "
                        "analysis because the text exceeds the policy size boundary."
                    ),
                    severity=Severity.HIGH,
                    requested_disposition=Disposition.REVIEW,
                    claim_status=ClaimStatus.ACTIVE,
                    deterministic=True,
                    evaluator="event-schema",
                    status_basis="Exact configured resource boundary.",
                    evidence=[
                        f"characters={len(text)}",
                        f"max_text_characters={self.policy.max_text_characters}",
                    ],
                )
            )
            return findings, {
                "text": {
                    "characters": len(text),
                    "analysis_skipped": True,
                    "reason": "max_text_characters",
                }
            }

        extraction = self.extractor.extract(text)
        report = self.analyser.analyse(text)

        if extraction.manipulation_density >= self.policy.manipulation_review_threshold:
            evidence = self._semantic_evidence(extraction)
            controls = [OWASP_PROMPT_INJECTION] if event.phase == Phase.INPUT else []
            findings.append(
                Finding.create(
                    finding_id="LYC:TEXT:MANIPULATION_CUES",
                    title="Manipulation cue density above review threshold",
                    description=(
                        "The bounded semantic extractor found compositional cue families "
                        "associated with verification suppression, fabricated certainty, "
                        "coercion, secrecy, dependency, or related manipulation patterns."
                    ),
                    severity=Severity.HIGH,
                    requested_disposition=Disposition.REVIEW,
                    claim_status=ClaimStatus.ACTIVE,
                    deterministic=False,
                    evaluator="semantic-extractor/1",
                    confidence=min(0.99, 0.5 + extraction.manipulation_density / 2.0),
                    status_basis=(
                        "ACTIVE only for implemented cue families; interpretation remains inferential."
                    ),
                    evidence=evidence,
                    controls=controls,
                )
            )

        if report.alignment_percent < self.policy.aura_review_below_percent:
            failing = [
                invariant.name
                for invariant in report.invariants
                if not invariant.passed and invariant.confidence != "NEEDS_REVIEW"
            ]
            evidence = [
                f"alignment_percent={report.alignment_percent:.3f}",
                f"threshold={self.policy.aura_review_below_percent:.3f}",
            ]
            if failing:
                evidence.append("failed_invariants=" + ",".join(failing))
            findings.append(
                Finding.create(
                    finding_id="LYC:AURA:BELOW_REVIEW_THRESHOLD",
                    title="AURA text proxy below policy review threshold",
                    description=(
                        "The current AURA/TRI-AXIAL text proxy fell below the policy's "
                        "review threshold. Thresholds and proxy formulas are not externally calibrated."
                    ),
                    severity=Severity.MEDIUM,
                    requested_disposition=Disposition.REVIEW,
                    claim_status=ClaimStatus.SCAFFOLD,
                    deterministic=False,
                    evaluator="aura-text-proxy/1",
                    confidence=0.55,
                    status_basis=(
                        "TRI-AXIAL text proxies and thresholds remain SCAFFOLD pending calibration."
                    ),
                    evidence=evidence,
                )
            )

        needs_review = [
            invariant.name
            for invariant in report.invariants
            if invariant.confidence == "NEEDS_REVIEW"
        ]
        if needs_review:
            findings.append(
                Finding.create(
                    finding_id="LYC:AURA:CONTEXT_REQUIRED",
                    title="Context-dependent invariants not resolved",
                    description=(
                        "One or more invariants require session, authority, or deployment context "
                        "that a single text output does not contain."
                    ),
                    severity=Severity.INFO,
                    requested_disposition=Disposition.ALLOW,
                    claim_status=ClaimStatus.ACTIVE,
                    deterministic=True,
                    evaluator="aura-text-proxy/1",
                    status_basis="Direct report of NEEDS_REVIEW markers emitted by the analyser.",
                    evidence=["invariants=" + ",".join(needs_review)],
                )
            )

        for rule in self.policy.text_rules:
            if rule.matches(text, event.phase):
                findings.append(self._finding_from_text_rule(rule))

        metrics = {
            "text": {
                "characters": len(text),
                "words": extraction.word_count,
                "sentences": extraction.sentence_count,
                "manipulation_density": round(extraction.manipulation_density, 6),
                "integrity_density": round(extraction.integrity_density, 6),
                "net_integrity": round(extraction.net_integrity, 6),
                "manipulation_categories": extraction.categories("manipulation"),
                "integrity_categories": extraction.categories("integrity"),
            },
            "aura_proxy": {
                "alignment_percent": report.alignment_percent,
                "overall_pass": report.overall_pass,
                "tes": report.tes_score,
                "vtr": report.vtr_score,
                "pai": report.pai_score,
                "needs_review_count": len(needs_review),
            },
        }
        return findings, metrics

    def _evaluate_tool(
        self, event: AssuranceEvent
    ) -> tuple[list[Finding], dict[str, Any]]:
        findings: list[Finding] = []
        name = (event.tool_name or "").strip()
        if not name:
            findings.append(
                Finding.create(
                    finding_id="LYC:TOOL:MISSING_NAME",
                    title="Tool event has no tool name",
                    description="A proposed tool action cannot be authorized without a stable tool name.",
                    severity=Severity.CRITICAL,
                    requested_disposition=Disposition.BLOCK,
                    claim_status=ClaimStatus.ACTIVE,
                    deterministic=True,
                    evaluator="tool-policy/1",
                    status_basis="Direct structural requirement for policy lookup and audit.",
                    controls=[OWASP_TOOL_MISUSE],
                )
            )
            return findings, {"tool": {"name_present": False}}

        if self.policy.tool_matches(name, self.policy.denied_tools):
            findings.append(
                Finding.create(
                    finding_id="LYC:TOOL:DENIED",
                    title="Tool denied by active policy",
                    description=f"Tool {name!r} matches the policy deny list.",
                    severity=Severity.CRITICAL,
                    requested_disposition=Disposition.BLOCK,
                    claim_status=ClaimStatus.ACTIVE,
                    deterministic=True,
                    evaluator="tool-policy/1",
                    status_basis=(
                        f"Exact declared policy {self.policy.policy_id}@{self.policy.version}."
                    ),
                    evidence=["matched_declared_deny_pattern"],
                    controls=[OWASP_TOOL_MISUSE, MCP_USER_CONTROL],
                )
            )

        if self.policy.tool_allowlist and not self.policy.tool_matches(
            name, self.policy.tool_allowlist
        ):
            findings.append(
                Finding.create(
                    finding_id="LYC:TOOL:NOT_ALLOWLISTED",
                    title="Tool blocked by policy allow-list",
                    description=f"Tool {name!r} is not covered by the configured allow-list.",
                    severity=Severity.CRITICAL,
                    requested_disposition=Disposition.BLOCK,
                    claim_status=ClaimStatus.ACTIVE,
                    deterministic=True,
                    evaluator="tool-policy/1",
                    status_basis=(
                        f"Exact declared policy {self.policy.policy_id}@{self.policy.version}."
                    ),
                    controls=[OWASP_TOOL_MISUSE, MCP_USER_CONTROL],
                )
            )

        if self.policy.tool_matches(name, self.policy.review_tools):
            findings.append(
                Finding.create(
                    finding_id="LYC:TOOL:REVIEW_PATTERN",
                    title="Tool requires policy review",
                    description=f"Tool {name!r} matches a configured review pattern.",
                    severity=Severity.HIGH,
                    requested_disposition=Disposition.REVIEW,
                    claim_status=ClaimStatus.ACTIVE,
                    deterministic=True,
                    evaluator="tool-policy/1",
                    status_basis=(
                        f"Exact declared policy {self.policy.policy_id}@{self.policy.version}."
                    ),
                    controls=[OWASP_TOOL_MISUSE, OPENAI_HUMAN_REVIEW],
                )
            )

        blocked = [
            scope
            for scope in event.scopes
            if any(fnmatch.fnmatchcase(scope, pattern) for pattern in self.policy.blocked_scopes)
        ]
        if blocked:
            findings.append(
                Finding.create(
                    finding_id="LYC:TOOL:BLOCKED_SCOPE",
                    title="Requested scope is blocked",
                    description="The tool action requests one or more scopes denied by policy.",
                    severity=Severity.CRITICAL,
                    requested_disposition=Disposition.BLOCK,
                    claim_status=ClaimStatus.ACTIVE,
                    deterministic=True,
                    evaluator="tool-policy/1",
                    status_basis=(
                        f"Exact declared policy {self.policy.policy_id}@{self.policy.version}."
                    ),
                    evidence=["blocked_scopes=" + ",".join(sorted(blocked))],
                    controls=[OWASP_TOOL_MISUSE, MCP_USER_CONTROL],
                )
            )

        if event.human_approved is False:
            findings.append(
                Finding.create(
                    finding_id="LYC:TOOL:HUMAN_DENIED",
                    title="Human reviewer rejected the action",
                    description=(
                        "The trusted caller declared an explicit human rejection. "
                        "Model-facing integrations must not populate this field themselves."
                    ),
                    severity=Severity.CRITICAL,
                    requested_disposition=Disposition.BLOCK,
                    claim_status=ClaimStatus.ACTIVE,
                    deterministic=True,
                    evaluator="tool-policy/1",
                    status_basis="Explicit rejection supplied through the trusted runtime API.",
                    controls=[OPENAI_HUMAN_REVIEW, MCP_USER_CONTROL],
                )
            )
        elif (
            event.side_effect
            and self.policy.require_approval_for_side_effects
            and event.human_approved is None
        ):
            findings.append(
                Finding.create(
                    finding_id="LYC:TOOL:APPROVAL_REQUIRED",
                    title="Side effect requires human approval",
                    description=(
                        "The proposed action declares a side effect and has no affirmative human approval."
                    ),
                    severity=Severity.HIGH,
                    requested_disposition=Disposition.REVIEW,
                    claim_status=ClaimStatus.ACTIVE,
                    deterministic=True,
                    evaluator="tool-policy/1",
                    status_basis=(
                        f"Exact declared policy {self.policy.policy_id}@{self.policy.version}."
                    ),
                    controls=[OPENAI_HUMAN_REVIEW, MCP_USER_CONTROL],
                )
            )

        sensitive_paths = sorted(
            self._sensitive_argument_paths(event.tool_arguments)
        )
        if sensitive_paths:
            findings.append(
                Finding.create(
                    finding_id="LYC:TOOL:SENSITIVE_ARGUMENTS",
                    title="Sensitive argument keys present",
                    description=(
                        "The tool arguments contain keys associated with credentials or secrets. "
                        "Presence alone does not prove misuse, but warrants review."
                    ),
                    severity=Severity.HIGH,
                    requested_disposition=Disposition.REVIEW,
                    claim_status=ClaimStatus.ACTIVE,
                    deterministic=False,
                    evaluator="argument-key-detector/1",
                    confidence=0.75,
                    status_basis="Bounded key-name detector; semantic sensitivity is inferential.",
                    evidence=["sensitive_key_count=" + str(len(sensitive_paths))],
                    controls=[OWASP_TOOL_MISUSE],
                )
            )

        metrics = {
            "tool": {
                "name_present": True,
                "scope_count": len(event.scopes),
                "side_effect": event.side_effect,
                "human_approved": event.human_approved,
                "argument_top_level_keys": len(event.tool_arguments),
                "sensitive_key_count": len(sensitive_paths),
            }
        }
        return findings, metrics

    def _finding_from_text_rule(self, rule: TextRule) -> Finding:
        return Finding.create(
            finding_id=f"POLICY:{rule.rule_id}",
            title=rule.title,
            description=rule.description,
            severity=rule.severity,
            requested_disposition=rule.requested_disposition,
            claim_status=rule.claim_status,
            deterministic=rule.deterministic,
            evaluator=f"policy-regex:{rule.rule_id}",
            status_basis=rule.status_basis,
            evidence=["configured_pattern_matched"],
        )

    def _semantic_evidence(self, extraction: Extraction) -> list[str]:
        categories = extraction.categories("manipulation")
        evidence = ["categories=" + ",".join(categories)] if categories else []
        evidence.append(
            f"manipulation_density={extraction.manipulation_density:.6f}"
        )
        if self.policy.capture_evidence_spans:
            spans = [
                signal.span[:160]
                for signal in extraction.manipulation_signals
            ][:10]
            evidence.extend(f"span={span}" for span in spans)
        return evidence

    def _event_record(self, event: AssuranceEvent) -> dict[str, Any]:
        base: dict[str, Any] = {
            "event_id": event.event_id,
            "phase": event.phase.value,
            "context_sha256": sha256_json(event.context),
            "metadata_sha256": sha256_json(event.metadata),
        }
        if event.phase in (Phase.INPUT, Phase.OUTPUT):
            content = event.content or ""
            base["subject"] = {
                "name": f"text:{event.phase.value}",
                "sha256": sha256_text(content),
                "characters": len(content),
            }
            base["replayable"] = self.policy.capture_content
            if self.policy.capture_content:
                base["content"] = content
            return base

        action = {
            "tool_name": event.tool_name,
            "tool_arguments": event.tool_arguments,
            "scopes": list(event.scopes),
            "side_effect": event.side_effect,
            "human_approved": event.human_approved,
        }
        base["subject"] = {
            "name": f"tool:{event.tool_name or 'unknown'}",
            "sha256": sha256_json(action),
        }
        base.update(
            {
                "tool_name": event.tool_name,
                "arguments_sha256": sha256_json(event.tool_arguments),
                "scopes": list(event.scopes),
                "side_effect": event.side_effect,
                "human_approved": event.human_approved,
            }
        )
        redacted_arguments, changed = redact(
            event.tool_arguments, self.policy.sensitive_argument_keys
        )
        base["replayable"] = self.policy.capture_arguments and not changed
        if self.policy.capture_arguments:
            base["arguments"] = redacted_arguments
            base["arguments_redacted"] = changed
        return base

    def _sensitive_argument_paths(
        self, value: Any, prefix: str = ""
    ) -> set[str]:
        paths: set[str] = set()
        if isinstance(value, Mapping):
            for key, item in value.items():
                path = f"{prefix}.{key}" if prefix else str(key)
                if sensitive_key(str(key), self.policy.sensitive_argument_keys):
                    paths.add(path)
                paths.update(self._sensitive_argument_paths(item, path))
        elif isinstance(value, list):
            for index, item in enumerate(value):
                paths.update(self._sensitive_argument_paths(item, f"{prefix}[{index}]"))
        return paths

    @staticmethod
    def _limitations(event_record: Mapping[str, Any]) -> tuple[str, ...]:
        limits = [
            "This receipt records a bounded runtime decision, not a safety, alignment, truth, or compliance certification.",
            "Text findings are limited to implemented cue families and proxy formulas.",
            "SHA-256 detects mutation only relative to a trusted digest; HMAC is required for shared-secret authentication.",
            "Standards references identify related concerns and do not establish conformity.",
            "Configured evidence-span capture may retain short raw-text excerpts even when full content capture is disabled.",
            "Human approval is caller-declared state; this runtime does not authenticate reviewer identity or authority.",
        ]
        if not event_record.get("replayable", False):
            limits.append(
                "Raw subject material was not retained or was redacted; exact policy replay is unavailable from this receipt alone."
            )
        return tuple(limits)
