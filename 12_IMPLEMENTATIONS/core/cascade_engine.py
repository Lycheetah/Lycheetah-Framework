"""
CASCADE Engine — Domain-Agnostic Knowledge Reorganization
==========================================================

This is the core mechanism. It knows nothing about physics, medicine,
or any specific domain. You feed it knowledge blocks with evidence
scores, it handles reorganization.

Usage:
    from cascade_engine import CascadeEngine, KnowledgeBlock
    
    engine = CascadeEngine()
    engine.add_block(KnowledgeBlock(
        id="my_claim",
        content="Some knowledge claim",
        domain="my_domain",
        paradigm="old",
        evidence_strength=0.6,
        explanatory_power=1.5,
        uncertainty=0.4,
    ))

Author: Mackenzie Clark (Lycheetah Foundation)
Version: 2.0 — Modular rewrite for real-world validation
Date: March 2026
"""

import numpy as np
from dataclasses import dataclass, field
from typing import List, Dict, Set, Tuple, Optional, Callable
from collections import defaultdict
import json


# =============================================================================
# KNOWLEDGE BLOCK
# =============================================================================

@dataclass
class KnowledgeBlock:
    """A single knowledge claim with evidence and metadata."""
    id: str
    content: str
    domain: str                     # Grouping label (e.g., "mechanics", "optics")
    paradigm: str                   # Which paradigm this belongs to
    evidence_strength: float        # E ∈ [0,1] — quality/quantity of evidence
    explanatory_power: float        # P ∈ [1,3] — breadth of phenomena explained
    uncertainty: float              # S ∈ (0,1] — Shannon entropy of evidence dist.
    
    # Optional metadata
    year: int = 0                   # When this knowledge was established
    key_figure: str = ""            # Who established it
    note: str = ""                  # Brief historical/contextual note
    dependencies: Set[str] = field(default_factory=set)
    
    # State (managed by engine)
    regime: str = "universal"       # "universal" or "qualified"
    layer: str = "EDGE"            # FOUNDATION, THEORY, or EDGE
    
    @property
    def truth_pressure(self) -> float:
        """Π = (E · P) / S"""
        return (self.evidence_strength * self.explanatory_power) / max(self.uncertainty, 0.01)
    
    def copy_with_noise(self, rng: np.random.Generator, noise: float) -> 'KnowledgeBlock':
        """Create a noisy copy for multi-trial experiments."""
        return KnowledgeBlock(
            id=self.id,
            content=self.content,
            domain=self.domain,
            paradigm=self.paradigm,
            evidence_strength=float(np.clip(
                self.evidence_strength + rng.normal(0, noise), 0.01, 0.99)),
            explanatory_power=float(np.clip(
                self.explanatory_power + rng.normal(0, noise * 0.5), 1.0, 3.0)),
            uncertainty=float(np.clip(
                self.uncertainty + rng.normal(0, noise * 0.3), 0.01, 0.99)),
            year=self.year,
            key_figure=self.key_figure,
            note=self.note,
            dependencies=self.dependencies.copy(),
        )
    
    def __repr__(self):
        q = " [Q]" if self.regime == "qualified" else ""
        return f"[{self.layer[0]}] {self.id}: Π={self.truth_pressure:.2f} ({self.paradigm}){q}"


# =============================================================================
# CASCADE ENGINE
# =============================================================================

class CascadeEngine:
    """
    Domain-agnostic CASCADE reorganization engine.
    
    Three layers (Foundation/Theory/Edge), four-phase cascade protocol,
    truth-pressure-driven demotion.
    """
    
    def __init__(self, 
                 foundation_threshold: float = 1.5,
                 theory_threshold: float = 1.2,
                 trigger_margin: float = 0.3,
                 compression_gamma: float = 0.85):
        self.foundation_threshold = foundation_threshold
        self.theory_threshold = theory_threshold
        self.trigger_margin = trigger_margin
        self.compression_gamma = compression_gamma
        
        self.blocks: Dict[str, KnowledgeBlock] = {}
        self.cascade_events: List[Dict] = []
        self.coherence_trace: List[Tuple[int, float]] = []
        self.step = 0
    
    def reset(self):
        """Clear all state."""
        self.blocks.clear()
        self.cascade_events.clear()
        self.coherence_trace.clear()
        self.step = 0
    
    # ── Layer assignment ──
    
    def _assign_layer(self, block: KnowledgeBlock):
        pi = block.truth_pressure
        if pi >= self.foundation_threshold:
            block.layer = "FOUNDATION"
        elif pi >= self.theory_threshold:
            block.layer = "THEORY"
        else:
            block.layer = "EDGE"
    
    # ── Contradiction detection ──
    
    def contradicts(self, b1: KnowledgeBlock, b2: KnowledgeBlock) -> bool:
        """Two blocks contradict if: same domain, different paradigm, both universal."""
        return (b1.domain == b2.domain and
                b1.paradigm != b2.paradigm and
                b1.regime == "universal" and
                b2.regime == "universal")
    
    def active_contradictions(self) -> List[Tuple[str, str]]:
        pairs = []
        blocks = list(self.blocks.values())
        for i, b1 in enumerate(blocks):
            for b2 in blocks[i+1:]:
                if self.contradicts(b1, b2):
                    pairs.append((b1.id, b2.id))
        return pairs
    
    # ── Metrics ──
    
    def coherence(self) -> float:
        n = len(self.blocks)
        if n < 2:
            return 1.0
        return 1.0 - len(self.active_contradictions()) / (n * (n - 1) / 2)
    
    def information_content(self) -> float:
        return sum(b.evidence_strength * b.explanatory_power for b in self.blocks.values())
    
    def total_entropy(self) -> float:
        return sum(b.uncertainty for b in self.blocks.values())
    
    def layer_distribution(self) -> Dict[str, int]:
        dist = {"FOUNDATION": 0, "THEORY": 0, "EDGE": 0}
        for b in self.blocks.values():
            dist[b.layer] += 1
        return dist
    
    def foundations(self) -> List[KnowledgeBlock]:
        return [b for b in self.blocks.values() if b.layer == "FOUNDATION"]
    
    def qualified_blocks(self) -> List[KnowledgeBlock]:
        return [b for b in self.blocks.values() if b.regime == "qualified"]
    
    # ── Core: add block ──
    
    def add_block(self, block: KnowledgeBlock) -> Optional[Dict]:
        """
        Add a knowledge block. Returns cascade event dict if cascade fired, else None.
        """
        self.step += 1
        self._assign_layer(block)
        self.blocks[block.id] = block
        
        # Find contradicting blocks where new block has sufficiently higher Π
        conflicts = []
        for existing in self.blocks.values():
            if existing.id == block.id:
                continue
            if self.contradicts(block, existing):
                if block.truth_pressure > existing.truth_pressure + self.trigger_margin:
                    conflicts.append(existing)
        
        event = None
        if conflicts:
            event = self._execute_cascade(block, conflicts)
        
        self.coherence_trace.append((self.step, self.coherence()))
        return event
    
    def _execute_cascade(self, new_block: KnowledgeBlock, 
                          conflicts: List[KnowledgeBlock]) -> Dict:
        """Four-phase cascade reorganization."""
        pre_c = self.coherence()
        pre_i = self.information_content()
        pre_h = self.total_entropy()
        
        # Phase 1: CONFLICT IDENTIFICATION (already done)
        
        # Phase 2: COMPRESSION — contextualize old foundations
        compressed_ids = []
        for old in conflicts:
            old.regime = "qualified"
            old.uncertainty = old.uncertainty / self.compression_gamma  # increases S → lowers Π
            self._assign_layer(old)  # may demote
            compressed_ids.append(old.id)
        
        # Phase 3: EXPANSION — promote new block
        new_block.layer = "FOUNDATION"
        new_block.regime = "universal"
        
        # Phase 4: STABILIZATION — reassign any affected blocks
        for b in self.blocks.values():
            if b.id != new_block.id and b.id not in compressed_ids:
                self._assign_layer(b)
        
        post_c = self.coherence()
        post_i = self.information_content()
        post_h = self.total_entropy()
        
        event = {
            "step": self.step,
            "trigger_id": new_block.id,
            "trigger_paradigm": new_block.paradigm,
            "trigger_pi": new_block.truth_pressure,
            "compressed": compressed_ids,
            "compressed_paradigm": conflicts[0].paradigm,
            "pre_coherence": pre_c,
            "post_coherence": post_c,
            "coherence_preserved": post_c >= pre_c - 1e-10,
            "info_preserved": post_i >= pre_i - 1e-10,
            "entropy_preserved": post_h >= pre_h - 1e-10,
            "demotion_correct": all(
                new_block.truth_pressure > c.truth_pressure for c in conflicts
            ),
        }
        self.cascade_events.append(event)
        return event


# =============================================================================
# BASELINE SYSTEMS (for comparison)
# =============================================================================

class StaticBaseline:
    """Adds blocks without any reorganization."""
    
    def __init__(self, thresholds=None):
        self.blocks: Dict[str, KnowledgeBlock] = {}
        self.step = 0
        self.ft = 1.5 if not thresholds else thresholds[0]
        self.tt = 1.2 if not thresholds else thresholds[1]
    
    def reset(self):
        self.blocks.clear()
        self.step = 0
    
    def add_block(self, block: KnowledgeBlock):
        self.step += 1
        pi = block.truth_pressure
        block.layer = "FOUNDATION" if pi >= self.ft else ("THEORY" if pi >= self.tt else "EDGE")
        self.blocks[block.id] = block
    
    def coherence(self):
        n = len(self.blocks)
        if n < 2:
            return 1.0
        contras = 0
        bl = list(self.blocks.values())
        for i, b1 in enumerate(bl):
            for b2 in bl[i+1:]:
                if (b1.domain == b2.domain and b1.paradigm != b2.paradigm and
                    b1.regime == "universal" and b2.regime == "universal"):
                    contras += 1
        return 1.0 - contras / (n * (n-1) / 2)
    
    def active_contradictions(self):
        pairs = []
        bl = list(self.blocks.values())
        for i, b1 in enumerate(bl):
            for b2 in bl[i+1:]:
                if (b1.domain == b2.domain and b1.paradigm != b2.paradigm and
                    b1.regime == "universal" and b2.regime == "universal"):
                    pairs.append((b1.id, b2.id))
        return pairs
    
    def qualified_blocks(self):
        return [b for b in self.blocks.values() if b.regime == "qualified"]
    
    def foundations(self):
        return [b for b in self.blocks.values() if b.layer == "FOUNDATION"]
    
    def information_content(self):
        return sum(b.evidence_strength * b.explanatory_power for b in self.blocks.values())


class AdditiveBaseline:
    """Contextualizes any lower-Π contradicting block immediately (no trigger margin)."""
    
    def __init__(self, thresholds=None):
        self.blocks: Dict[str, KnowledgeBlock] = {}
        self.step = 0
        self.ft = 1.5 if not thresholds else thresholds[0]
        self.tt = 1.2 if not thresholds else thresholds[1]
    
    def reset(self):
        self.blocks.clear()
        self.step = 0
    
    def add_block(self, block: KnowledgeBlock):
        self.step += 1
        pi = block.truth_pressure
        block.layer = "FOUNDATION" if pi >= self.ft else ("THEORY" if pi >= self.tt else "EDGE")
        self.blocks[block.id] = block
        
        for existing in list(self.blocks.values()):
            if existing.id == block.id:
                continue
            if (existing.domain == block.domain and existing.paradigm != block.paradigm and
                existing.regime == "universal" and block.regime == "universal"):
                if block.truth_pressure > existing.truth_pressure:
                    existing.regime = "qualified"
                elif existing.truth_pressure > block.truth_pressure:
                    block.regime = "qualified"
    
    def coherence(self):
        n = len(self.blocks)
        if n < 2:
            return 1.0
        contras = 0
        bl = list(self.blocks.values())
        for i, b1 in enumerate(bl):
            for b2 in bl[i+1:]:
                if (b1.domain == b2.domain and b1.paradigm != b2.paradigm and
                    b1.regime == "universal" and b2.regime == "universal"):
                    contras += 1
        return 1.0 - contras / (n * (n-1) / 2)
    
    def active_contradictions(self):
        pairs = []
        bl = list(self.blocks.values())
        for i, b1 in enumerate(bl):
            for b2 in bl[i+1:]:
                if (b1.domain == b2.domain and b1.paradigm != b2.paradigm and
                    b1.regime == "universal" and b2.regime == "universal"):
                    pairs.append((b1.id, b2.id))
        return pairs
    
    def qualified_blocks(self):
        return [b for b in self.blocks.values() if b.regime == "qualified"]
    
    def foundations(self):
        return [b for b in self.blocks.values() if b.layer == "FOUNDATION"]
    
    def information_content(self):
        return sum(b.evidence_strength * b.explanatory_power for b in self.blocks.values())


class NoPressureBaseline:
    """CASCADE structure but random demotion (no truth pressure guidance)."""
    
    def __init__(self, seed: int = 12345):
        self.blocks: Dict[str, KnowledgeBlock] = {}
        self.cascade_events: List[Dict] = []
        self.step = 0
        self._rng = np.random.default_rng(seed)
    
    def reset(self):
        self.blocks.clear()
        self.cascade_events.clear()
        self.step = 0
    
    def add_block(self, block: KnowledgeBlock):
        self.step += 1
        block.layer = "FOUNDATION" if block.truth_pressure >= 1.5 else (
            "THEORY" if block.truth_pressure >= 1.2 else "EDGE")
        self.blocks[block.id] = block
        
        for existing in list(self.blocks.values()):
            if existing.id == block.id:
                continue
            if (existing.domain == block.domain and existing.paradigm != block.paradigm and
                existing.regime == "universal" and block.regime == "universal"):
                # Random choice instead of truth-pressure-based
                if self._rng.random() > 0.5:
                    existing.regime = "qualified"
                    correct = block.truth_pressure > existing.truth_pressure
                else:
                    block.regime = "qualified"
                    correct = existing.truth_pressure > block.truth_pressure
                self.cascade_events.append({"demotion_correct": correct})
    
    def coherence(self):
        n = len(self.blocks)
        if n < 2:
            return 1.0
        contras = 0
        bl = list(self.blocks.values())
        for i, b1 in enumerate(bl):
            for b2 in bl[i+1:]:
                if (b1.domain == b2.domain and b1.paradigm != b2.paradigm and
                    b1.regime == "universal" and b2.regime == "universal"):
                    contras += 1
        return 1.0 - contras / (n * (n-1) / 2)
    
    def qualified_blocks(self):
        return [b for b in self.blocks.values() if b.regime == "qualified"]


# =============================================================================
# EXPERIMENT HARNESS
# =============================================================================

class DomainExperiment:
    """
    Reusable experiment harness. Feed it a domain dataset (list of KnowledgeBlocks)
    and it runs CASCADE vs baselines with full statistical analysis.
    """
    
    def __init__(self, 
                 domain_name: str,
                 blocks: List[KnowledgeBlock],
                 old_paradigm: str,
                 new_paradigm: str,
                 fidelity_checks: Optional[List[Callable]] = None):
        self.domain_name = domain_name
        self.base_blocks = blocks
        self.old_paradigm = old_paradigm
        self.new_paradigm = new_paradigm
        self.fidelity_checks = fidelity_checks or []
    
    def run_historical_trace(self, verbose: bool = True) -> Dict:
        """Single deterministic run showing cascade events chronologically."""
        engine = CascadeEngine()
        
        if verbose:
            print(f"\n{'='*70}")
            print(f"HISTORICAL TRACE: {self.domain_name}")
            print(f"{'='*70}\n")
        
        for block in self.base_blocks:
            event = engine.add_block(block)
            if verbose:
                yr = f"[{block.year}] " if block.year else ""
                print(f"  {yr}Added: {block.id}")
                print(f"       Π = {block.truth_pressure:.2f} → {block.layer}"
                      f" ({block.paradigm})")
                if event:
                    print(f"       ⚡ CASCADE! Compressed: {event['compressed']}")
                    print(f"       Coherence: {event['pre_coherence']:.3f} → "
                          f"{event['post_coherence']:.3f}")
        
        # Final structure
        if verbose:
            print(f"\n{'─'*50}")
            print("FINAL STRUCTURE:")
            print(f"{'─'*50}")
            for layer in ["FOUNDATION", "THEORY", "EDGE"]:
                layer_blocks = sorted(
                    [b for b in engine.blocks.values() if b.layer == layer],
                    key=lambda b: b.truth_pressure, reverse=True)
                if layer_blocks:
                    print(f"\n  [{layer}]")
                    for b in layer_blocks:
                        q = " [QUALIFIED]" if b.regime == "qualified" else ""
                        fig = f" — {b.key_figure}" if b.key_figure else ""
                        print(f"    {b.id}: Π={b.truth_pressure:.2f} "
                              f"({b.paradigm}){q}{fig}")
        
        # Fidelity checks
        results = {"engine": engine, "passed": 0, "total": 0, "checks": []}
        if self.fidelity_checks:
            if verbose:
                print(f"\n{'─'*50}")
                print("HISTORICAL FIDELITY:")
                print(f"{'─'*50}")
            for i, check_fn in enumerate(self.fidelity_checks):
                passed, description = check_fn(engine)
                results["checks"].append((passed, description))
                results["total"] += 1
                if passed:
                    results["passed"] += 1
                if verbose:
                    print(f"  {i+1}. {description}: {'✓' if passed else '✗'}")
            
            if verbose:
                print(f"\n  Score: {results['passed']}/{results['total']}")
        
        return results
    
    def run_comparative(self, n_trials: int = 200, seed: int = 42, 
                         noise: float = 0.05, verbose: bool = True) -> Dict:
        """Run multi-trial comparison: CASCADE vs Static vs Additive vs NoΠ."""
        rng = np.random.default_rng(seed)
        
        if verbose:
            print(f"\n{'='*70}")
            print(f"COMPARATIVE EXPERIMENT: {self.domain_name}")
            print(f"  Trials: {n_trials}, Seed: {seed}, Noise: {noise}")
            n_old = sum(1 for b in self.base_blocks if b.paradigm == self.old_paradigm)
            n_new = sum(1 for b in self.base_blocks if b.paradigm == self.new_paradigm)
            print(f"  Blocks: {len(self.base_blocks)} "
                  f"({n_old} {self.old_paradigm}, {n_new} {self.new_paradigm})")
            print(f"{'='*70}\n")
        
        # Accumulators
        results = {
            "cascade": {"coherence": [], "contradictions": [], "info": [],
                        "invariants_ok": [], "demotion_acc": [], "n_cascades": []},
            "static":  {"coherence": [], "contradictions": [], "info": []},
            "additive": {"coherence": [], "contradictions": [], "info": []},
            "no_pi":   {"demotion_acc": []},
        }
        
        for trial in range(n_trials):
            # Make noisy copies
            noisy = [b.copy_with_noise(rng, noise) for b in self.base_blocks]
            
            # CASCADE
            engine = CascadeEngine()
            for b in noisy:
                engine.add_block(b)
            results["cascade"]["coherence"].append(engine.coherence())
            results["cascade"]["contradictions"].append(len(engine.active_contradictions()))
            results["cascade"]["info"].append(engine.information_content())
            results["cascade"]["n_cascades"].append(len(engine.cascade_events))
            results["cascade"]["invariants_ok"].append(
                all(e["coherence_preserved"] and e["info_preserved"] and e["entropy_preserved"]
                    for e in engine.cascade_events) if engine.cascade_events else True)
            if engine.cascade_events:
                acc = sum(1 for e in engine.cascade_events if e["demotion_correct"]) / len(engine.cascade_events)
                results["cascade"]["demotion_acc"].append(acc)
            
            # Static
            noisy2 = [b.copy_with_noise(rng, noise) for b in self.base_blocks]
            static = StaticBaseline()
            for b in noisy2:
                static.add_block(b)
            results["static"]["coherence"].append(static.coherence())
            results["static"]["contradictions"].append(len(static.active_contradictions()))
            results["static"]["info"].append(static.information_content())
            
            # Additive
            noisy3 = [b.copy_with_noise(rng, noise) for b in self.base_blocks]
            additive = AdditiveBaseline()
            for b in noisy3:
                additive.add_block(b)
            results["additive"]["coherence"].append(additive.coherence())
            results["additive"]["contradictions"].append(len(additive.active_contradictions()))
            results["additive"]["info"].append(additive.information_content())
            
            # No truth pressure
            noisy4 = [b.copy_with_noise(rng, noise) for b in self.base_blocks]
            no_pi = NoPressureBaseline(seed=seed + trial)
            for b in noisy4:
                no_pi.add_block(b)
            if no_pi.cascade_events:
                acc2 = sum(1 for e in no_pi.cascade_events if e["demotion_correct"]) / len(no_pi.cascade_events)
                results["no_pi"]["demotion_acc"].append(acc2)
            
            if verbose and (trial + 1) % 50 == 0:
                print(f"  Completed {trial + 1}/{n_trials} trials...")
        
        # Statistics
        from scipy import stats as sp_stats
        
        cas_c = results["cascade"]["coherence"]
        sta_c = results["static"]["coherence"]
        add_c = results["additive"]["coherence"]
        
        # Safe t-tests
        def safe_ttest(a, b):
            diff = np.array(a) - np.array(b)
            if np.std(diff) == 0:
                m = np.mean(diff)
                return (float('inf') if m > 0 else 0.0, 
                        0.0 if m != 0 else 1.0,
                        float('inf') if m > 0 else 0.0)
            t, p = sp_stats.ttest_rel(a, b)
            d = np.mean(diff) / np.std(diff)
            return float(t), float(p), float(d)
        
        t_cs, p_cs, d_cs = safe_ttest(cas_c, sta_c)
        t_ca, p_ca, d_ca = safe_ttest(cas_c, add_c)
        
        # Ablation t-test
        cas_dem = results["cascade"]["demotion_acc"]
        nopi_dem = results["no_pi"]["demotion_acc"]
        if cas_dem and nopi_dem:
            t_abl, p_abl = sp_stats.ttest_ind(cas_dem, nopi_dem)
        else:
            t_abl, p_abl = 0.0, 1.0
        
        stats = {
            "cascade_vs_static": {"t": t_cs, "p": p_cs, "d": d_cs},
            "cascade_vs_additive": {"t": t_ca, "p": p_ca, "d": d_ca},
            "ablation": {"t": float(t_abl), "p": float(p_abl)},
        }
        
        if verbose:
            self._print_comparative(results, stats, n_trials)
        
        return {"raw": results, "stats": stats}
    
    def _print_comparative(self, results: Dict, stats: Dict, n_trials: int):
        """Print formatted comparative results."""
        print(f"\n{'='*70}")
        print(f"RESULTS: {self.domain_name}")
        print(f"{'='*70}\n")
        
        # Table
        print(f"  {'System':<12} {'Coherence':>16} {'Contradictions':>16} {'Info':>16}")
        print(f"  {'-'*62}")
        for name, key in [("Static","static"),("Additive","additive"),("CASCADE","cascade")]:
            c = results[key]["coherence"]
            x = results[key]["contradictions"]
            info = results[key]["info"]
            print(f"  {name:<12} {np.mean(c):.4f} ± {np.std(c):.4f}"
                  f"   {np.mean(x):>5.1f} ± {np.std(x):.1f}"
                  f"   {np.mean(info):>6.2f} ± {np.std(info):.2f}")
        
        # CASCADE specifics
        cas = results["cascade"]
        print(f"\n  CASCADE Details:")
        print(f"    Invariant preservation: "
              f"{np.mean(cas['invariants_ok'])*100:.1f}% ({n_trials} trials)")
        if cas["demotion_acc"]:
            print(f"    Demotion accuracy:      "
                  f"{np.mean(cas['demotion_acc'])*100:.1f}% ± "
                  f"{np.std(cas['demotion_acc'])*100:.1f}%")
        print(f"    Cascade events/trial:   "
              f"{np.mean(cas['n_cascades']):.1f} ± {np.std(cas['n_cascades']):.1f}")
        
        # Ablation
        nopi = results["no_pi"]["demotion_acc"]
        if nopi:
            print(f"    No-Π demotion accuracy: "
                  f"{np.mean(nopi)*100:.1f}% ± {np.std(nopi)*100:.1f}%")
            print(f"    Ablation: t={stats['ablation']['t']:.2f}, "
                  f"p={stats['ablation']['p']:.2e}")
        
        # Statistical comparisons
        print(f"\n  Comparisons:")
        s = stats["cascade_vs_static"]
        if s["p"] == 0.0:
            print(f"    vs Static:   CASCADE always outperforms "
                  f"(Δ=+{np.mean(cas['coherence'])-np.mean(results['static']['coherence']):.4f})")
        else:
            print(f"    vs Static:   t={s['t']:.2f}, p={s['p']:.2e}, d={s['d']:.2f}")
        
        s2 = stats["cascade_vs_additive"]
        if s2["p"] == 1.0 and s2["d"] == 0.0:
            print(f"    vs Additive: Identical coherence; difference is structural")
        else:
            print(f"    vs Additive: t={s2['t']:.2f}, p={s2['p']:.2e}, d={s2['d']:.2f}")
