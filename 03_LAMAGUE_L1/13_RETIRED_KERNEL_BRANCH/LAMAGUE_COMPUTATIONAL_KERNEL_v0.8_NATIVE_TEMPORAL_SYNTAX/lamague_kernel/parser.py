from __future__ import annotations
import re, shlex
from pathlib import Path
from .errors import ParseFailure
from .model import AuthoritySpec, DissentSpec, EffectSpec, NamedText, ProgramSpec, ResolutionSpec, UnknownSpec, ValueFlowSpec

_EFFECT_RE = re.compile(r"^([A-Za-z][A-Za-z0-9_]*)(?:<([^>]*)>)?$")

def _bool(text):
    if text.lower() in {"true","yes","1"}: return True
    if text.lower() in {"false","no","0"}: return False
    raise ParseFailure(f"Expected boolean, received {text!r}")

def _kv(tokens):
    out = {}
    for token in tokens:
        if "=" in token:
            k,v = token.split("=",1); out[k]=v
    return out

def _effect(token):
    m = _EFFECT_RE.fullmatch(token)
    if not m: raise ParseFailure(f"Invalid effect syntax: {token}")
    args = tuple(x.strip() for x in (m.group(2) or "").split(",") if x.strip())
    return EffectSpec(m.group(1), args)

def _path(text):
    tokens = tuple(x.strip() for x in text.replace("→","->").split("->") if x.strip())
    if not tokens: raise ParseFailure("Path is empty")
    return tokens

def parse_source(source):
    data = {"name":"", "version":"0.5", "identity":"", "purpose":"", "claim":"", "path_tokens":(), "risk":"low", "irreversible":False, "decoder_confidence":1.0, "horizon":"", "step_limit":128, "requested_compression":False, "yield_text":""}
    evidence=[]; unknowns=[]; invariants=[]; authorities=[]; participants=[]; affected=[]; boundaries=[]; dissent=[]; flows=[]; recoveries=[]; effects=[]; resolutions=[]; gates=[]
    for lineno, raw in enumerate(source.splitlines(),1):
        s=raw.strip()
        if not s or s.startswith("#"): continue
        if s.startswith("path "):
            data["path_tokens"]=_path(s[5:].strip()); continue
        try: tokens=shlex.split(s, comments=True, posix=True)
        except ValueError as exc: raise ParseFailure(f"Line {lineno}: {exc}") from exc
        if not tokens: continue
        key=tokens[0].lower(); args=tokens[1:]
        try:
            if key=="program": data["name"]=args[0]
            elif key=="version": data["version"]=args[0]
            elif key=="identity": data["identity"]=args[0]
            elif key=="purpose": data["purpose"]=args[0]
            elif key=="claim": data["claim"]=args[0]
            elif key=="risk": data["risk"]=args[0].lower()
            elif key=="irreversible": data["irreversible"]=_bool(args[0])
            elif key=="confidence": data["decoder_confidence"]=float(args[0])
            elif key=="evidence": evidence.append(NamedText(args[0],args[1]))
            elif key=="unknown":
                kv=_kv(args[1:]); unknowns.append(UnknownSpec(args[0], "unprotected" not in args[1:], kv.get("required_for","")))
            elif key=="invariant": invariants.append(NamedText(args[0],args[1]))
            elif key=="authority":
                kv=_kv(args[1:]); desc=args[-1] if args and "=" not in args[-1] else ""; authorities.append(AuthoritySpec(args[0],kv.get("scope",""),desc))
            elif key=="participant": participants.append(args[0])
            elif key=="affected": affected.append(args[0])
            elif key=="boundary": boundaries.append(NamedText(args[0],args[1]))
            elif key=="dissent": dissent.append(DissentSpec(args[0],args[1]))
            elif key=="valueflow":
                kv=_kv(args[2:]); desc=args[-1] if "=" not in args[-1] else ""; flows.append(ValueFlowSpec(args[0],args[1],desc or kv.get("kind",""),kv.get("consent","")))
            elif key=="recovery": recoveries.append(NamedText(args[0],args[1]))
            elif key=="effect": effects.append(_effect(args[0]))
            elif key=="resolve":
                kv=_kv(args[1:]); resolutions.append(ResolutionSpec(args[0],kv.get("with","")))
            elif key=="gate": gates.append(args[0])
            elif key=="horizon": data["horizon"]=args[0]
            elif key=="limit":
                kv=_kv(args); data["step_limit"]=int(kv.get("max_steps", args[0] if args else "128"))
            elif key=="compress": data["requested_compression"]=args[0].lower()=="requested"
            elif key=="yield": data["yield_text"]=args[0]
            else: raise ParseFailure(f"Unknown declaration {tokens[0]!r}")
        except (IndexError, ValueError) as exc:
            raise ParseFailure(f"Line {lineno}: invalid {key} declaration: {s}") from exc
    if not data["name"]: raise ParseFailure("Program name is required")
    if not data["path_tokens"]: raise ParseFailure("Program path is required")
    data["identity"] = data["identity"] or data["name"]
    return ProgramSpec(evidence=tuple(evidence), unknowns=tuple(unknowns), invariants=tuple(invariants), authorities=tuple(authorities), participants=tuple(participants), affected_parties=tuple(affected), boundaries=tuple(boundaries), dissent=tuple(dissent), value_flows=tuple(flows), recoveries=tuple(recoveries), effects=tuple(effects), resolutions=tuple(resolutions), gates=tuple(gates), **data)

def parse_file(path): return parse_source(Path(path).read_text(encoding="utf-8"))
