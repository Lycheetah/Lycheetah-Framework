"""
CASCADE: Experimental Validation Suite
=======================================
Every number in the paper comes from this file.
Run: python cascade_real_experiments.py

Author: Mackenzie Clark, Lycheetah Foundation
"""
import numpy as np
from scipy import stats
from dataclasses import dataclass, field
from typing import List, Dict, Tuple, Optional
import copy, json, time

# ═══════════════════════════════════════════════════
# CORE: Knowledge Block and Truth Pressure
# ═══════════════════════════════════════════════════

@dataclass
class Block:
    name: str
    evidence: float          # E in [0,1]
    power: float             # P > 0 (explanatory scope)  
    entropy: float           # S > 0 (uncertainty)
    domain: str = ""
    regime: str = "universal"  # "universal" or "limited_to_X"
    contradicts: set = field(default_factory=set)
    
    @property
    def pi(self):
        return (self.evidence * self.power) / max(self.entropy, 1e-10)
    
    @property  
    def layer(self):
        p = self.pi
        if p >= 1.5: return 'F'
        if p >= 1.2: return 'T'
        return 'E'
    
    def copy(self):
        b = Block(self.name, self.evidence, self.power, self.entropy,
                  self.domain, self.regime, set(self.contradicts))
        return b


class Pyramid:
    """Knowledge pyramid with coherence, accuracy, and information metrics."""
    
    def __init__(self):
        self.blocks: Dict[str, Block] = {}
    
    def _active_contradictions(self) -> int:
        """
        A contradiction between A and B is ACTIVE if:
        1. A.contradicts contains B (or vice versa)
        2. Both claim universal validity (regime == "universal")
        3. They are in the same domain
        
        A contradiction is RESOLVED if one block has been 
        contextualized (regime != "universal") — i.e., it's been
        demoted to "holds only in regime X".
        """
        active = 0
        names = list(self.blocks.keys())
        for i in range(len(names)):
            for j in range(i+1, len(names)):
                bi = self.blocks[names[i]]
                bj = self.blocks[names[j]]
                if (names[j] in bi.contradicts or names[i] in bj.contradicts):
                    if bi.domain == bj.domain:
                        # Both universal = active contradiction
                        if bi.regime == "universal" and bj.regime == "universal":
                            active += 1
        return active
    
    def coherence(self) -> float:
        n = len(self.blocks)
        if n < 2: return 1.0
        c = self._active_contradictions()
        possible = n * (n - 1) / 2
        return 1.0 - (c / possible)
    
    def total_info(self) -> float:
        """Total information = sum of (evidence * power) for all blocks."""
        return sum(b.evidence * b.power for b in self.blocks.values())
    
    def total_entropy(self) -> float:
        return sum(b.entropy for b in self.blocks.values())
    
    def query(self, domain: str, paradigm: str) -> float:
        """
        Query accuracy: what's the pi of the best universal block
        in this domain that belongs to the given paradigm?
        Returns the pi, or 0 if no matching block.
        """
        best = 0
        for b in self.blocks.values():
            if b.domain == domain and b.regime == "universal":
                if paradigm in b.name:
                    best = max(best, b.pi)
        return best
    
    def layer_counts(self):
        c = {'F': 0, 'T': 0, 'E': 0}
        for b in self.blocks.values():
            c[b.layer] += 1
        return c


# ═══════════════════════════════════════════════════
# THREE KNOWLEDGE MANAGEMENT STRATEGIES
# ═══════════════════════════════════════════════════

def static_add(pyramid: Pyramid, block: Block) -> Pyramid:
    """Static: just insert, no reorganization."""
    pyramid.blocks[block.name] = block.copy()
    return pyramid

def additive_add(pyramid: Pyramid, block: Block) -> Pyramid:
    """Additive: insert + mark lower-pi contradictors as 'limited'."""
    b = block.copy()
    for cname in b.contradicts:
        if cname in pyramid.blocks:
            old = pyramid.blocks[cname]
            if old.pi < b.pi:
                old.regime = f"limited_to_{old.domain}"
    pyramid.blocks[b.name] = b
    return pyramid

def cascade_add(pyramid: Pyramid, block: Block, 
                threshold=0.1, gamma=0.85) -> dict:
    """
    CASCADE: full reorganization protocol.
    Returns event log (empty dict if no cascade triggered).
    """
    b = block.copy()
    new_pi = b.pi
    log = {}
    
    # Find contradicting foundation blocks
    conflicting = []
    for cname in b.contradicts:
        if cname in pyramid.blocks and pyramid.blocks[cname].layer == 'F':
            if pyramid.blocks[cname].regime == "universal":
                conflicting.append(cname)
    
    if conflicting:
        max_conf_pi = max(pyramid.blocks[n].pi for n in conflicting)
        
        if new_pi > max_conf_pi + threshold:
            # ═══ CASCADE EVENT ═══
            coh_before = pyramid.coherence()
            info_before = pyramid.total_info()
            entropy_before = pyramid.total_entropy()
            
            # Phase 1: COMPRESS — demote conflicting foundations
            for cname in conflicting:
                old = pyramid.blocks[cname]
                # Contextualize: no longer universal
                old.regime = f"limited_to_{old.domain}_classical"
                # Increase entropy (lower confidence)
                old.entropy /= gamma
            
            # Phase 2: EXPAND — new block enters as foundation
            b.regime = "universal"
            pyramid.blocks[b.name] = b
            
            coh_after = pyramid.coherence()
            info_after = pyramid.total_info()
            entropy_after = pyramid.total_entropy()
            
            log = {
                'triggered': True,
                'compressed': conflicting,
                'coherence': (coh_before, coh_after),
                'information': (info_before, info_after),
                'entropy': (entropy_before, entropy_after),
            }
            return log
    
    # No cascade — normal insert
    pyramid.blocks[b.name] = b
    return {}


# ═══════════════════════════════════════════════════
# SCENARIO GENERATORS
# ═══════════════════════════════════════════════════

def make_physics_paradigm(rng, n_per_paradigm=8):
    """
    Classical physics (moderate evidence) vs Modern physics (strong evidence).
    Returns: (classical_blocks, modern_blocks, test_queries)
    """
    domains = ['mechanics', 'electromagnetism', 'thermodynamics', 'optics',
               'gravity', 'matter', 'energy', 'spacetime']
    
    classical = []
    for i in range(n_per_paradigm):
        b = Block(
            name=f'classical_{domains[i]}',
            evidence=rng.uniform(0.72, 0.88),
            power=rng.uniform(1.3, 1.8),
            entropy=rng.uniform(0.30, 0.55),
            domain=domains[i],
            regime="universal",
        )
        classical.append(b)
    
    modern = []
    for i in range(n_per_paradigm):
        b = Block(
            name=f'modern_{domains[i]}',
            evidence=rng.uniform(0.90, 0.99),
            power=rng.uniform(1.9, 2.8),
            entropy=rng.uniform(0.08, 0.18),
            domain=domains[i],
            regime="universal",
            contradicts={f'classical_{domains[i]}'},
        )
        # Set reverse contradiction
        classical[i].contradicts.add(f'modern_{domains[i]}')
        modern.append(b)
    
    # Test: modern paradigm is "correct"
    test_queries = [(domains[i], 'modern') for i in range(n_per_paradigm)]
    
    return classical, modern, test_queries


def make_incremental(rng, n_steps=30, n_domains=5):
    """Generate incremental knowledge with occasional contradictions."""
    blocks = []
    names_by_domain = {f'd{i}': [] for i in range(n_domains)}
    
    for step in range(n_steps):
        domain = f'd{step % n_domains}'
        name = f'block_{step}'
        
        contradicts = set()
        existing = names_by_domain[domain]
        if existing and rng.random() < 0.35:
            contradicts.add(rng.choice(existing))
        
        b = Block(
            name=name,
            evidence=rng.uniform(0.4, 1.0),
            power=rng.uniform(0.4, 2.8),
            entropy=rng.uniform(0.08, 0.9),
            domain=domain,
            regime="universal",
            contradicts=contradicts,
        )
        blocks.append(b)
        names_by_domain[domain].append(name)
    
    return blocks


# ═══════════════════════════════════════════════════
# EXPERIMENTS
# ═══════════════════════════════════════════════════

def run_all():
    results = {}
    
    # ─── EXP 1: PARADIGM SHIFT ──────────────────────
    print("=" * 65)
    print("EXPERIMENT 1: Paradigm Shift — CASCADE vs Static vs Additive")
    print("=" * 65)
    
    N = 200
    data = {s: {'coh': [], 'acc': [], 'active_cont': []} 
            for s in ['static', 'additive', 'cascade']}
    cascade_events = []
    
    for trial in range(N):
        rng = np.random.RandomState(trial)
        classical, modern, queries = make_physics_paradigm(rng)
        
        for sys_name, add_fn in [('static', static_add), 
                                  ('additive', additive_add)]:
            pyr = Pyramid()
            for b in classical: add_fn(pyr, b.copy())
            for b in modern: add_fn(pyr, b.copy())
            
            data[sys_name]['coh'].append(pyr.coherence())
            # Accuracy: fraction of queries where modern paradigm has highest pi
            correct = 0
            for domain, paradigm in queries:
                modern_pi = pyr.query(domain, paradigm)
                classical_pi = pyr.query(domain, 'classical')
                if modern_pi > classical_pi:
                    correct += 1
            data[sys_name]['acc'].append(correct / len(queries))
            data[sys_name]['active_cont'].append(pyr._active_contradictions())
        
        # CASCADE
        pyr = Pyramid()
        for b in classical: cascade_add(pyr, b.copy())
        events_this = []
        for b in modern:
            log = cascade_add(pyr, b.copy())
            if log: events_this.append(log)
        
        data['cascade']['coh'].append(pyr.coherence())
        correct = 0
        for domain, paradigm in queries:
            modern_pi = pyr.query(domain, paradigm)
            classical_pi = pyr.query(domain, 'classical')
            if modern_pi > classical_pi:
                correct += 1
        data['cascade']['acc'].append(correct / len(queries))
        data['cascade']['active_cont'].append(pyr._active_contradictions())
        cascade_events.extend(events_this)
    
    exp1 = {}
    print(f"\n  n={N} trials, 8 classical + 8 modern blocks each\n")
    print(f"  {'System':<12} {'Coherence':>16} {'Accuracy':>16} {'Active Contradictions':>22}")
    print("  " + "-" * 70)
    
    for s in ['static', 'additive', 'cascade']:
        c = np.array(data[s]['coh'])
        a = np.array(data[s]['acc'])
        ac = np.array(data[s]['active_cont'])
        exp1[s] = {
            'coherence': f"{c.mean():.4f} ± {c.std():.4f}",
            'accuracy': f"{a.mean():.4f} ± {a.std():.4f}",
            'active_contradictions': f"{ac.mean():.1f} ± {ac.std():.1f}",
            'coh_val': float(c.mean()), 'acc_val': float(a.mean()),
            'ac_val': float(ac.mean()),
        }
        print(f"  {s:<12} {c.mean():.4f} ± {c.std():.4f}   "
              f"{a.mean():.4f} ± {a.std():.4f}   "
              f"{ac.mean():.1f} ± {ac.std():.1f}")
    
    # Statistical tests
    def paired_test(a, b):
        t, p = stats.ttest_rel(a, b)
        pooled = np.sqrt((a.std()**2 + b.std()**2) / 2)
        d = (a.mean() - b.mean()) / pooled if pooled > 1e-10 else float('inf')
        return float(t), float(p), float(d)
    
    cc = np.array(data['cascade']['coh'])
    sc = np.array(data['static']['coh'])
    ac = np.array(data['additive']['coh'])
    ca_acc = np.array(data['cascade']['acc'])
    sa_acc = np.array(data['static']['acc'])
    aa_acc = np.array(data['additive']['acc'])
    
    tests = {}
    for name, a, b in [
        ('coh_cascade_vs_static', cc, sc),
        ('coh_cascade_vs_additive', cc, ac),
        ('acc_cascade_vs_static', ca_acc, sa_acc),
        ('acc_cascade_vs_additive', ca_acc, aa_acc),
    ]:
        t, p, d = paired_test(a, b)
        tests[name] = {'t': t, 'p': p, 'd': d}
    
    exp1['tests'] = tests
    exp1['n_cascade_events'] = len(cascade_events)
    results['exp1_paradigm_shift'] = exp1
    
    print(f"\n  Cascade events triggered: {len(cascade_events)} across {N} trials")
    print(f"\n  Statistical tests:")
    for name, t in tests.items():
        sig = '***' if t['p']<0.001 else '**' if t['p']<0.01 else '*' if t['p']<0.05 else 'ns'
        print(f"    {name}: t={t['t']:.2f}, p={t['p']:.2e}, d={t['d']:.2f} {sig}")
    
    # ─── EXP 2: CASCADE INVARIANTS ──────────────────
    print("\n" + "=" * 65)
    print("EXPERIMENT 2: Three CASCADE Invariants (n=1000)")
    print("=" * 65)
    
    n_cas = 1000
    coh_preserved = 0
    info_preserved = 0
    entropy_increased = 0
    coh_deltas = []
    info_deltas = []
    entropy_deltas = []
    
    for trial in range(n_cas):
        rng = np.random.RandomState(10000 + trial)
        pyr = Pyramid()
        
        # Random initial pyramid
        n_init = rng.randint(5, 20)
        domains = [f'd{i%4}' for i in range(n_init)]
        for i in range(n_init):
            b = Block(f'init_{i}', rng.uniform(0.5, 0.95),
                     rng.uniform(0.5, 2.5), rng.uniform(0.15, 0.7),
                     domain=domains[i])
            pyr.blocks[b.name] = b
        
        # Pick a foundation block to challenge
        foundation_blocks = [n for n, b in pyr.blocks.items() if b.layer == 'F']
        if not foundation_blocks:
            continue
        
        target = rng.choice(foundation_blocks)
        target_domain = pyr.blocks[target].domain
        
        # Create challenger with higher pi
        challenger = Block(
            f'challenger_{trial}',
            rng.uniform(0.92, 0.99),
            rng.uniform(2.2, 3.5),
            rng.uniform(0.05, 0.12),
            domain=target_domain,
            contradicts={target}
        )
        pyr.blocks[target].contradicts.add(challenger.name)
        
        log = cascade_add(pyr, challenger)
        
        if log and log.get('triggered'):
            c_before, c_after = log['coherence']
            i_before, i_after = log['information']
            e_before, e_after = log['entropy']
            
            coh_deltas.append(c_after - c_before)
            info_deltas.append(i_after - i_before)
            entropy_deltas.append(e_after - e_before)
            
            if c_after >= c_before - 1e-10: coh_preserved += 1
            if i_after >= i_before - 1e-10: info_preserved += 1
            if e_after >= e_before - 1e-10: entropy_increased += 1
    
    n_actual = len(coh_deltas)
    cd = np.array(coh_deltas)
    id_ = np.array(info_deltas)
    ed = np.array(entropy_deltas)
    
    exp2 = {
        'n_cascades': n_actual,
        'coherence_preserved': f"{coh_preserved}/{n_actual} ({coh_preserved/n_actual:.1%})",
        'information_preserved': f"{info_preserved}/{n_actual} ({info_preserved/n_actual:.1%})",
        'entropy_nondecreasing': f"{entropy_increased}/{n_actual} ({entropy_increased/n_actual:.1%})",
        'delta_coherence': f"{cd.mean():.4f} ± {cd.std():.4f}",
        'delta_information': f"{id_.mean():.4f} ± {id_.std():.4f}",
        'delta_entropy': f"{ed.mean():.4f} ± {ed.std():.4f}",
        'coh_rate': coh_preserved/n_actual,
        'info_rate': info_preserved/n_actual,
        'ent_rate': entropy_increased/n_actual,
    }
    results['exp2_invariants'] = exp2
    
    print(f"\n  Cascades triggered: {n_actual}")
    print(f"\n  Invariant 1 (Coherence ≥): {coh_preserved}/{n_actual} ({coh_preserved/n_actual:.1%})")
    print(f"    ΔC = {cd.mean():.4f} ± {cd.std():.4f}, range [{cd.min():.4f}, {cd.max():.4f}]")
    print(f"\n  Invariant 2 (Information ≥): {info_preserved}/{n_actual} ({info_preserved/n_actual:.1%})")
    print(f"    ΔI = {id_.mean():.4f} ± {id_.std():.4f}")
    print(f"\n  Invariant 3 (Entropy ≥): {entropy_increased}/{n_actual} ({entropy_increased/n_actual:.1%})")
    print(f"    ΔS = {ed.mean():.4f} ± {ed.std():.4f}")
    
    # ─── EXP 3: SEQUENTIAL COHERENCE ────────────────
    print("\n" + "=" * 65)
    print("EXPERIMENT 3: Sequential Learning (30-step trajectories)")
    print("=" * 65)
    
    N3 = 200
    final = {s: [] for s in ['static', 'additive', 'cascade']}
    mean_traj = {s: np.zeros(30) for s in ['static', 'additive', 'cascade']}
    
    for trial in range(N3):
        rng = np.random.RandomState(20000 + trial)
        blocks = make_incremental(rng, n_steps=30, n_domains=5)
        
        for sys_name, add_fn in [('static', static_add), ('additive', additive_add)]:
            pyr = Pyramid()
            traj = []
            for b in blocks:
                add_fn(pyr, b.copy())
                traj.append(pyr.coherence())
            final[sys_name].append(traj[-1])
            mean_traj[sys_name] += np.array(traj)
        
        pyr = Pyramid()
        traj = []
        for b in blocks:
            cascade_add(pyr, b.copy())
            traj.append(pyr.coherence())
        final['cascade'].append(traj[-1])
        mean_traj['cascade'] += np.array(traj)
    
    for s in mean_traj:
        mean_traj[s] /= N3
    
    exp3 = {}
    print(f"\n  n={N3} sequences, 30 blocks each\n")
    print(f"  {'System':<12} {'Final Coherence':>20} {'Mean Trajectory':>20}")
    print("  " + "-" * 55)
    
    for s in ['static', 'additive', 'cascade']:
        f = np.array(final[s])
        exp3[s] = {
            'final_mean': float(f.mean()), 'final_std': float(f.std()),
            'trajectory_mean': [float(x) for x in mean_traj[s]],
        }
        print(f"  {s:<12} {f.mean():.4f} ± {f.std():.4f}       "
              f"start={mean_traj[s][0]:.4f} → end={mean_traj[s][-1]:.4f}")
    
    cf = np.array(final['cascade'])
    sf = np.array(final['static'])
    af = np.array(final['additive'])
    
    for name, a, b in [('cascade_vs_static', cf, sf), ('cascade_vs_additive', cf, af)]:
        t, p, d = paired_test(a, b)
        exp3[name] = {'t': t, 'p': p, 'd': d}
        sig = '***' if p<0.001 else '**' if p<0.01 else '*' if p<0.05 else 'ns'
        print(f"  {name}: t={t:.2f}, p={p:.2e}, d={d:.2f} {sig}")
    
    results['exp3_sequential'] = exp3
    
    # ─── EXP 4: THRESHOLD + GAMMA SENSITIVITY ───────
    print("\n" + "=" * 65)
    print("EXPERIMENT 4: Hyperparameter Sensitivity")
    print("=" * 65)
    
    # 4a: Threshold sensitivity
    thresholds = [0.0, 0.05, 0.1, 0.15, 0.2, 0.3, 0.5, 1.0, 2.0]
    exp4a = {}
    
    for thresh in thresholds:
        cohs, accs, n_cas_list = [], [], []
        for trial in range(100):
            rng = np.random.RandomState(30000 + trial)
            classical, modern, queries = make_physics_paradigm(rng)
            pyr = Pyramid()
            for b in classical: cascade_add(pyr, b.copy(), threshold=thresh)
            events = 0
            for b in modern:
                log = cascade_add(pyr, b.copy(), threshold=thresh)
                if log: events += 1
            cohs.append(pyr.coherence())
            correct = sum(1 for d, p in queries if pyr.query(d, p) > pyr.query(d, 'classical'))
            accs.append(correct / len(queries))
            n_cas_list.append(events)
        
        exp4a[str(thresh)] = {
            'coherence': float(np.mean(cohs)),
            'accuracy': float(np.mean(accs)),
            'n_cascades': float(np.mean(n_cas_list)),
        }
    
    print(f"\n  4a: Cascade threshold (Δπ)")
    print(f"  {'Δπ':>6} {'Coherence':>12} {'Accuracy':>12} {'Cascades':>10}")
    print("  " + "-" * 44)
    for t in thresholds:
        e = exp4a[str(t)]
        print(f"  {t:>6.2f} {e['coherence']:>12.4f} {e['accuracy']:>12.4f} {e['n_cascades']:>10.1f}")
    
    # 4b: Gamma sensitivity
    gammas = [0.5, 0.6, 0.7, 0.8, 0.85, 0.9, 0.95, 0.99]
    exp4b = {}
    
    for gam in gammas:
        cohs = []
        for trial in range(100):
            rng = np.random.RandomState(30000 + trial)
            classical, modern, queries = make_physics_paradigm(rng)
            pyr = Pyramid()
            for b in classical: cascade_add(pyr, b.copy(), gamma=gam)
            for b in modern: cascade_add(pyr, b.copy(), gamma=gam)
            cohs.append(pyr.coherence())
        exp4b[str(gam)] = {'coherence': float(np.mean(cohs))}
    
    print(f"\n  4b: Compression decay (γ)")
    print(f"  {'γ':>6} {'Coherence':>12}")
    print("  " + "-" * 20)
    for g in gammas:
        print(f"  {g:>6.2f} {exp4b[str(g)]['coherence']:>12.4f}")
    
    results['exp4_sensitivity'] = {'threshold': exp4a, 'gamma': exp4b}
    
    # ─── EXP 5: ABLATION ────────────────────────────
    print("\n" + "=" * 65)
    print("EXPERIMENT 5: Ablation Study")
    print("=" * 65)
    
    N5 = 200
    ablations = {}
    
    configs = {
        'Full CASCADE': lambda pyr, b: cascade_add(pyr, b),
        'No cascade (static)': lambda pyr, b: static_add(pyr, b),
        'No truth pressure': 'special_random_pi',
        'No contextualization': 'special_no_context',
        'Binary layers (F/E)': 'special_binary',
    }
    
    for config_name in configs:
        cohs, accs, conts = [], [], []
        for trial in range(N5):
            rng = np.random.RandomState(40000 + trial)
            classical, modern, queries = make_physics_paradigm(rng)
            pyr = Pyramid()
            
            if config_name == 'No truth pressure':
                # Randomize pi components
                for b in classical:
                    b2 = b.copy()
                    b2.evidence = rng.uniform(0.3, 1.0)
                    b2.power = rng.uniform(0.3, 3.0)
                    b2.entropy = rng.uniform(0.1, 1.0)
                    cascade_add(pyr, b2)
                for b in modern:
                    b2 = b.copy()
                    b2.evidence = rng.uniform(0.3, 1.0)
                    b2.power = rng.uniform(0.3, 3.0)
                    b2.entropy = rng.uniform(0.1, 1.0)
                    cascade_add(pyr, b2)
            elif config_name == 'No contextualization':
                # CASCADE but don't contextualize (just add, no regime change)
                for b in classical: pyr.blocks[b.name] = b.copy()
                for b in modern: pyr.blocks[b.name] = b.copy()
            elif config_name == 'Binary layers (F/E)':
                # Only F and E, no T buffer
                for b in classical: cascade_add(pyr, b.copy())
                for b in modern: cascade_add(pyr, b.copy())
                # Force T blocks to E
                for n, blk in pyr.blocks.items():
                    if blk.layer == 'T':
                        blk.entropy *= 1.5  # push to E
            else:
                add_fn = configs[config_name]
                for b in classical: add_fn(pyr, b.copy())
                for b in modern: add_fn(pyr, b.copy())
            
            cohs.append(pyr.coherence())
            correct = sum(1 for d,p in queries if pyr.query(d,p) > pyr.query(d,'classical'))
            accs.append(correct / len(queries))
            conts.append(pyr._active_contradictions())
        
        c = np.array(cohs)
        a = np.array(accs)
        ct = np.array(conts)
        ablations[config_name] = {
            'coherence': f"{c.mean():.4f} ± {c.std():.4f}",
            'accuracy': f"{a.mean():.4f} ± {a.std():.4f}",
            'contradictions': f"{ct.mean():.1f} ± {ct.std():.1f}",
            'coh_val': float(c.mean()), 'acc_val': float(a.mean()),
            'cont_val': float(ct.mean()),
        }
    
    results['exp5_ablation'] = ablations
    
    print(f"\n  n={N5} trials\n")
    print(f"  {'Configuration':<28} {'Coherence':>16} {'Accuracy':>16} {'Contradictions':>16}")
    print("  " + "-" * 80)
    for cfg, data in ablations.items():
        print(f"  {cfg:<28} {data['coherence']:>16} {data['accuracy']:>16} {data['contradictions']:>16}")
    
    # ─── EXP 6: SCALING ─────────────────────────────
    print("\n" + "=" * 65)
    print("EXPERIMENT 6: Computational Scaling")
    print("=" * 65)
    
    sizes = [10, 25, 50, 100, 250, 500, 1000, 2500]
    exp6 = {}
    
    for n in sizes:
        times = []
        for rep in range(3):
            rng = np.random.RandomState(50000 + n + rep)
            pyr = Pyramid()
            t0 = time.time()
            for i in range(n):
                contradicts = set()
                if i > 0 and rng.random() < 0.15:
                    contradicts.add(f'b_{rng.randint(0, i)}')
                b = Block(f'b_{i}', rng.uniform(0.4, 1.0),
                         rng.uniform(0.3, 3.0), rng.uniform(0.05, 0.9),
                         domain=f'd{i%5}', contradicts=contradicts)
                cascade_add(pyr, b)
            dt = time.time() - t0
            times.append(dt)
        
        exp6[str(n)] = {
            'time_mean': float(np.mean(times)),
            'time_std': float(np.std(times)),
        }
    
    results['exp6_scaling'] = exp6
    
    print(f"\n  {'N':>6} {'Time (s)':>14}")
    print("  " + "-" * 22)
    for n in sizes:
        e = exp6[str(n)]
        print(f"  {n:>6} {e['time_mean']:>10.4f} ± {e['time_std']:.4f}")
    
    # Fit scaling law
    ns = np.array(sizes, dtype=float)
    ts = np.array([exp6[str(n)]['time_mean'] for n in sizes])
    log_ns = np.log(ns)
    log_ts = np.log(ts)
    slope, intercept, r, p, se = stats.linregress(log_ns, log_ts)
    exp6['scaling_exponent'] = float(slope)
    exp6['scaling_r2'] = float(r**2)
    print(f"\n  Scaling: T ∝ N^{slope:.2f} (R²={r**2:.4f})")
    
    # ─── SAVE ────────────────────────────────────────
    with open('cascade_real_results.json', 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    print("\n" + "=" * 65)
    print("ALL RESULTS SAVED: cascade_real_results.json")
    print("=" * 65)
    return results

if __name__ == '__main__':
    t0 = time.time()
    run_all()
    print(f"\nTotal time: {time.time()-t0:.1f}s")
