from __future__ import annotations
import argparse,json,sys
from pathlib import Path
from .api import run_file
from .compiler import compile_program
from .continuity import classify
from .errors import CompileFailure,LamagueError
from .parser import parse_file
from .seals import list_seals

def main(argv=None):
    parser=argparse.ArgumentParser(prog="lamague"); sub=parser.add_subparsers(dest="command",required=True)
    p=sub.add_parser("compile"); p.add_argument("source")
    p=sub.add_parser("run"); p.add_argument("source"); p.add_argument("-o","--output")
    p=sub.add_parser("continuity"); p.add_argument("parent"); p.add_argument("child")
    sub.add_parser("seals")
    args=parser.parse_args(argv)
    try:
        if args.command=="compile":
            ir,ds=compile_program(parse_file(args.source)); print(json.dumps({"ir":ir.to_dict(),"diagnostics":[d.to_dict() for d in ds]},indent=2)); return 0
        if args.command=="run":
            text=json.dumps(run_file(args.source).to_dict(),indent=2)
            if args.output: Path(args.output).write_text(text+"\n",encoding="utf-8")
            else: print(text)
            return 0
        if args.command=="continuity":
            parent=json.loads(Path(args.parent).read_text()); child=json.loads(Path(args.child).read_text()); print(json.dumps(classify(parent,child).to_dict(),indent=2)); return 0
        if args.command=="seals": print(json.dumps({k:list(v) for k,v in list_seals().items()},indent=2)); return 0
    except CompileFailure as exc:
        print(json.dumps({"outcome":"COMPILE_REJECTED","diagnostics":[d.to_dict() for d in exc.diagnostics]},indent=2),file=sys.stderr); return 2
    except LamagueError as exc:
        print(json.dumps({"outcome":"RUNTIME_HALTED","message":str(exc)},indent=2),file=sys.stderr); return 3
    return 1
