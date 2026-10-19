"""Longitudinal choice-change analysis (synthetic design fixture only)."""
from __future__ import annotations
from dataclasses import replace
from sovereignty_surface import Snapshot, standard_edges, evaluate


def preference_change_demo() -> dict:
    """Same observed use, one person revises intent; a requested change can be reachable or not."""
    base={'id':'voluntary-collaboration','current':'collaborate','max_friction_minutes':5,
          'sessions':5,'stated_preference_evidenced':True}
    good=standard_edges(); bad=standard_edges(offboarding='blocked')
    weeks=[]
    for week,desired in enumerate(('collaborate','collaborate','off','off')):
        open_snapshot=Snapshot(week=week,desired=desired,edges=good,**base)
        blocked_snapshot=Snapshot(week=week,desired=desired,edges=bad,**base)
        weeks.append({'week':week,'use_sessions':5,'requested':desired,
                      'open':evaluate(open_snapshot)['verdict'],
                      'constrained':evaluate(blocked_snapshot)['verdict']})
    return {'status':'FICTIONAL_DYNAMIC_PREFERENCE_PROBE','weeks':weeks,
            'effect':'At weeks 0–1 both products meet the declared coupling mode; after the user revises the goal to OFF, their structural affordances diverge.',
            'caution':'At-target status is not proof of free choice. Verified means fixture-verified only.'}


def reverse_consent_probe() -> dict:
    """Someone may choose to restart using AI; exit-only ideology can obstruct choice."""
    open_graph=standard_edges()
    no_return=standard_edges(consent='blocked')
    s=Snapshot('return',2,0,'off','consult',5,open_graph)
    return {'open':evaluate(s)['verdict'],
            'no_return':evaluate(replace(s,edges=no_return))['verdict'],
            'interpretation':'An effective return option can be a freedom-relevant affordance.'}

if __name__=='__main__':
    import json
    print(json.dumps({'change':preference_change_demo(),'return':reverse_consent_probe()},indent=2))
