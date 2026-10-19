"""Transparent parameter sweep showing impact of an explicit retention incentive."""
from self_displacement import SCENARIOS, choose
import json

def run():
    rows=[]
    for w in (0,0.5,1,2,3,4,5,6,8,10,12):
        outcomes=[choose(s,'retention', retention_weight=w) for s in SCENARIOS]
        rows.append({'retention_weight':w,
                     'acceptable':sum(o.id in s.acceptable for o,s in zip(outcomes,SCENARIOS)),
                     'pressure_choices':sum(o.avoidable_pressure for o in outcomes),
                     'predicted_followups':sum(o.followups for o in outcomes)})
    return {'status':'AUTHOR_CONSTRUCTED_SENSITIVITY_NOT_CAUSAL_EVIDENCE','rows':rows}
if __name__=='__main__': print(json.dumps(run(),indent=2))
