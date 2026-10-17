#!/usr/bin/env python3
"""Non-invasive rootless namespace probe; does NOT run actual copy workload."""
import json
import os
import shutil
import subprocess
import sys

SCRIPT='''import json,os
print(json.dumps({'euid_inside_user_namespace':os.geteuid(),
  'netns_inode':os.stat('/proc/self/ns/net').st_ino,
  'mntns_inode':os.stat('/proc/self/ns/mnt').st_ino,
  'userns_inode':os.stat('/proc/self/ns/user').st_ino,
  'uid_map':open('/proc/self/uid_map').read().strip()}))'''

def run():
    host={'netns_inode':os.stat('/proc/self/ns/net').st_ino,
          'mntns_inode':os.stat('/proc/self/ns/mnt').st_ino,
          'userns_inode':os.stat('/proc/self/ns/user').st_ino}
    out={'host_namespaces':host,'target_host_uid':65534,'probe_type':'unshare -Urnm with preexec host UID drop, no copy operation'}
    if not shutil.which('unshare') or os.geteuid()!=0:
        out['result']='NOT_ATTEMPTED_MISSING_PREREQUISITES';return out
    def drop():
        os.setgroups([]);os.setgid(65534);os.setuid(65534)
    try:
        p=subprocess.run(['unshare','-Urnm',sys.executable,'-c',SCRIPT],
              preexec_fn=drop,capture_output=True,text=True,timeout=8)
        out['exit_code']=p.returncode
        if p.returncode==0:
            child=json.loads(p.stdout)
            out['isolated_process_report']=child
            out['verified_independent_namespaces']=all(child[k]!=host[k] for k in host)
            out['result']='ROOTLESS_NAMESPACE_CREATION_OBSERVED' if out['verified_independent_namespaces'] else 'NOT_DISTINCT'
        else:
            out['stderr']=p.stderr[:300];out['result']='NOT_AVAILABLE'
    except (OSError,subprocess.TimeoutExpired,ValueError) as exc:
        out['result']='FAILED_'+type(exc).__name__
    out['limitation']='This is an isolated namespace creation probe, NOT a mature sandbox or proof of isolated file/network operation.'
    return out
if __name__=='__main__':print(json.dumps(run(),indent=2))
