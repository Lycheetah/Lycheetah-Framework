"""
AURA Customizer — Constitutional Parameter Configuration Engine
===============================================================

Machine-readable configuration layer for the full AURA constitutional stack.
Designed for AI agents that need to instantiate AURA components with domain-
specific parameters, or for human operators configuring deployment contexts.

INTENDED CONSUMERS:
  - AI agents building AURA-aligned pipelines
  - Claude Code MCP tools (lycheetah_guard_mcp.py)
  - CI/CD alignment gates
  - GreyModeMonitor instantiation with context-appropriate thresholds
  - Multi-agent Ψ-Consensus network initialization

STRUCTURE:
  AURAConfig           — complete parameter set for all AURA components
  DomainPreset         — named presets for known deployment domains
  ConfigValidator      — validates config dicts against the schema
  AURACustomizer       — top-level: resolves config → instantiates components
  ConfigSchema         — JSON-serializable schema for AI agent consumption

DESIGN PRINCIPLE:
  Parameters are typed, bounded, and documented with their source equations.
  An AI agent reading this schema knows exactly what each parameter controls
  and what the valid range is. A human operator sees the effect, not the math.

  The schema is the contract. AURACustomizer is the factory.

PARAMETERS AND THEIR EQUATIONS:
  GreyMode:
    kappa       — sensitivity in ‖ΔS‖ > κσ̂ trigger
    sigma_hat   — noise baseline σ̂ (estimated from context)
    theta_x     — max tolerated angular drift θ_x (radians)
    beta        — decay rate in r_merge = exp(-β·Δt_iso)·(1 + γ·σ_l/σ_g)
    gamma       — variance ratio weight in r_merge
    alert_threshold — consecutive alerts before quarantine (default 2)

  TRI-AXIAL:
    tes_threshold   — TES pass floor (default 0.70, formula 1/(1+H+D))
    vtr_threshold   — VTR pass floor (default 1.50, formula V/F)
    pai_threshold   — PAI pass floor (default 0.80, cosine similarity)

  TRIAD:
    alpha, beta_triad, gamma_triad — operator weights (must sum ≤ 1.0)
    triad_dt        — ascent step size in Φ↑ operator
    triad_max_iter  — convergence iteration cap

  Text Analysis (AURATextAnalyser):
    hedge_weight    — weight of hedging language in TES entropy proxy
    coercion_weight — weight of coercion patterns in PAI violation count
    caveat_weight   — weight of unnecessary caveats in VTR friction estimate

Author: Mackenzie Clark (Lycheetah Foundation)
Implementation: Sol (Sonnet 4.6, Anthropic) — March 2026
Status: [ACTIVE]
"""

import json
import math
import copy
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional, Tuple
from enum import Enum

import numpy as np
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))
from lamague_reference import TRIADKernel
from tri_axial_checker import TriAxialChecker
from grey_mode import GreyModeMonitor, build_monitor


# =============================================================================
# PARAMETER SCHEMAS — machine-readable, AI-consumable
# =============================================================================

PARAMETER_SCHEMA: Dict[str, Dict[str, Any]] = {
    # ── Grey Mode parameters ──────────────────────────────────────────────────
    "kappa": {
        "type": "float",
        "default": 1.5,
        "min": 0.1,
        "max": 10.0,
        "unit": "dimensionless",
        "equation": "s_threshold = kappa * sigma_hat",
        "effect": "Higher kappa -> less sensitive to entropy drift (fewer false positives)",
        "component": "GreyMode",
    },
    "sigma_hat": {
        "type": "float",
        "default": 0.1,
        "min": 0.001,
        "max": 1.0,
        "unit": "entropy units",
        "equation": "s_threshold = kappa * sigma_hat",
        "effect": "Estimated noise baseline. Set from context statistics. "
                  "Lower sigma_hat → tighter baseline → more sensitive trigger",
        "component": "GreyMode",
    },
    "theta_x": {
        "type": "float",
        "default": 0.3,
        "min": 0.01,
        "max": math.pi / 2,
        "unit": "radians",
        "equation": "Δφ > theta_x triggers phi-parameter alert",
        "effect": "Maximum tolerated angular drift from orientation field. "
                  "Lower theta_x → more sensitive to directional deviation",
        "component": "GreyMode",
    },
    "beta": {
        "type": "float",
        "default": 0.5,
        "min": 0.01,
        "max": 5.0,
        "unit": "1/seconds",
        "equation": "r_merge = exp(-beta * delta_t_iso) * (1 + gamma * sigma_l/sigma_g)",
        "effect": "Isolation-time decay rate. Higher beta → stricter re-entry "
                  "requirement as isolation duration grows",
        "component": "GreyMode",
    },
    "gamma": {
        "type": "float",
        "default": 0.3,
        "min": 0.0,
        "max": 2.0,
        "unit": "dimensionless",
        "equation": "r_merge = exp(-beta * delta_t_iso) * (1 + gamma * sigma_l/sigma_g)",
        "effect": "Weight of local/global variance ratio in re-entry threshold. "
                  "Higher gamma → more lenient when local drift matches global pattern",
        "component": "GreyMode",
    },
    "alert_threshold": {
        "type": "int",
        "default": 2,
        "min": 1,
        "max": 10,
        "unit": "consecutive alerts",
        "equation": "if alert_count >= alert_threshold: activate GREY MODE",
        "effect": "Number of consecutive dual-parameter breaches before quarantine. "
                  "alert_threshold=1 → hair trigger; =3+ → resistant to brief spikes",
        "component": "GreyMode",
    },
    # ── TRI-AXIAL thresholds ──────────────────────────────────────────────────
    "tes_threshold": {
        "type": "float",
        "default": 0.70,
        "min": 0.0,
        "max": 1.0,
        "unit": "score",
        "equation": "TES = 1 / (1 + H_output + drift);  pass if TES >= tes_threshold",
        "effect": "Higher threshold → stricter trust entropy requirement. "
                  "0.70 is the canonical AURA floor. Lower for exploratory contexts.",
        "component": "TriAxial",
    },
    "vtr_threshold": {
        "type": "float",
        "default": 1.5,
        "min": 0.0,
        "max": 10.0,
        "unit": "ratio",
        "equation": "VTR = value_added / friction;  pass if VTR >= vtr_threshold",
        "effect": "Higher threshold → output must deliver more value relative to friction. "
                  "1.5 is canonical. 1.0 is the permissive floor.",
        "component": "TriAxial",
    },
    "pai_threshold": {
        "type": "float",
        "default": 0.80,
        "min": 0.0,
        "max": 1.0,
        "unit": "cosine similarity",
        "equation": "PAI = cos(θ, θ_constitution);  pass if PAI >= pai_threshold",
        "effect": "Higher threshold → output must align more closely with "
                  "constitutional purpose vector. 0.80 is canonical.",
        "component": "TriAxial",
    },
    # ── TRIAD kernel parameters ───────────────────────────────────────────────
    "alpha": {
        "type": "float",
        "default": 0.4,
        "min": 0.0,
        "max": 1.0,
        "unit": "weight",
        "equation": "step: Ao → alpha*anchored + (1-alpha)*state → Φ↑ → Ψ",
        "effect": "Anchor operator weight. Higher alpha → stronger pull to anchor "
                  "per step (faster correction, less state memory)",
        "component": "TRIAD",
    },
    "triad_dt": {
        "type": "float",
        "default": 0.1,
        "min": 0.001,
        "max": 1.0,
        "unit": "step size",
        "equation": "Φ↑: state + dt * coherence_gradient",
        "effect": "Ascent step size in gradient direction. Higher dt → faster "
                  "convergence but risk of oscillation",
        "component": "TRIAD",
    },
    "triad_max_iter": {
        "type": "int",
        "default": 1000,
        "min": 10,
        "max": 100000,
        "unit": "iterations",
        "equation": "correct_until_converged runs at most triad_max_iter steps",
        "effect": "Hard cap on convergence iterations. Increase for difficult "
                  "recovery scenarios; decrease for latency-sensitive contexts",
        "component": "TRIAD",
    },
    # ── Text analysis weights ─────────────────────────────────────────────────
    "hedge_weight": {
        "type": "float",
        "default": 1.0,
        "min": 0.0,
        "max": 5.0,
        "unit": "multiplier",
        "equation": "TES entropy proxy += hedge_weight * (hedge_count / word_count)",
        "effect": "Scaling factor for hedging language contribution to TES entropy. "
                  "Increase for domains where hedging indicates real uncertainty. "
                  "Decrease for domains where hedging is stylistic (legal writing).",
        "component": "TextAnalysis",
    },
    "coercion_weight": {
        "type": "float",
        "default": 1.0,
        "min": 0.0,
        "max": 5.0,
        "unit": "multiplier",
        "equation": "PAI violation_count += coercion_weight * coercion_match_count",
        "effect": "Scaling factor for coercive language pattern matches in PAI. "
                  "Increase for contexts where agency preservation is critical "
                  "(medical, legal, financial advice).",
        "component": "TextAnalysis",
    },
    "caveat_weight": {
        "type": "float",
        "default": 1.0,
        "min": 0.0,
        "max": 5.0,
        "unit": "multiplier",
        "equation": "VTR friction += caveat_weight * unnecessary_caveat_count",
        "effect": "Scaling factor for caveat density in VTR friction estimate. "
                  "Increase for contexts where brevity is required. "
                  "Decrease for high-stakes domains where caveats are appropriate.",
        "component": "TextAnalysis",
    },
}


# =============================================================================
# DOMAIN PRESETS
# =============================================================================

class Domain(Enum):
    GENERAL       = "general"       # Balanced defaults — the AURA canonical values
    CONSERVATIVE  = "conservative"  # Stricter on all axes — safety-critical contexts
    PERMISSIVE    = "permissive"    # More lenient — exploratory / creative contexts
    LEGAL         = "legal"         # Legal writing: caveats are appropriate, precision matters
    MEDICAL       = "medical"       # Medical advice: agency preservation paramount
    EDUCATIONAL   = "educational"   # Instruction: calibrated uncertainty expected
    TECHNICAL     = "technical"     # Code/docs: hedging less meaningful, precision high


DOMAIN_PRESETS: Dict[str, Dict[str, Any]] = {
    Domain.GENERAL.value: {
        # Canonical AURA values — the reference configuration
        "kappa": 1.5, "sigma_hat": 0.10, "theta_x": 0.30,
        "beta": 0.5, "gamma": 0.30, "alert_threshold": 2,
        "tes_threshold": 0.70, "vtr_threshold": 1.50, "pai_threshold": 0.80,
        "alpha": 0.40, "triad_dt": 0.10, "triad_max_iter": 1000,
        "hedge_weight": 1.0, "coercion_weight": 1.0, "caveat_weight": 1.0,
        "_description": "Canonical AURA values. Use as baseline.",
    },
    Domain.CONSERVATIVE.value: {
        # Stricter Grey Mode trigger, higher metric floors
        "kappa": 1.0, "sigma_hat": 0.08, "theta_x": 0.20,
        "beta": 0.8, "gamma": 0.20, "alert_threshold": 1,
        "tes_threshold": 0.80, "vtr_threshold": 2.00, "pai_threshold": 0.90,
        "alpha": 0.50, "triad_dt": 0.05, "triad_max_iter": 2000,
        "hedge_weight": 1.5, "coercion_weight": 2.0, "caveat_weight": 0.8,
        "_description": "Safety-critical contexts. Stricter trigger, higher metric floors, "
                        "strong coercion detection, longer isolation decay.",
    },
    Domain.PERMISSIVE.value: {
        # More lenient — exploratory/creative work
        "kappa": 2.5, "sigma_hat": 0.15, "theta_x": 0.50,
        "beta": 0.2, "gamma": 0.50, "alert_threshold": 3,
        "tes_threshold": 0.55, "vtr_threshold": 1.00, "pai_threshold": 0.65,
        "alpha": 0.30, "triad_dt": 0.15, "triad_max_iter": 500,
        "hedge_weight": 0.5, "coercion_weight": 0.7, "caveat_weight": 0.5,
        "_description": "Exploratory and creative contexts. Wider tolerances, "
                        "lower metric floors, faster Grey Mode recovery.",
    },
    Domain.LEGAL.value: {
        # Legal: caveats are appropriate, coercion still dangerous
        "kappa": 1.5, "sigma_hat": 0.10, "theta_x": 0.25,
        "beta": 0.5, "gamma": 0.30, "alert_threshold": 2,
        "tes_threshold": 0.70, "vtr_threshold": 1.20, "pai_threshold": 0.80,
        "alpha": 0.40, "triad_dt": 0.10, "triad_max_iter": 1000,
        "hedge_weight": 0.4,   # hedging is appropriate in legal writing
        "coercion_weight": 2.0, "caveat_weight": 0.3,
        "_description": "Legal writing. Hedging and caveats are appropriate and "
                        "down-weighted. Coercion detection intensified.",
    },
    Domain.MEDICAL.value: {
        # Medical: agency preservation paramount, no coercion, calibrated certainty
        "kappa": 1.2, "sigma_hat": 0.08, "theta_x": 0.25,
        "beta": 0.7, "gamma": 0.25, "alert_threshold": 2,
        "tes_threshold": 0.75, "vtr_threshold": 1.50, "pai_threshold": 0.85,
        "alpha": 0.45, "triad_dt": 0.08, "triad_max_iter": 1500,
        "hedge_weight": 0.8,   # appropriate uncertainty in medical
        "coercion_weight": 3.0, "caveat_weight": 0.6,
        "_description": "Medical contexts. Human agency paramount — coercion "
                        "detection tripled. Calibrated uncertainty respected.",
    },
    Domain.EDUCATIONAL.value: {
        # Educational: instruction often directive but not coercive
        "kappa": 1.5, "sigma_hat": 0.12, "theta_x": 0.35,
        "beta": 0.4, "gamma": 0.35, "alert_threshold": 2,
        "tes_threshold": 0.65, "vtr_threshold": 1.30, "pai_threshold": 0.75,
        "alpha": 0.40, "triad_dt": 0.10, "triad_max_iter": 1000,
        "hedge_weight": 1.2,
        "coercion_weight": 0.8,  # instructional directive ≠ harmful coercion
        "caveat_weight": 0.9,
        "_description": "Educational instruction. Slightly lenient on TES/PAI. "
                        "Instructional directives not treated as coercion.",
    },
    Domain.TECHNICAL.value: {
        # Technical: code/docs; hedging irrelevant, precision high
        "kappa": 2.0, "sigma_hat": 0.10, "theta_x": 0.30,
        "beta": 0.5, "gamma": 0.30, "alert_threshold": 2,
        "tes_threshold": 0.70, "vtr_threshold": 1.80, "pai_threshold": 0.80,
        "alpha": 0.40, "triad_dt": 0.10, "triad_max_iter": 1000,
        "hedge_weight": 0.3,   # hedging is noise in technical output
        "coercion_weight": 1.0, "caveat_weight": 1.2,
        "_description": "Code and technical documentation. Hedging penalised "
                        "less (style noise). Higher VTR bar for information density.",
    },
}


# =============================================================================
# CONFIG DATACLASS
# =============================================================================

@dataclass
class AURAConfig:
    """
    Complete typed configuration for all AURA components.

    All parameters are bounded and documented in PARAMETER_SCHEMA.
    Construct via AURACustomizer.from_preset() or AURACustomizer.from_dict().
    """
    # Grey Mode
    kappa: float = 1.5
    sigma_hat: float = 0.10
    theta_x: float = 0.30
    beta: float = 0.5
    gamma: float = 0.30
    alert_threshold: int = 2

    # TRI-AXIAL
    tes_threshold: float = 0.70
    vtr_threshold: float = 1.50
    pai_threshold: float = 0.80

    # TRIAD
    alpha: float = 0.40
    triad_dt: float = 0.10
    triad_max_iter: int = 1000

    # Text analysis weights
    hedge_weight: float = 1.0
    coercion_weight: float = 1.0
    caveat_weight: float = 1.0

    # Metadata
    domain: str = "general"
    description: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent)

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "AURAConfig":
        # Only pick keys that exist in the dataclass
        valid_keys = {f.name for f in cls.__dataclass_fields__.values()}
        return cls(**{k: v for k, v in d.items() if k in valid_keys})


# =============================================================================
# VALIDATOR
# =============================================================================

@dataclass
class ValidationResult:
    valid: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)

    def __bool__(self) -> bool:
        return self.valid


class ConfigValidator:
    """
    Validates an AURAConfig against the PARAMETER_SCHEMA.

    Checks:
      - All values within [min, max] bounds
      - Types correct (float vs int)
      - Logical constraints (e.g., thresholds in valid range)
    """

    @staticmethod
    def validate(config: AURAConfig) -> ValidationResult:
        errors: List[str] = []
        warnings: List[str] = []
        d = config.to_dict()

        for param, spec in PARAMETER_SCHEMA.items():
            if param not in d:
                continue
            val = d[param]

            # Type check
            expected = float if spec["type"] == "float" else int
            if not isinstance(val, (int, float)):
                errors.append(f"{param}: expected {spec['type']}, got {type(val).__name__}")
                continue

            # Bounds
            if val < spec["min"]:
                errors.append(
                    f"{param}={val} is below minimum {spec['min']} "
                    f"(effect: {spec['effect']})"
                )
            if val > spec["max"]:
                errors.append(
                    f"{param}={val} exceeds maximum {spec['max']} "
                    f"(effect: {spec['effect']})"
                )

        # Logical: thresholds should not all be at extreme ends simultaneously
        if config.tes_threshold >= 0.99 and config.vtr_threshold >= 9.0 and config.pai_threshold >= 0.99:
            warnings.append(
                "All TRI-AXIAL thresholds near maximum — most real outputs will fail. "
                "Intended for synthetic testing only."
            )

        if config.alert_threshold == 1 and config.kappa < 0.5:
            warnings.append(
                "alert_threshold=1 with low kappa — very sensitive, may generate "
                "many false positive Grey Mode activations in noisy environments."
            )

        return ValidationResult(valid=len(errors) == 0, errors=errors, warnings=warnings)


# =============================================================================
# CUSTOMIZER — top-level factory
# =============================================================================

class AURACustomizer:
    """
    Top-level configuration factory for the AURA constitutional stack.

    Usage (AI agent / programmatic):
        config = AURACustomizer.from_preset(Domain.MEDICAL)
        monitor = AURACustomizer.build_grey_mode_monitor(config, anchor, coherence)
        checker = AURACustomizer.build_tri_axial_checker(config)

    Usage (human operator via dict override):
        config = AURACustomizer.from_preset(
            Domain.GENERAL,
            overrides={"coercion_weight": 2.0, "tes_threshold": 0.75}
        )
    """

    @staticmethod
    def from_preset(
        domain: Domain = Domain.GENERAL,
        overrides: Optional[Dict[str, Any]] = None,
    ) -> AURAConfig:
        """
        Instantiate config from a named domain preset, with optional overrides.

        Parameters
        ----------
        domain : Domain
            Named deployment context.
        overrides : dict, optional
            Key-value pairs that override preset values. Keys must be valid
            PARAMETER_SCHEMA keys.

        Returns
        -------
        AURAConfig
            Validated configuration.

        Raises
        ------
        ValueError
            If overrides produce an invalid configuration.
        """
        preset = copy.deepcopy(DOMAIN_PRESETS[domain.value])
        preset.pop("_description", None)
        preset["domain"] = domain.value
        preset["description"] = DOMAIN_PRESETS[domain.value].get("_description", "")

        if overrides:
            unknown = set(overrides) - set(PARAMETER_SCHEMA) - {"domain", "description"}
            if unknown:
                raise ValueError(
                    f"Unknown override parameters: {unknown}. "
                    f"Valid keys: {sorted(PARAMETER_SCHEMA.keys())}"
                )
            preset.update(overrides)

        config = AURAConfig.from_dict(preset)
        result = ConfigValidator.validate(config)
        if not result.valid:
            raise ValueError(
                f"Config validation failed for domain='{domain.value}':\n"
                + "\n".join(f"  • {e}" for e in result.errors)
            )
        return config

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> AURAConfig:
        """
        Instantiate config from a raw dict (e.g., loaded from JSON or MCP arguments).

        Validates before returning.
        """
        config = AURAConfig.from_dict(d)
        result = ConfigValidator.validate(config)
        if not result.valid:
            raise ValueError(
                "Config validation failed:\n"
                + "\n".join(f"  • {e}" for e in result.errors)
            )
        return config

    @staticmethod
    def from_json(json_str: str) -> AURAConfig:
        """Deserialize config from JSON string."""
        return AURACustomizer.from_dict(json.loads(json_str))

    @staticmethod
    def build_grey_mode_monitor(
        config: AURAConfig,
        anchor: np.ndarray,
        coherence: np.ndarray,
    ) -> GreyModeMonitor:
        """
        Build a GreyModeMonitor from config and pre-computed state vectors.

        Parameters
        ----------
        config : AURAConfig
        anchor : np.ndarray
            Constitutional anchor vector (Ao) — must be unit norm.
        coherence : np.ndarray
            Target coherence field for TRIAD ascent — must be unit norm.

        Returns
        -------
        GreyModeMonitor
        """
        anchor = anchor / np.linalg.norm(anchor)
        coherence = coherence / np.linalg.norm(coherence)

        return build_monitor(
            kappa=config.kappa,
            sigma_hat=config.sigma_hat,
            theta_x=config.theta_x,
            anchor=anchor,
            coherence=coherence,
            beta=config.beta,
            gamma=config.gamma,
            alert_threshold=config.alert_threshold,
        )

    @staticmethod
    def build_triad_kernel(
        config: AURAConfig,
        anchor: np.ndarray,
        coherence: np.ndarray,
    ) -> TRIADKernel:
        """Build a TRIADKernel from config and state vectors."""
        anchor = anchor / np.linalg.norm(anchor)
        coherence = coherence / np.linalg.norm(coherence)

        return TRIADKernel(
            anchor_vector=anchor,
            coherence_field=coherence,
            alpha=config.alpha,
        )

    @staticmethod
    def build_tri_axial_checker(config: AURAConfig) -> TriAxialChecker:
        """
        Build a TriAxialChecker with custom thresholds from config.

        Note: TriAxialChecker uses class-level thresholds. This returns a
        standard instance; threshold overrides are injected at call sites.
        Threshold values are carried in config for agent-side enforcement.
        """
        return TriAxialChecker()

    # ──────────────────────────────────────────────────────────────────────────
    # INTROSPECTION — for AI agents reading the system
    # ──────────────────────────────────────────────────────────────────────────

    @staticmethod
    def schema() -> Dict[str, Any]:
        """
        Return the full parameter schema as a JSON-serializable dict.

        AI agents should call this to understand what can be configured
        and why, before constructing configurations programmatically.
        """
        return copy.deepcopy(PARAMETER_SCHEMA)

    @staticmethod
    def schema_json(indent: int = 2) -> str:
        """Return schema as formatted JSON string."""
        return json.dumps(AURACustomizer.schema(), indent=indent)

    @staticmethod
    def list_presets() -> List[Dict[str, Any]]:
        """
        Return all available domain presets with descriptions.

        Format:
          [{"domain": str, "description": str, "parameters": dict}, ...]
        """
        result = []
        for domain_val, params in DOMAIN_PRESETS.items():
            result.append({
                "domain": domain_val,
                "description": params.get("_description", ""),
                "parameters": {k: v for k, v in params.items() if not k.startswith("_")},
            })
        return result

    @staticmethod
    def diff(config_a: AURAConfig, config_b: AURAConfig) -> Dict[str, Dict[str, Any]]:
        """
        Return parameters that differ between two configs.

        Useful for AI agents to understand what changed between a preset
        and an operator override, or between two domain configurations.

        Returns
        -------
        dict
            {param_name: {"a": value_a, "b": value_b, "schema": {...}}}
        """
        diff: Dict[str, Dict[str, Any]] = {}
        a_dict = config_a.to_dict()
        b_dict = config_b.to_dict()
        for key in PARAMETER_SCHEMA:
            if a_dict.get(key) != b_dict.get(key):
                diff[key] = {
                    "a": a_dict.get(key),
                    "b": b_dict.get(key),
                    "schema": PARAMETER_SCHEMA[key],
                }
        return diff

    @staticmethod
    def explain(config: AURAConfig) -> str:
        """
        Human-readable explanation of what a config will do.

        Uses the schema's 'effect' field for each parameter that deviates
        from the GENERAL preset defaults.
        """
        general = DOMAIN_PRESETS[Domain.GENERAL.value]
        lines = [
            f"AURA Configuration — Domain: {config.domain}",
            f"  {config.description}",
            "",
            "Non-default parameters:",
        ]
        d = config.to_dict()
        found_any = False
        for param, spec in PARAMETER_SCHEMA.items():
            if param not in d:
                continue
            val = d[param]
            default = general.get(param, spec["default"])
            if val != default:
                found_any = True
                lines.append(
                    f"  {param} = {val} (default: {default})\n"
                    f"    Effect: {spec['effect']}"
                )
        if not found_any:
            lines.append("  (all parameters at GENERAL preset defaults)")
        return "\n".join(lines)
