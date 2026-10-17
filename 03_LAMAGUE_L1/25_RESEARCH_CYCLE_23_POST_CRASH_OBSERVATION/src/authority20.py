"""Cycle20: original-grant cryptographic verification + bounded multi-file recovery.
This is a local reference inspector, not the Cycle18 persistent witness implementation.
"""
import base64, hashlib, json, sqlite3, stat
from pathlib import Path
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
import execution_boundary as auth
from authjournal15 import canon, digest
from witness17 import validate_records, read_anchor

class Refusal(Exception): pass


def verify_original_grant(plan, envelope, trusted_keys, binding, *, now=None):
    """Verify original grant signature and signed exact-plan binding.
    Without now, signature/grant structure are verified, but expiry is NOT established.
    """
    try:
        grant=envelope['grant']
        if set(envelope)!={'grant','signature_ed25519_b64'} or not isinstance(grant,dict):raise Refusal('grant shape')
        key=trusted_keys[grant['signer_id']]
        if not isinstance(key,bytes) or len(key)!=32:raise Refusal('key shape')
        sig=base64.b64decode(envelope['signature_ed25519_b64'],validate=True)
        Ed25519PublicKey.from_public_bytes(key).verify(sig, auth.canonical(grant))
        if len(sig)!=64:raise Refusal('signature length')
        if grant['protocol']!=auth.PROTOCOL or grant['plan_sha256']!=plan['plan_sha256'] or grant['packet_sha256']!=plan['packet_sha256'] or grant['assertion']!=auth.DIRECTIONS:raise Refusal('grant mismatched plan')
        if not isinstance(grant['nonce'],str) or len(grant['nonce'])!=64:raise Refusal('nonce')
        if grant['roots']!={'source':grant['roots']['source'],'destination':grant['roots']['destination']}:raise Refusal('root shape')
        if now is not None:
            issued,expiry=auth.parse_z(grant['issued_at']),auth.parse_z(grant['expires_at'])
            if not issued<=now<expiry:raise Refusal('grant expired or future dated')
        expected={'protocol':'C20-ORIGINAL-GRANT-v1',
                  'plan_sha256':plan['plan_sha256'],
                  'packet_sha256':plan['packet_sha256'],
                  'grant_nonce':grant['nonce'],
                  'grant_sha256':hashlib.sha256(canon(envelope)).hexdigest(),
                  'expected':{a['destination_relative']:{'sha256':a['source_sha256'],'bytes':a['source_bytes']} for a in plan['actions']}}
        if binding != expected:raise Refusal('binding not derived from signed grant and exact plan')
        return {'status':'GRANT_SIGNATURE_AND_BINDING_VALID','plan_sha256':plan['plan_sha256'],'nonce':grant['nonce'],'expiry_checked':now is not None}
    except Exception as exc:
        if isinstance(exc,Refusal):raise
        raise Refusal('original grant invalid: '+type(exc).__name__) from exc


def build_binding(plan,envelope):
    return {'protocol':'C20-ORIGINAL-GRANT-v1','plan_sha256':plan['plan_sha256'],
      'packet_sha256':plan['packet_sha256'],'grant_nonce':envelope['grant']['nonce'],
      'grant_sha256':hashlib.sha256(canon(envelope)).hexdigest(),
      'expected':{a['destination_relative']:{'sha256':a['source_sha256'],'bytes':a['source_bytes']} for a in plan['actions']}}


def file_observation(root, relative, expected):
    """No-follow path walk from directory fd; uses trusted quiet directory, not concurrent-writer safe."""
    parts=relative.split('/')
    if not parts or any(x in ('','.','..') for x in parts):return 'UNSAFE_PATH'
    import os
    fd=os.open(root,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW)
    try:
        for part in parts[:-1]:
            try:n=os.open(part,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW,dir_fd=fd)
            except FileNotFoundError:return 'ABSENT'
            except OSError:return 'UNSAFE_TYPE'
            os.close(fd);fd=n
        try: f=os.open(parts[-1],os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK,dir_fd=fd)
        except FileNotFoundError:return 'ABSENT'
        except OSError:return 'UNSAFE_TYPE'
        try:
            s=os.fstat(f)
            if not stat.S_ISREG(s.st_mode):return 'UNSAFE_TYPE'
            if s.st_size!=expected['bytes']:return 'MISMATCH'
            h=hashlib.sha256()
            while True:
                chunk=os.read(f,65536)
                if not chunk:break
                h.update(chunk)
            return 'MATCH' if h.hexdigest()==expected['sha256'] else 'MISMATCH'
        finally:os.close(f)
    finally:os.close(fd)


def classify(binding, published_root, *, journal_stage, checkpoint_state, ledger_state):
    statuses={rel:file_observation(published_root,rel,info) for rel,info in binding['expected'].items()}
    values=list(statuses.values())
    if not values:state='QUARANTINE_EMPTY_SCOPE'
    elif checkpoint_state!='MATCH' or any(x in ('MISMATCH','UNSAFE_TYPE','UNSAFE_PATH') for x in values):state='QUARANTINE'
    elif all(x=='ABSENT' for x in values):state='NOT_PUBLISHED'
    elif any(x=='MATCH' for x in values) and any(x=='ABSENT' for x in values):state='PARTIALLY_PUBLISHED'
    elif all(x=='MATCH' for x in values) and journal_stage=='FINAL' and ledger_state=='COMPLETED_VERIFIED':state='VERIFIED_PUBLISHED'
    else:state='PUBLISHED_EVIDENCE_INCOMPLETE'
    return {'state':state,'outputs':statuses,'journal_stage':journal_stage,'checkpoint':checkpoint_state,
      'ledger':ledger_state,'retry_allowed':False,'warning':'Requires quiescent publisher; cannot attest hostile concurrent writer or power loss'}
