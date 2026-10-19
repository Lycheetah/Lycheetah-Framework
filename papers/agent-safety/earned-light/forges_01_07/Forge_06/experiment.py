"""Repeatable, hand-authored Forge VI synthetic scenarios. No live external effects."""
import csv, json, tempfile, pathlib
from right_of_return import ReturnController, SimulatedProvider, ConventionalSagaBaseline, SnapshotBaseline, Rejected, Conflict, sign_operator_request

KEY = b'synthetic-key-not-suitable-for-deployment'


def lab():
    td=tempfile.TemporaryDirectory()
    root=pathlib.Path(td.name)
    provider=SimulatedProvider(root/'provider.db')
    ctrl=ReturnController(root/'control.db', provider, KEY,clock=lambda:100)
    ctrl.grant('agent',['write','notify'])
    provider.seed('rule',{'value':'human-original'})
    count=[0]
    def approve(action):
        count[0]+=1
        return sign_operator_request(KEY,action,'agent',nonce=f'test-nonce-{count[0]}',expires=200)
    return td,provider,ctrl,approve


def put(c,p,op,value):
    now=p.current('rule')
    c.propose('agent',op,'write','rule',{'value':value},now['version'])
    return c.dispatch(op)


def scenario(name):
    td,p,c,approve=lab()
    try:
        if name=='simple_write':
            put(c,p,'a','AI');c.revoke('agent',approve('revoke'))
            results=c.return_to_human('agent',approve('return'))
        elif name=='chained_writes':
            put(c,p,'a','A');put(c,p,'b','B');c.revoke('agent',approve('revoke'))
            results=c.return_to_human('agent',approve('return'))
        elif name=='third_party_conflict':
            put(c,p,'a','AI');p.human_write('rule',{'value':'human-new'})
            c.revoke('agent',approve('revoke'))
            results=c.return_to_human('agent',approve('return'))
        elif name=='irreversible_notification':
            c.propose('agent','a','notify','member@example.test',{'message':'sent'})
            c.dispatch('a');c.revoke('agent',approve('revoke'))
            results=c.return_to_human('agent',approve('return'))
        elif name=='revoked_before_dispatch':
            c.propose('agent','a','write','rule',{'value':'AI'},0)
            c.revoke('agent',approve('revoke'))
            c.dispatch('a');results=c.return_to_human('agent',approve('return'))
        elif name=='revoked_during_flight':
            c.propose('agent','a','write','rule',{'value':'AI'},0)
            c.dispatch('a',after_reservation=lambda:c.revoke('agent',approve('revoke')))
            results=c.return_to_human('agent',approve('return'))
        elif name=='lost_ack_provider_observed':
            c.propose('agent','a','write','rule',{'value':'AI'},0)
            c.dispatch('a',simulate_lost_ack=True)
            c.revoke('agent',approve('revoke'));results=c.return_to_human('agent',approve('return'))
        elif name=='lost_ack_provider_unobservable':
            c.propose('agent','a','write','rule',{'value':'AI'},0)
            c.dispatch('a',simulate_lost_ack=True)
            p.receipt=lambda op:None
            c.revoke('agent',approve('revoke'));results=c.return_to_human('agent',approve('return'))
        elif name=='mixed_write_and_notification':
            put(c,p,'a','AI')
            c.propose('agent','n','notify','member@example.test',{'message':'sent'})
            c.dispatch('n');c.revoke('agent',approve('revoke'))
            results=c.return_to_human('agent',approve('return'))
        elif name=='expired_operator_authority':
            put(c,p,'a','AI')
            bad=sign_operator_request(KEY,'revoke','agent',nonce='expired-test',expires=99)
            try: c.revoke('agent',bad); results=[{'status':'incorrectly_permitted'}]
            except Rejected: results=[{'status':'revocation_rejected'}]
        elif name=='no_grant_action_after_revocation':
            c.revoke('agent',approve('revoke'))
            try:
                c.propose('agent','a','write','rule',{'value':'AI'},0)
                results=[{'status':'incorrectly_permitted'}]
            except Rejected: results=[{'status':'new_work_rejected'}]
        else: raise KeyError(name)
        final=p.current('rule')['value']
        return dict(scenario=name, statuses=[r['status'] for r in results], final_value=final, claims=len(c.view('agent')))
    finally: td.cleanup()


def saga_baseline(name):
    td,p,c,approve=lab()
    try:
        if name=='simple_write': put(c,p,'a','AI'); ids=['a']
        elif name=='chained_writes': put(c,p,'a','A');put(c,p,'b','B');ids=['a','b']
        elif name=='third_party_conflict': put(c,p,'a','AI');p.human_write('rule',{'value':'human-new'});ids=['a']
        elif name=='irreversible_notification':
            c.propose('agent','a','notify','member@example.test',{'message':'sent'});c.dispatch('a');ids=['a']
        else: raise KeyError(name)
        statuses=[r['status'] for r in ConventionalSagaBaseline.compensate_all(p,ids)]
        return dict(scenario=name,statuses=statuses,final_value=p.current('rule')['value'])
    finally: td.cleanup()


def main():
    cases=['simple_write','chained_writes','third_party_conflict','irreversible_notification',
           'revoked_before_dispatch','revoked_during_flight','lost_ack_provider_observed',
           'lost_ack_provider_unobservable','mixed_write_and_notification',
           'expired_operator_authority','no_grant_action_after_revocation']
    data=[scenario(case) for case in cases]
    baselines=[saga_baseline(case) for case in cases[:4]]
    output=pathlib.Path(__file__).parent/'results'
    output.mkdir(exist_ok=True)
    with open(output/'scenario_results.json','w') as f:
        json.dump(dict(prototype=data,strong_saga_baseline=baselines),f,indent=2)
    with open(output/'scenario_results.csv','w',newline='') as f:
        writer=csv.writer(f);writer.writerow(['scenario','status_list','final_rule_value','number_of_intents'])
        for row in data: writer.writerow([row['scenario'],';'.join(row['statuses']),row['final_value']['value'],row['claims']])
    for row in data: print(f"{row['scenario']:<35} {', '.join(row['statuses'])}")
    print('Strong conventional saga comparison:')
    for row in baselines: print(f"{row['scenario']:<35} {', '.join(row['statuses'])}")

if __name__ == '__main__': main()
