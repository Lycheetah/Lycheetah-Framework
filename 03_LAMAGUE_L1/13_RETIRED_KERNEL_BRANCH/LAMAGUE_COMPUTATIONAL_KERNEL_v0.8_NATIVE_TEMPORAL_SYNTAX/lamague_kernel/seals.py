from .registry import SEALS

def expand_seal(name):
    if name not in SEALS: raise KeyError(f"Unknown LAMAGUE seal {name!r}")
    return SEALS[name]

def list_seals(): return dict(SEALS)
