"""Separate-process kill-point laboratory; synthetic localhost-only service.

Runs child controller + child HTTP provider with independently committed SQLite stores.
Outcomes are compared with synthetic provider ground truth (NOT external attestation).
"""
import json, os, subprocess, sys, tempfile, time
from pathlib import Path
from contextlib import contextmanager
from controller import start, job, request

HERE=Path(__file__).resolve().parent

@contextmanager
def instance(kind='write'):
    with tempfile.TemporaryDirectory(prefix='earned_light_f7_') as folder:
        root=Path(folder);ctrl=str(root/'controller.sqlite');prov=str(root/'provider.sqlite');ready=str(root/'port.txt')
        server=subprocess.Popen([sys.executable,str(HERE/'provider.py'),'--db',prov,'--ready',ready],cwd=HERE,stdout=subprocess.DEVNULL,stderr=subprocess.PIPE)
        try:
            deadline=time.monotonic()+7
            while not Path(ready).exists() and time.monotonic()<deadline:
                if server.poll() is not None:raise RuntimeError('provider terminated: '+server.stderr.read().decode())
                time.sleep(.02)
            if not Path(ready).exists():raise TimeoutError('provider did not start')
            url='http://127.0.0.1:'+Path(ready).read_text()
            start(ctrl,kind)
            yield ctrl,url
        finally:
            server.terminate()
            try:server.wait(timeout=3)
            except subprocess.TimeoutExpired:server.kill();server.wait(timeout=3)
            server.stderr.close()

def worker(action,ctrl,url,cut=None,unsafe=False,no_query=False):
    argv=[sys.executable,str(HERE/'worker.py'),action,'--db',ctrl,'--url',url]
    if cut:argv+=['--cut',cut]
    if unsafe:argv+=['--unsafe-nonidempotent']
    if no_query:argv+=['--no-query']
    p=subprocess.run(argv,cwd=HERE,capture_output=True,text=True,timeout=7)
    return dict(code=p.returncode,output=json.loads(p.stdout) if p.returncode==0 and p.stdout else None,stderr=p.stderr)

def run_trial(kind,cut,comp_cut=None,query=True):
    with instance(kind) as (ctrl,url):
        a=worker('dispatch',ctrl,url,cut=cut)
        w=worker('revoke',ctrl,url)
        b=worker('recover',ctrl,url,cut=comp_cut,no_query=not query)
        if b['code']==73:b=worker('recover',ctrl,url,no_query=not query)
        snapshot=request(url,'/state')
        r=worker('report',ctrl,url,no_query=not query)['output']
        count=len(snapshot['effects'])
        irreversible=count>0 and kind=='notify'
        compensated=bool(snapshot['compensations'] and snapshot['compensations'][0]['status']=='restored')
        return dict(kind=kind,dispatch_cut=cut or 'none',compensation_cut=comp_cut or 'none',query_available=query,
                    kill_code=a['code'],revoked=w['code']==0,controller_status=r['controller_status'],
                    consequences_reported=b['output']['terminal_status'] if b['output'] else 'failure',
                    remote_effect_count=count,compensation_count=len(snapshot['compensations']),
                    irreversible_remote=irreversible,restored_remote=compensated,
                    report_exposes_unknown=b['output'] is not None and b['output']['terminal_status']=='unresolved_effect')

def retry_trial(dedup):
    with instance('write') as (ctrl,url):
        first=worker('dispatch',ctrl,url,cut='after_commit_before_ack',unsafe=not dedup)
        assert first['code']==73
        # A conventional durable outbox retries with same stable operation ID; if
        # provider is not idempotent, duplicate remote effects occur.
        second=worker('dispatch',ctrl,url,unsafe=not dedup)
        snapshot=request(url,'/state')
        return dict(baseline='durable_outbox_idempotent' if dedup else 'naive_nonidempotent_retry',
                    first_killed=first['code']==73,second_completed=second['code']==0,
                    effects=len(snapshot['effects']),distinct_operation_ids=len(snapshot['operations']))

def run_all():
    scenarios=[]
    for kind in ('write','notify'):
        for cut in ('before_reserve','after_reserve_before_send','after_commit_before_ack','after_ack_before_return',None):
            scenarios.append(run_trial(kind,cut))
            print('trial complete:',kind,cut or 'none',flush=True)
        for cut in ('after_compensation_before_ack','after_compensation_ack'):
            scenarios.append(run_trial(kind,'after_ack_before_return',comp_cut=cut))
            print('comp trial complete:',kind,cut,flush=True)
        scenarios.append(run_trial(kind,'after_commit_before_ack',query=False))
        print('no-query trial complete:',kind,flush=True)
    results=dict(trials=scenarios,comparison=[retry_trial(True),retry_trial(False)],
                 disclaimer='Manually designed synthetic separate-process localhost trials, not model checking or production deployment.')
    out=HERE/'results';out.mkdir(exist_ok=True)
    (out/'trial_results.json').write_text(json.dumps(results,indent=2,sort_keys=True)+'\n')
    import csv
    with (out/'trial_results.csv').open('w',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=list(scenarios[0]));writer.writeheader();writer.writerows(scenarios)
    return results


def restartable_provider_trial():
    """Kill provider after it committed, fail recovery, then restart from its DB.

    A restarted provider supplies the same operation receipt; no separate attestor.
    """
    with tempfile.TemporaryDirectory(prefix='earned_light_f7_restart_') as folder:
        root=Path(folder);ctrl=str(root/'controller.sqlite');prov=str(root/'provider.sqlite')
        def launch(tag):
            ready=root/(tag+'.port')
            p=subprocess.Popen([sys.executable,str(HERE/'provider.py'),'--db',prov,'--ready',str(ready)],cwd=HERE,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
            deadline=time.monotonic()+7
            while not ready.exists() and time.monotonic()<deadline:
                if p.poll() is not None:raise RuntimeError('provider startup failure')
                time.sleep(.02)
            if not ready.exists():raise TimeoutError('restart provider startup timeout')
            return p,'http://127.0.0.1:'+ready.read_text()
        p,url=launch('initial')
        try:
            start(ctrl,'write')
            first=worker('dispatch',ctrl,url,cut='after_commit_before_ack')
            p.kill();p.wait(timeout=5)
            worker('revoke',ctrl,url)
            failed=worker('recover',ctrl,url)
            p2,new_url=launch('restarted')
            try:
                recovered=worker('recover',ctrl,new_url)
                s=request(new_url,'/state')
            finally:p2.kill();p2.wait(timeout=5)
        finally:
            if p.poll() is None:p.kill();p.wait(timeout=5)
        return dict(dispatch_crashed=first['code']==73,
                    during_outage=failed['output']['terminal_status'],
                    after_provider_restart=recovered['output']['terminal_status'],
                    remote_effects=len(s['effects']),compensations=len(s['compensations']))

if __name__=='__main__':
    r=run_all()
    r['provider_restart']=restartable_provider_trial()
    (HERE/'results'/'trial_results.json').write_text(json.dumps(r,indent=2,sort_keys=True)+'\n')
    print(json.dumps({'trials':len(r['trials']),
                      'categories':{s:sum(x['consequences_reported']==s for x in r['trials']) for s in sorted(set(x['consequences_reported'] for x in r['trials']))},
                      'comparison':r['comparison'], 'provider_restart':r['provider_restart']},indent=2))
