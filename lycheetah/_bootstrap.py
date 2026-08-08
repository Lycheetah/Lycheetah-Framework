"""
Locate the framework implementation tree, wherever this package is running from.

The implementation modules live in ``12_IMPLEMENTATIONS/`` in a source checkout, and
in ``lycheetah/`` itself once installed as a wheel — ``pyproject.toml`` maps the two
implementation directories onto ``lycheetah.core`` and ``lycheetah.applications`` so
they ship without being copied. Modules inside that tree import each other by the
flat top-level names ``core.*`` and ``applications.*``, so exactly one directory
containing both sub-trees must be on ``sys.path`` before any of them is imported.

Before this module existed, ``__init__.py`` and ``cli.py`` each hardcoded the
source-checkout path::

    _IMPL = os.path.join(os.path.dirname(_HERE), "12_IMPLEMENTATIONS")

That directory does not exist in an installed wheel, so every advertised entry point
— ``lycheetah.check``, ``lycheetah.sol_assess``, and the ``lycheetah-check``,
``lycheetah-web`` and ``lycheetah-guard`` console scripts — raised
``ModuleNotFoundError`` for anyone who installed the package instead of cloning it.
Resolution now happens in one place, and says so when it fails.
"""

from __future__ import annotations

import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))

#: Candidate roots in priority order. The first that holds every required sub-tree
#: wins: ``_HERE`` covers the installed wheel, the sibling ``12_IMPLEMENTATIONS``
#: covers a source checkout.
_CANDIDATE_ROOTS: tuple[str, ...] = (
    _HERE,
    os.path.join(os.path.dirname(_HERE), "12_IMPLEMENTATIONS"),
)

#: Sub-trees the flat ``core.*`` / ``applications.*`` imports resolve against.
_REQUIRED_SUBTREES: tuple[str, ...] = ("core", "applications")


def implementation_root() -> str | None:
    """Return the directory holding every required sub-tree, or ``None`` if absent."""
    for root in _CANDIDATE_ROOTS:
        if all(os.path.isdir(os.path.join(root, sub)) for sub in _REQUIRED_SUBTREES):
            return root
    return None


def ensure_implementation_on_path() -> str:
    """
    Put the implementation root on ``sys.path`` and return it.

    Raises ``ImportError`` naming every candidate when none holds the implementation.
    A missing implementation tree is a broken install, and it should fail where the
    cause is legible rather than surface three frames later as a bare
    ``ModuleNotFoundError: No module named 'core'``.
    """
    root = implementation_root()
    if root is None:
        raise ImportError(
            "Lycheetah implementation tree not found. Looked for a directory "
            f"containing {' and '.join(repr(s) for s in _REQUIRED_SUBTREES)} in: "
            + ", ".join(repr(c) for c in _CANDIDATE_ROOTS)
            + ". This normally means the distribution was built without its "
            "implementation packages — reinstall from a complete source tree."
        )
    if root not in sys.path:
        sys.path.insert(0, root)
    return root
