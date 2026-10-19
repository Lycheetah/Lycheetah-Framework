"""Sovereignty Surface: an auditable option-reachability *toy instrument*.

Do not use this code to assess anyone's moral worth, psychological state, autonomy,
consent, AI addiction, consciousness or metaphysical free will. Its results only
reflect declared edges/costs/evidence in a synthetic interface/service graph.

Each transition represents an *assumed* way a user can change how they use an
AI service. VERIFIED means verified in a supplied fixture, not independently
verified outside this run. CLAIMED means an interface/document asserts a path.
UNKNOWN is preserved rather than treated as either working or absent.

This is a conventional shortest-path formulation, not a new mathematical law.
"""
from __future__ import annotations
from dataclasses import dataclass
from heapq import heappush, heappop
from typing import Literal

Mode = Literal['off','consult','collaborate','delegate']
Evidence = Literal['verified','claimed','unknown','blocked']
Verdict = Literal['verified','claimed_only','unknown','blocked','at_target','preference_unknown']

@dataclass(frozen=True)
class Transition:
    source: Mode
    target: Mode
    friction_minutes: int
    evidence: Evidence
    user_initiated: bool = True
    name: str = ''

    def __post_init__(self):
        if self.friction_minutes < 0 or isinstance(self.friction_minutes, bool):
            raise ValueError('friction must be a nonnegative integer')
        if self.source == self.target:
            raise ValueError('no self transition')
        if self.evidence not in ('verified','claimed','unknown','blocked'):
            raise ValueError('bad evidence')
        if self.source not in ('off','consult','collaborate','delegate') or self.target not in ('off','consult','collaborate','delegate'):
            raise ValueError('bad mode')

@dataclass(frozen=True)
class Snapshot:
    id: str
    week: int
    sessions: int
    current: Mode
    desired: Mode | None
    max_friction_minutes: int
    edges: tuple[Transition, ...]
    stated_preference_evidenced: bool = True
    observation_note: str = ''

    def __post_init__(self):
        if self.week < 0 or self.sessions < 0 or self.max_friction_minutes < 0:
            raise ValueError('nonnegative week, sessions and friction budget required')
        if self.current not in ('off','consult','collaborate','delegate'):
            raise ValueError('bad current mode')
        if self.desired is not None and self.desired not in ('off','consult','collaborate','delegate'):
            raise ValueError('bad desired mode')


def _shortest(snapshot: Snapshot, allowed: frozenset[Evidence]) -> tuple[int,list[str]] | None:
    """Conventional Dijkstra for nonnegative explicit fiction-friction costs."""
    if snapshot.desired is None: return None
    q: list[tuple[int, Mode, tuple[str,...]]] = [(0,snapshot.current,tuple())]
    best: dict[Mode,int] = {}
    while q:
        cost,mode,names = heappop(q)
        if cost > snapshot.max_friction_minutes or cost >= best.get(mode, float('inf')):
            continue
        best[mode] = cost
        if mode == snapshot.desired:
            return cost,list(names)
        for edge in snapshot.edges:
            if edge.source == mode and edge.user_initiated and edge.evidence in allowed:
                heappush(q,(cost + edge.friction_minutes,edge.target,names+(edge.name or f'{edge.source}->{edge.target}',)))
    return None


def evaluate(snapshot: Snapshot) -> dict:
    """Never report a person's free will. Evidence is a fixture status only."""
    base = {'id':snapshot.id,'week':snapshot.week,'observed_sessions':snapshot.sessions,
            'from':snapshot.current,'desired':snapshot.desired,
            'budget_minutes':snapshot.max_friction_minutes,
            'human_sovereignty_score':None,
            'claim_boundary':'Interface transition reachability only; not evidence of autonomous choice.'}
    if snapshot.desired is None or not snapshot.stated_preference_evidenced:
        return {**base,'verdict':'preference_unknown','path':None,'cost_minutes':None,
                'interpretation':'No evidenced current preference: cannot infer consent from usage.'}
    if snapshot.current == snapshot.desired:
        return {**base,'verdict':'at_target','path':[],'cost_minutes':0,
                'interpretation':'At declared target; this alone does not prove free or informed choice.'}
    for allowed, verdict in (
        (frozenset(('verified',)),'verified'),
        (frozenset(('verified','claimed')),'claimed_only'),
        (frozenset(('verified','claimed','unknown')),'unknown'),
    ):
        result = _shortest(snapshot,allowed)
        if result:
            return {**base,'verdict':verdict,'path':result[1],
                    'cost_minutes':result[0],
                    'interpretation': {'verified':'Reachable through test-fixture verified transitions.',
                        'claimed_only':'Reachable if unverified product claims are honoured.',
                        'unknown':'Reachable only if untested/unknown transitions work.'}[verdict]}
    return {**base,'verdict':'blocked','path':None,'cost_minutes':None,
            'interpretation':'No user-initiated transition path in supplied graph meets the declared budget.'}


def usage_only(snapshot: Snapshot) -> tuple[int,int]:
    """Deliberately information-poor baseline; an identical trace gives identical output."""
    return (snapshot.week, snapshot.sessions)


def transition(source: Mode,target: Mode,evidence: Evidence='verified',cost: int=2,
               name: str='',user_initiated: bool=True) -> Transition:
    return Transition(source,target,cost,evidence,user_initiated,name)


def standard_edges(*,offboarding: Evidence='verified', portability: Evidence='verified',
                   consent: Evidence='verified', cost: int=2) -> tuple[Transition,...]:
    # Two-way choice: offboarding and on-boarding independent directions.
    # Offboarding through consult models an export + end path; direct offboarding
    # models stopping immediately, not assuming data portability.
    return (
      transition('delegate','collaborate',consent,1,'reduce delegation'),
      transition('collaborate','consult',portability,cost,'shift to consultation'),
      transition('consult','off',offboarding,cost,'end service'),
      transition('delegate','off',offboarding,cost+4,'stop all delegations'),
      transition('collaborate','off',offboarding,cost+4,'end collaboration'),
      transition('off','consult',consent,1,'return to consultation'),
      transition('consult','collaborate',consent,1,'increase collaboration'),
      transition('collaborate','delegate',consent,1,'delegate with review'),
    )


def paired_case(label: str, *,sessions:tuple[int,...],desired: Mode,current:Mode,
                good:tuple[Transition,...],bad:tuple[Transition,...],budget:int=5):
    """Observational equivalence: pair's sessions and time are EXACTLY matched."""
    a=[];b=[]
    for w,n in enumerate(sessions):
        a.append(Snapshot(label+'_open',w,n,current,desired,budget,good,True,'synthetic fictional participant'))
        b.append(Snapshot(label+'_constrained',w,n,current,desired,budget,bad,True,'synthetic fictional participant'))
    return a,b


def make_corpus() -> dict[str,tuple[list[Snapshot],list[Snapshot]]]:
    good=standard_edges()
    # Distinct capabilities: revoke, data export, change engagement mode, re-enter.
    blocked_exit=standard_edges(offboarding='blocked')
    claimed_exit=standard_edges(offboarding='claimed')
    unknown_exit=standard_edges(offboarding='unknown')
    costly=standard_edges(cost=30)
    blocked_shift=standard_edges(portability='blocked',offboarding='blocked')
    blocked_entry=standard_edges(consent='blocked')
    designs={
      'accessibility_free_continuation': ('delegate','collaborate',good,blocked_shift,5,(5,5,5,5)),
      'desire_to_leave': ('collaborate','off',good,blocked_exit,5,(4,4,4,4)),
      'desire_to_pause': ('consult','off',good,claimed_exit,5,(3,3,3,3)),
      'desire_to_export': ('collaborate','consult',good,blocked_shift,5,(6,6,6,6)),
      'delegation_revocation': ('delegate','off',good,blocked_exit,9,(7,7,7,7)),
      'cost_prohibitive_exit': ('collaborate','off',good,costly,5,(2,2,2,2)),
      'unknown_exit_path': ('consult','off',good,unknown_exit,5,(1,1,1,1)),
      'chosen_return': ('off','consult',good,blocked_entry,5,(0,0,0,0)),
    }
    out={}
    for label,(cur,dst,edges_a,edges_b,budget,sessions) in designs.items():
        out[label]=paired_case(label,sessions=sessions,current=cur,desired=dst,
                               good=edges_a,bad=edges_b,budget=budget)
    return out


def benchmark() -> dict:
    corpus=make_corpus(); rows=[]
    for name,(open_rows,constrained_rows) in corpus.items():
        a=open_rows[-1];b=constrained_rows[-1]
        r1=evaluate(a);r2=evaluate(b)
        rows.append({'scenario':name,'sessions':list(x.sessions for x in open_rows),
                     'desired':a.desired,'current':a.current,
                     'usage_indistinguishable':list(map(usage_only,open_rows))==list(map(usage_only,constrained_rows)),
                     'open_verdict':r1['verdict'],'constrained_verdict':r2['verdict'],
                     'open_path':r1['path'],'constrained_path':r2['path']})
    return {'status':'FULLY_SYNTHETIC_OBSERVATIONAL_EQUIVALENCE_DEMONSTRATION',
            'pairs':len(rows),'snapshots':sum(len(a)+len(b) for a,b in corpus.values()),
            'matched_usage_pairs':sum(r['usage_indistinguishable'] for r in rows),
            'different_surface_verdicts':sum(r['open_verdict']!=r['constrained_verdict'] for r in rows),
            'human_freedom_measured':False,'real_users_tested':0,'model_eval':False,
            'claim':'User frequency alone cannot distinguish cases with identical frequency and different observed affordances.',
            'rows':rows}

if __name__=='__main__':
    import json
    print(json.dumps(benchmark(),indent=2))
