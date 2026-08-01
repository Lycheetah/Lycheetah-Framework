from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
from typing import Any

from .auditor import ConstitutionalAuditor
from .breathing import BreathingCompression
from .dissent import normalize_dissent
from .explainer import Explainer
from .memory import memory_record
from .model import AuditOutcome, CompressionMode, ExecutionResult, ProgramAST
from .semantic_hash import semantic_hash
from .value_ledger import normalize_value_entries


class AbstractInterpreter:
    """Executes only over an in-memory abstract state record."""

    def __init__(self) -> None:
        self.auditor = ConstitutionalAuditor()
        self.explainer = Explainer()
        self.breathing = BreathingCompression()

    def execute(self, ast: ProgramAST, initial_state: dict[str, Any] | None = None) -> ExecutionResult:
        audit = self.auditor.audit(ast)
        compression = self.breathing.decide(ast)
        sem_hash = semantic_hash(ast)
        state: dict[str, Any] = deepcopy(initial_state or {})
        for key, default in {
            "observations": [],
            "evidence": [],
            "unknowns": [],
            "invariants": [],
            "transitions": [],
            "memory": [],
            "outputs": [],
            "operations_applied": [],
            "dissent": [],
            "value_ledger": [],
        }.items():
            state.setdefault(key, deepcopy(default))
        state["semantic_hash"] = sem_hash
        state["compression_mode"] = compression.mode.value
        trace: list[dict[str, Any]] = []

        if "Z" in ast.operation_path and compression.mode is not CompressionMode.COMPRESS:
            trace.append({
                "event": "compression_refused",
                "mode": compression.mode.value,
                "reasons": compression.reasons,
                "time": datetime.now(timezone.utc).isoformat(),
            })
            return ExecutionResult(
                executed=False,
                state=state,
                audit=audit,
                trace=trace,
                explanation=self.explainer.explain(ast),
                semantic_hash=sem_hash,
                compression=compression,
            )

        if audit.outcome is not AuditOutcome.VALID:
            trace.append({
                "event": "execution_blocked",
                "audit_outcome": audit.outcome.value,
                "time": datetime.now(timezone.utc).isoformat(),
            })
            return ExecutionResult(
                executed=False,
                state=state,
                audit=audit,
                trace=trace,
                explanation=self.explainer.explain(ast),
                semantic_hash=sem_hash,
                compression=compression,
            )

        ctx = ast.context
        state["dissent"] = normalize_dissent(ctx.dissent)
        state["value_ledger"] = normalize_value_entries(ctx.value_ledger)

        for node in ast.nodes:
            op = node.operation
            state["operations_applied"].append(op)
            event: dict[str, Any] = {
                "node_id": node.node_id,
                "operation": op,
                "operation_name": node.operation_name,
                "time": datetime.now(timezone.utc).isoformat(),
            }
            if op == "Q":
                state.setdefault("queries", []).append(ctx.claim or ctx.purpose or "unresolved target")
            elif op == "O":
                state["observations"].append({
                    "target": ctx.claim or ctx.purpose,
                    "domain": ctx.domain,
                    "provenance": ctx.provenance,
                })
            elif op == "E":
                state["evidence"].extend(x for x in ctx.evidence if x not in state["evidence"])
            elif op == "U":
                typed = node.arguments.get("type")
                values = [typed] if typed else ctx.unknowns
                for value in values:
                    if value and value not in state["unknowns"]:
                        state["unknowns"].append(value)
            elif op == "I":
                state["invariants"].extend(x for x in ctx.invariants if x not in state["invariants"])
            elif op == "G":
                state["guard"] = {
                    "passed": True,
                    "authority": ctx.authority,
                    "boundaries": ctx.boundaries,
                }
            elif op == "W":
                state["weave"] = {
                    "participants": ctx.participants,
                    "identity_merged": False,
                    "dissent_preserved": bool(state["dissent"]),
                }
            elif op == "M":
                state["merge"] = {
                    "performed": True,
                    "dissent_preserved": bool(state["dissent"]),
                    "policy": node.arguments.get("policy", "preserve-visible-difference"),
                }
            elif op == "T":
                transition = {
                    "purpose": ctx.purpose,
                    "from": state.get("phase", "input"),
                    "to": "evaluated",
                    "invariants": list(state["invariants"]),
                }
                state["transitions"].append(transition)
                state["phase"] = "evaluated"
            elif op == "P":
                if not ctx.evidence:
                    state["proof_status"] = "under-determined"
                elif ctx.unknowns:
                    state["proof_status"] = "context-limited"
                else:
                    state["proof_status"] = "supported"
            elif op == "F":
                record = memory_record(ast).to_dict()
                record["claim"] = ctx.claim
                record["residue"] = list(ctx.unknowns)
                state["memory"].append(record)
            elif op == "X":
                entry = dict(node.value_flow)
                if entry and entry not in state["value_ledger"]:
                    state["value_ledger"].append(entry)
            elif op == "Z":
                state["compressed"] = {
                    "semantic_hash": sem_hash,
                    "recoverable": True,
                    "mode": compression.mode.value,
                }
            elif op == "Y":
                state["outputs"].append({
                    "claim": ctx.claim,
                    "proof_status": state.get("proof_status", "not-requested"),
                    "scope": ctx.domain,
                    "unknowns": list(state["unknowns"]),
                    "semantic_hash": sem_hash,
                    "dissent": deepcopy(state["dissent"]),
                    "value_ledger": deepcopy(state["value_ledger"]),
                })
            else:
                state.setdefault("generic_records", []).append({
                    "operation": op,
                    "arguments": node.arguments,
                })
            event["state_digest"] = {
                "phase": state.get("phase"),
                "proof_status": state.get("proof_status"),
                "unknown_count": len(state["unknowns"]),
                "dissent_count": len(state["dissent"]),
                "value_entries": len(state["value_ledger"]),
                "output_count": len(state["outputs"]),
                "semantic_hash": sem_hash,
            }
            trace.append(event)

        return ExecutionResult(
            executed=True,
            state=state,
            audit=audit,
            trace=trace,
            explanation=self.explainer.explain(ast),
            semantic_hash=sem_hash,
            compression=compression,
        )
