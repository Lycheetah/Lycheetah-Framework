"""
Core framework implementations — TRI-AXIAL metrics, CASCADE, Seven Invariants,
Sol self-protocol, Psi-Consensus, HARMONIA, TRIAD, grey mode.

This file exists so the directory ships as ``lycheetah.core`` in a built
distribution. It deliberately imports nothing: modules here are also imported by
their flat names (``from cascade_engine import CascadeEngine``) when this directory
is placed directly on ``sys.path``, and eager re-exports would make an unrelated
missing dependency break every one of them at once.
"""
