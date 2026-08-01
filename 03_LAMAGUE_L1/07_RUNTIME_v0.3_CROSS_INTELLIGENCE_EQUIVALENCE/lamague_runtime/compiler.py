from __future__ import annotations

import re

from .model import ContextCapsule, ProgramAST
from .parser import Parser


class UnsupportedNaturalLanguage(ValueError):
    pass


class CanonicalMilestoneCompiler:
    """Narrow deterministic compiler for the first canon milestone.

    This intentionally does not claim general natural-language understanding.
    It recognizes the research pattern defined in Frontier Canon Addendum I.
    """

    REQUIRED_CONCEPTS = {
        "human": r"\bhuman(s)?\b",
        "ai": r"\bai\b|artificial intelligence",
        "claim": r"\bclaim\b|hypothesis",
        "uncertainty": r"uncertaint|unknown|unproven",
        "contribution": r"contribution|authorship|lineage",
        "evidence": r"evidence|support(ed|s)?",
        "publication": r"publish|release|share",
    }

    def __init__(self, parser: Parser | None = None) -> None:
        self.parser = parser or Parser()

    def compile(self, text: str, context: ContextCapsule | None = None) -> ProgramAST:
        lowered = text.lower()
        missing = [
            concept
            for concept, pattern in self.REQUIRED_CONCEPTS.items()
            if not re.search(pattern, lowered)
        ]
        if missing:
            raise UnsupportedNaturalLanguage(
                "v0.1 canonical compiler cannot safely infer the requested structure; "
                f"missing concepts: {', '.join(missing)}"
            )

        context = context or ContextCapsule(
            domain="human-ai semantic research",
            participants=["human collaborators", "AI collaborators"],
            affected_parties=["future testers", "future users"],
            purpose="test an unproven semantic language architecture without overstating evidence",
            claim="LAMAGUE may improve inspectable human-AI collaboration",
            evidence=[
                "LAMAGUE-1C prototype exists",
                "machine registries exist",
                "Frontier Canon Addendum I specifies the architecture",
            ],
            evidence_score=0.45,
            certainty=0.35,
            unknowns=[
                "human learnability",
                "net semantic compression",
                "cross-model consistency",
                "long-term usefulness",
            ],
            authority=[
                "project steward may publish prototype artefacts",
                "test participants govern their own participation",
            ],
            consent={"test participants": "required and revocable"},
            boundaries=[
                "prototype claims remain experimental",
                "no real-world action execution",
            ],
            invariants=[
                "uncertainty remains visible",
                "human and AI contributions remain visible",
                "publication certainty does not exceed evidence",
            ],
            value_created=["testable structure", "public evidence", "shared learning"],
            costs=["time", "attention", "computation", "reputational risk"],
            risks=["overclaiming", "semantic ambiguity", "decoder disagreement"],
            consequences=[
                "evidence may strengthen, revise, or reject components",
                "weak forms return to repair or ASH",
            ],
            consequence_horizon="prototype, independent testing, and later replication",
            recovery=[
                "expand compressed seals",
                "publish audit findings",
                "repair or return weak forms to ASH",
            ],
            provenance=["Frontier Canon Addendum I", "canonical first milestone compiler"],
            risk_level="medium",
            irreversible=False,
            execute_requested=True,
        )
        return self.parser.parse("FORGE_TRUTH", context)
