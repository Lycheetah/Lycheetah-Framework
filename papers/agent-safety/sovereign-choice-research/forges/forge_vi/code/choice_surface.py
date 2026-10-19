"""Sovereign Choice Surface Audit — observable interface properties, not a human agency score.

A signed choice cannot prove that the person understood the options presented.
This inspector makes explicit observations about a *specified UI fixture*.
Unknown remains unknown; fail is not a diagnosis of any person's free will.
"""
from __future__ import annotations
from dataclasses import dataclass, asdict
from typing import Literal

Tri = Literal["present", "absent", "unknown"]

@dataclass(frozen=True)
class ChoiceSurface:
    """Each property requires evidence from an interaction or design review."""
    accurate_purpose: Tri = "unknown"
    meaningful_no_action: Tri = "unknown"
    visible_revision: Tri = "unknown"
    honest_costs: Tri = "unknown"
    custom_alternative: Tri = "unknown"
    review_before_effect: Tri = "unknown"
    nonpunitive_exit: Tri = "unknown"
    accessible_comprehension: Tri = "unknown"
    dependency_pressure: Tri = "unknown"  # present = a defect / red flag

    def __post_init__(self):
        for k,v in asdict(self).items():
            if v not in ("present", "absent", "unknown"):
                raise ValueError(f"invalid evidence status for {k}: {v!r}")

    def audit(self) -> dict:
        checks = asdict(self)
        problematic = [k for k,v in checks.items()
                       if (v=="present" if k=="dependency_pressure" else v=="absent")]
        unknown = [k for k,v in checks.items() if v=="unknown"]
        observed = [k for k,v in checks.items()
                    if (v=="absent" if k=="dependency_pressure" else v=="present")]
        return {
            "status": "OBSERVATIONAL_INTERFACE_CHECK_ONLY",
            "observed_supports": observed,
            "red_flags": problematic,
            "unknowns": unknown,
            "human_free_will_score": None,
            "identity_or_consent_proven": False,
            "interpretation": ("No red flags observed in supplied fields, but this is not "
                               "evidence of informed or uncoerced consent."
                               if not problematic else
                               "Specified interface contains one or more agency-related red flags.")
        }
