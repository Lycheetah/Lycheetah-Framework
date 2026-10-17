#!/usr/bin/env python3
"""Read-only environment snapshot; userns attempts can fail, recorded as such."""
import json
import os
import platform
import shutil
import subprocess
from cycle12 import prerequisites

def run():
    d={'uname':platform.uname()._asdict(), 'requirements':prerequisites(),
       'tools':{n:shutil.which(n) for n in ('opa','bwrap','unshare','docker','podman','firejail')},
       'process_credentials':{'uid':os.geteuid(),'gid':os.getegid()}}
    if shutil.which('unshare'):
        p=subprocess.run(['unshare','-Ur','true'],capture_output=True,text=True,timeout=5)
        d['user_namespace_probe']={'exit_code':p.returncode,'stderr':p.stderr.strip()[:300]}
    else:d['user_namespace_probe']='unshare unavailable'
    d['note']='This is one host environment, not evidence for other systems.'
    return d
if __name__=='__main__':print(json.dumps(run(),indent=2))
