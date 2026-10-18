"""Separate-process crash injector; exit codes are part of scenario evidence."""
import os,sys
from lab_fixture import authority,provider,ACTION
from crashsafe_authority import SimulatedIdempotentProvider

def main():
    if len(sys.argv)!=5: raise SystemExit('usage: crash_worker.py AUTHDB PROVIDERDB MODE EFFECT_ID')
    authdb,providerdb,mode,effect_id=sys.argv[1:]
    f=authority(authdb);p=provider(providerdb)
    if mode=='crash-after-challenge-commit':
        body=f.challenge_body('crm','nonce-'+effect_id)
        assert f.challenge(body,f.sign_challenge(body))
        os._exit(93)
    if mode=='crash-during-challenge-transaction':
        body=f.challenge_body('crm','nonce-'+effect_id)
        with f._db() as c:
            c.execute('BEGIN IMMEDIATE')
            c.execute('INSERT INTO used_nonces VALUES(?)',(body['nonce'],))
            seq=f._append(c,'CHALLENGE',body)
            c.execute('INSERT INTO disputes VALUES(?,?)',('crm',seq))
            f._advance_head(c,'CHALLENGE',body)
            os._exit(94)  # never committed: sqlite must roll back entire mutation
    witness=f.witness(effect_id)
    res=f.reserve_send(effect_id,ACTION,witness,50)
    assert res.allowed, res
    if mode=='crash-after-reserve':
        os._exit(90)
    result=p.apply(effect_id,ACTION)
    if mode=='crash-after-provider-commit':
        os._exit(91)
    if mode=='complete':
        assert f.acknowledge(effect_id,result)
        return
    raise SystemExit('unknown mode')

if __name__=='__main__': main()
