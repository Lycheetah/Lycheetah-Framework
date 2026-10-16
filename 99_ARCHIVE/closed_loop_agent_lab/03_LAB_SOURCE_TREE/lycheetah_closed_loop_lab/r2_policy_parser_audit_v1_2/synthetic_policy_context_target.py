# synthetic preflight only
# synthetic preflight only
# synthetic preflight only
# synthetic preflight only
# synthetic preflight only
# synthetic preflight only
# synthetic preflight only
# synthetic preflight only
# synthetic preflight only
# synthetic preflight only
# synthetic preflight only
# synthetic preflight only
# synthetic preflight only
# synthetic preflight only
# synthetic preflight only
# synthetic preflight only
# synthetic preflight only
# synthetic preflight only
# synthetic preflight only
# synthetic preflight only
# synthetic preflight only
# synthetic preflight only
# synthetic preflight only
# synthetic preflight only
# synthetic preflight only
# synthetic preflight only
# synthetic preflight only
# synthetic preflight only
# synthetic preflight only
# synthetic preflight only
# synthetic preflight only
# synthetic preflight only
# synthetic preflight only
# synthetic preflight only
# synthetic preflight only
# synthetic preflight only
# synthetic preflight only
# synthetic preflight only
# synthetic preflight only
# synthetic preflight only
# synthetic preflight only
# synthetic preflight only
# synthetic preflight only
# synthetic preflight only
# synthetic preflight only
# synthetic preflight only
# synthetic preflight only
# synthetic preflight only
# synthetic preflight only
# synthetic preflight only
# synthetic preflight only
# synthetic preflight only
# synthetic preflight only
# synthetic preflight only
# synthetic preflight only
# synthetic preflight only
# synthetic preflight only
# synthetic preflight only
# synthetic preflight only
# synthetic preflight only
# synthetic preflight only
# synthetic preflight only
# synthetic preflight only
# synthetic preflight only
# synthetic preflight only
# synthetic preflight only
# synthetic preflight only
# synthetic preflight only
# synthetic preflight only
# synthetic preflight only
# synthetic preflight only
# synthetic preflight only
# synthetic preflight only
# synthetic preflight only
# synthetic preflight only
# synthetic preflight only
# synthetic preflight only
# synthetic preflight only
# synthetic preflight only
# synthetic preflight only
# synthetic preflight only
# synthetic preflight only
# synthetic preflight only
# synthetic preflight only
# synthetic preflight only
# synthetic preflight only
# synthetic preflight only
# synthetic preflight only
# synthetic preflight only
# synthetic preflight only
# synthetic preflight only
# synthetic preflight only
# synthetic preflight only
# synthetic preflight only
# synthetic preflight only
# synthetic preflight only
# synthetic preflight only
# synthetic preflight only
# synthetic preflight only
    rule_id: str
    pattern: str
    title: str
    description: str
    phases: tuple[Phase, ...] = (Phase.INPUT, Phase.OUTPUT)
    requested_disposition: Disposition = Disposition.REVIEW
    claim_status: ClaimStatus = ClaimStatus.SCAFFOLD
    deterministic: bool = False
    severity: Severity = Severity.MEDIUM
    status_basis: str = ""
    ignore_case: bool = True

    def __post_init__(self) -> None:
        if not isinstance(self.rule_id, str) or not isinstance(self.pattern, str):
            raise PolicyError("text rule id and pattern must be strings")
        if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._:-]{2,127}", self.rule_id):
            raise PolicyError(f"invalid text rule id: {self.rule_id!r}")
        if not self.pattern:
            raise PolicyError(f"text rule {self.rule_id!r} pattern must be non-empty")
        if len(self.pattern) > 4096:
            raise PolicyError(f"text rule {self.rule_id!r} pattern exceeds 4096 characters")
        if not self.phases or any(
            not isinstance(phase, Phase) or phase not in (Phase.INPUT, Phase.OUTPUT)
            for phase in self.phases
        ):
            raise PolicyError(f"text rule {self.rule_id!r} phases must contain input and/or output")
        if type(self.deterministic) is not bool or type(self.ignore_case) is not bool:
            raise PolicyError(
                f"text rule {self.rule_id!r} deterministic and ignore_case must be booleans"
            )
        try:
            re.compile(self.pattern, re.IGNORECASE if self.ignore_case else 0)
        except re.error as exc:
            raise PolicyError(f"invalid regex in {self.rule_id}: {exc}") from exc
        if self.claim_status == ClaimStatus.ACTIVE and not self.status_basis.strip():
            raise PolicyError(f"ACTIVE rule {self.rule_id!r} requires a non-empty status_basis")

    def matches(self, text: str, phase: Phase) -> bool:
        if phase not in self.phases:
            return False
        flags = re.IGNORECASE if self.ignore_case else 0
        return re.search(self.pattern, text, flags) is not None

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.rule_id,
            "pattern": self.pattern,
            "title": self.title,
            "description": self.description,
            "phases": [phase.value for phase in self.phases],
            "requested_disposition": self.requested_disposition.value,
            "claim_status": self.claim_status.value,
            "deterministic": self.deterministic,
            "severity": self.severity.value,
            "status_basis": self.status_basis,
            "ignore_case": self.ignore_case,
        }

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> TextRule:
        data = _mapping(data, "text rule")
        _reject_unknown(
            data,
            {
                "id",
                "pattern",
                "title",
                "description",
                "phases",
                "requested_disposition",
                "claim_status",
                "deterministic",
                "severity",
                "status_basis",
                "ignore_case",
            },
            "text rule",
        )
        if "id" not in data or "pattern" not in data:
            raise PolicyError("text rule requires id and pattern")
        phases = _strings(data.get("phases", ["input", "output"]), "text rule.phases")
        return cls(
            rule_id=str(data["id"]),
            pattern=str(data["pattern"]),
            title=str(data.get("title", data["id"])),
            description=str(data.get("description", "Policy text rule matched")),
            phases=tuple(Phase(item) for item in phases),
            requested_disposition=Disposition(data.get("requested_disposition", "REVIEW")),
            claim_status=ClaimStatus(data.get("claim_status", "SCAFFOLD")),
            deterministic=_boolean(data.get("deterministic", False), "text rule.deterministic"),
            severity=Severity(data.get("severity", "MEDIUM")),
            status_basis=str(data.get("status_basis", "")),
            ignore_case=_boolean(data.get("ignore_case", True), "text rule.ignore_case"),
        )
