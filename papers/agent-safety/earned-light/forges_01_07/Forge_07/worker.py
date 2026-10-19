"""Run as a child process. Crash cuts exit using os._exit(73)."""
import argparse,json
from controller import dispatch,recover,report,revoke
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('action',choices=['dispatch','revoke','recover','report']);p.add_argument('--db',required=True);p.add_argument('--url',required=True)
    p.add_argument('--cut',default='');p.add_argument('--unsafe-nonidempotent',action='store_true');p.add_argument('--no-query',action='store_true')
    a=p.parse_args()
    if a.action=='dispatch':out=dispatch(a.db,a.url,a.cut,dedup=not a.unsafe_nonidempotent)
    elif a.action=='revoke':revoke(a.db);out='revoked'
    elif a.action=='recover':out=recover(a.db,a.url,a.cut,provider_query=not a.no_query)
    else:out=report(a.db,a.url,provider_query=not a.no_query)
    print(json.dumps(out,sort_keys=True))
