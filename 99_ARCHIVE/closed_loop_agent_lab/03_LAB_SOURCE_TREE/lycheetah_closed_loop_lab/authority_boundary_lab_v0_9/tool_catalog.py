"""Trusted tool catalog + strict proposal stamping for the Lycheetah agent lab.

Research scaffold, not an authorization service. The host must keep the catalog,
policy file, action file, approval issuer and provider credentials outside the
model's write/control boundary.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from dataclasses import dataclass
from pathlib import Path
from types import MappingProxyType
from typing import Any, Mapping

SCHEMA = "lycheetah-tool-catalog/0.1"
TOOL_NAME_RE = re.compile(r"^[a-z][a-z0-9_]*(?:\.[a-z][a-z0-9_]*)*$")


def canonical(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False).encode("utf-8")


def sha256(value: Any) -> str:
    return hashlib.sha256(canonical(value)).hexdigest()


@dataclass(frozen=True)
class Field:
    kind: str
    required: bool = True
    choices: tuple[str, ...] = ()
    minimum: int | None = None

    def to_dict(self) -> dict[str, Any]:
        return {"kind": self.kind, "required": self.required, "choices": list(self.choices), "minimum": self.minimum}


@dataclass(frozen=True)
class ToolSpec:
    name: str
    dispatcher_id: str
    dispatcher_version: str
    side_effect: bool
    scopes: tuple[str, ...]
    fields: Mapping[str, Field]
    description: str

    def __post_init__(self) -> None:
        # Freeze the mapping as well as the dataclass fields; a mutable dict here
        # could change the live schema without changing the catalog digest.
        object.__setattr__(self, "fields", MappingProxyType(dict(self.fields)))

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "dispatcher_id": self.dispatcher_id,
            "dispatcher_version": self.dispatcher_version,
            "side_effect": self.side_effect,
            "scopes": list(self.scopes),
            "fields": {name: field.to_dict() for name, field in sorted(self.fields.items())},
            "description": self.description,
        }


class ProposalError(ValueError):
    pass


class ToolCatalog:
    def __init__(self, tools: tuple[ToolSpec, ...]):
        mapping: dict[str, ToolSpec] = {}
        for spec in tools:
            if not TOOL_NAME_RE.fullmatch(spec.name):
                raise ValueError(f"invalid canonical tool name: {spec.name!r}")
            if spec.name in mapping:
                raise ValueError(f"duplicate tool name: {spec.name}")
            if not spec.dispatcher_id or not spec.dispatcher_version or not spec.scopes:
                raise ValueError(f"incomplete trusted metadata for {spec.name}")
            mapping[spec.name] = spec
        self._tools = MappingProxyType(mapping)
        self.revision = SCHEMA
        self.digest = sha256({"schema": SCHEMA, "tools": [mapping[name].to_dict() for name in sorted(mapping)]})

    def get(self, name: str) -> ToolSpec:
        if not isinstance(name, str) or name not in self._tools:
            raise ProposalError("unknown-tool")
        return self._tools[name]

    def stamp(
        self,
        proposal: Mapping[str, Any],
        *,
        operation_id: str,
        agent_id: str,
        workspace_id: str,
    ) -> dict[str, Any]:
        """Build an authoritative action from the minimal model proposal.

        The model may choose a tool name and arguments. It may not classify effects,
        choose scopes, select a dispatcher, name an agent/workspace, or choose the
        operation ID. Those are supplied by this trusted host and catalog.
        """
        if not isinstance(proposal, Mapping) or set(proposal) != {"tool_name", "arguments"}:
            raise ProposalError("proposal-schema-must-contain-only-tool_name-and-arguments")
        tool_name = proposal["tool_name"]
        if not isinstance(tool_name, str):
            raise ProposalError("tool_name-must-be-string")
        spec = self.get(tool_name)
        arguments = proposal["arguments"]
        if not isinstance(arguments, Mapping):
            raise ProposalError("arguments-must-be-object")
        unknown = set(arguments) - set(spec.fields)
        missing = {name for name, field in spec.fields.items() if field.required and name not in arguments}
        if unknown:
            raise ProposalError("unknown-argument-fields:" + ",".join(sorted(unknown)))
        if missing:
            raise ProposalError("missing-argument-fields:" + ",".join(sorted(missing)))
        self._validate_fields(spec, arguments)
        if not all(isinstance(value, str) and value.strip() for value in (operation_id, agent_id, workspace_id)):
            raise ProposalError("trusted-context-fields-must-be-non-empty-strings")
        # Shape is intentionally compatible with the v0.7 single fake refund route.
        # Side effect, scope and route are never copied from the model proposal.
        return {
            "agent_id": agent_id,
            "operation_id": operation_id,
            "tool_name": spec.name,
            "arguments": dict(arguments),
            "scopes": list(spec.scopes),
            "workspace_id": workspace_id,
            "dispatcher_id": spec.dispatcher_id,
            "dispatcher_version": spec.dispatcher_version,
            "side_effect": spec.side_effect,
            "catalog_sha256": self.digest,
        }

    @staticmethod
    def _validate_fields(spec: ToolSpec, args: Mapping[str, Any]) -> None:
        for key, field in spec.fields.items():
            if key not in args:
                continue
            value = args[key]
            if field.kind == "string":
                if not isinstance(value, str) or not value.strip():
                    raise ProposalError(f"invalid-field:{key}:expected-non-empty-string")
            elif field.kind == "int":
                # bool is a subclass of int in Python, but must not be an amount.
                if type(value) is not int:
                    raise ProposalError(f"invalid-field:{key}:expected-integer-not-bool")
                if field.minimum is not None and value < field.minimum:
                    raise ProposalError(f"invalid-field:{key}:below-minimum")
            else:
                raise ValueError(f"unsupported field kind in trusted catalog: {field.kind}")
            if field.choices and value not in field.choices:
                raise ProposalError(f"invalid-field:{key}:unsupported-choice")


DEFAULT_CATALOG = ToolCatalog((
    ToolSpec(
        name="refund_order",
        dispatcher_id="fake-provider.refund",
        dispatcher_version="1",
        side_effect=True,
        scopes=("orders:refund",),
        fields={
            "order_id": Field("string"),
            "amount_minor": Field("int", minimum=1),
            "currency": Field("string", choices=("NZD", "USD")),
        },
        description="Issue a simulated refund; always consequential in this lab.",
    ),
    ToolSpec(
        name="read_order",
        dispatcher_id="fake-provider.order-read",
        dispatcher_version="1",
        side_effect=False,
        scopes=("orders:read",),
        fields={"order_id": Field("string")},
        description="Read a simulated order; no side effect in this lab catalog.",
    ),
))


def check_policy_catalog_binding(policy_path: str | Path, catalog: ToolCatalog = None) -> dict[str, Any]:
    catalog = catalog or DEFAULT_CATALOG
    try:
        policy = json.loads(Path(policy_path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ProposalError("cannot-load-policy-file") from exc
    return validate_policy_binding(policy, catalog)


def validate_policy_binding(policy: Mapping[str, Any], catalog: ToolCatalog = None) -> dict[str, Any]:
    """Validate the small lab policy contract and bind it to the trusted catalog."""
    catalog = catalog or DEFAULT_CATALOG
    if not isinstance(policy, Mapping):
        raise ProposalError("policy-must-be-json-object")
    required = {"policy_id", "version", "refund_requires_host_approval", "tool_catalog_sha256"}
    if set(policy) != required:
        raise ProposalError("policy-schema-mismatch")
    if not isinstance(policy["policy_id"], str) or not policy["policy_id"].strip():
        raise ProposalError("invalid-policy-id")
    if type(policy["version"]) is not int or policy["version"] < 1:
        raise ProposalError("invalid-policy-version")
    if type(policy["refund_requires_host_approval"]) is not bool or policy["refund_requires_host_approval"] is not True:
        raise ProposalError("lab-policy-must-require-host-approval")
    if policy["tool_catalog_sha256"] != catalog.digest:
        raise ProposalError("policy-tool-catalog-digest-mismatch")
    return dict(policy)


def validate_stamped_action(action: Mapping[str, Any], catalog: ToolCatalog = None, *, consequential_only: bool = False) -> dict[str, Any]:
    """Re-derive trusted metadata and reject an action not produced by this catalog.

    This must be called at approval issuance and again at dispatch/provider boundaries;
    merely calling it in a separate stamping utility is not sufficient.
    """
    catalog = catalog or DEFAULT_CATALOG
    required = {"agent_id", "operation_id", "tool_name", "arguments", "scopes", "workspace_id", "dispatcher_id", "dispatcher_version", "side_effect", "catalog_sha256"}
    if not isinstance(action, Mapping) or set(action) != required:
        raise ProposalError("stamped-action-schema-mismatch")
    if action["catalog_sha256"] != catalog.digest:
        raise ProposalError("stamped-action-catalog-digest-mismatch")
    if type(action["side_effect"]) is not bool or not isinstance(action["scopes"], list):
        raise ProposalError("stamped-action-metadata-type-invalid")
    for key in ("agent_id", "operation_id", "workspace_id"):
        if not isinstance(action[key], str) or not action[key].strip():
            raise ProposalError("stamped-action-context-invalid:" + key)
    expected = catalog.stamp(
        {"tool_name": action["tool_name"], "arguments": action["arguments"]},
        operation_id=action["operation_id"],
        agent_id=action["agent_id"],
        workspace_id=action["workspace_id"],
    )
    if dict(action) != expected:
        raise ProposalError("stamped-action-metadata-mismatch")
    if consequential_only and action["side_effect"] is not True:
        raise ProposalError("consequential-dispatch-requires-side-effect-tool")
    return dict(action)


def main() -> int:
    parser = argparse.ArgumentParser(description="Stamp a model proposal using trusted catalog metadata")
    parser.add_argument("proposal_file")
    parser.add_argument("policy_file")
    parser.add_argument("output_action_file")
    parser.add_argument("--operation-id", required=True, help="Host-generated stable operation identifier")
    parser.add_argument("--agent-id", required=True, help="Trusted host identity for this agent session")
    parser.add_argument("--workspace-id", required=True, help="Trusted isolated workspace identifier")
    args = parser.parse_args()
    check_policy_catalog_binding(args.policy_file)
    proposal = json.loads(Path(args.proposal_file).read_text(encoding="utf-8"))
    action = DEFAULT_CATALOG.stamp(proposal, operation_id=args.operation_id, agent_id=args.agent_id, workspace_id=args.workspace_id)
    destination = Path(args.output_action_file)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(action, sort_keys=True, indent=2), encoding="utf-8")
    print(json.dumps({"status":"stamped","tool_name":action["tool_name"],"side_effect_from_trusted_catalog":action["side_effect"],"catalog_sha256":DEFAULT_CATALOG.digest,"action_sha256":sha256(action)}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
