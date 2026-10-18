"""Opt-in, pinned execution of an external canonical CASCADE checkout.

The gateway package NEVER vendors the upstream engine or downloads code on import.
A caller supplies its local checkout; module execution is explicitly opt-in.
The pinned blob SHA was read from the linked GitHub repository on 2026-10-18.
SHA verification is provenance/identity, NOT a sandbox or safety proof.
"""
from __future__ import annotations
from dataclasses import dataclass
import hashlib
import importlib.util
from pathlib import Path
import sys

CANONICAL_PATH = Path('12_IMPLEMENTATIONS/core/cascade_engine.py')
PINNED_GIT_BLOB_SHA1 = 'bf90a47ab17da11c0266d078fc4d74a5d95c9235'
CANONICAL_URL = 'https://github.com/Lycheetah/Lycheetah-Framework/blob/master/12_IMPLEMENTATIONS/core/cascade_engine.py'


def git_blob_sha(content: bytes) -> str:
    return hashlib.sha1(b'blob ' + str(len(content)).encode('ascii') + b'\0' + content).hexdigest()


@dataclass(frozen=True)
class CanonicalClasses:
    engine_factory: type
    block_factory: type
    blob_sha: str
    path: str


def load_canonical_classes(root: str | Path, *, expected_blob_sha: str = PINNED_GIT_BLOB_SHA1) -> CanonicalClasses:
    """Verify SHA first, then execute an *explicitly trusted* local Python file.

    Use only with a checkout supplied and trusted by the operator. A Git blob SHA
    authenticates file bytes against a chosen reference, not their benign intent.
    """
    if (not isinstance(expected_blob_sha, str) or len(expected_blob_sha) != 40
            or any(c not in '0123456789abcdef' for c in expected_blob_sha)):
        raise ValueError('expected SHA must be exact lowercase Git blob SHA-1')
    path = Path(root).expanduser().resolve() / CANONICAL_PATH
    if not path.is_file():
        raise FileNotFoundError(f'canonical CASCADE file missing: {path}')
    actual_sha = git_blob_sha(path.read_bytes())
    if actual_sha != expected_blob_sha:
        raise ValueError('canonical CASCADE file does not match pinned blob SHA')
    name = '_lycheetah_cycle7_pinned_cascade'
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ImportError('cannot construct canonical engine loader')
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    try:
        spec.loader.exec_module(mod)
        engine, block = mod.CascadeEngine, mod.KnowledgeBlock
    except BaseException:
        sys.modules.pop(name, None)
        raise
    return CanonicalClasses(engine, block, actual_sha, str(path))
