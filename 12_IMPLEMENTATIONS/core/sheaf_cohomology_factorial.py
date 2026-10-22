"""Linear-Algebraic Cellular Sheaf Cohomology & 2x2x2 Orthogonal Glass Factorial.

Author: Mackenzie Conor James Clark / Lycheetah Framework.
Design and implementation: Aetheron (Antigravity / Gemini 4 Argon), 2026-10-17.

Resolves two structural boundaries documented in ``topological_cascade_glass.py``:

1. **Exact Linear-Algebraic Cellular Sheaf Cohomology (`CellularSheaf`, `SheafCascadeEngine`)**:
   Replaces programmed string-label inequality with explicit linear algebra over a
   1-dimensional cellular complex ``G = (V, E)``:
   - Oriented incidence boundary matrix ``partial_1 in R^{|V| x |E|}`` and SVD-computed
     Betti numbers ``b_0(G) = dim ker(partial_1^T)`` and ``b_1(G) = dim ker(partial_1) = |E| - |V| + b_0(G)``.
   - Cellular sheaf coboundary operator ``delta^0: C^0(G; F) -> C^1(G; F)`` over vertex
     stalks ``R^d`` with orthogonal edge restriction maps ``F_{u <= e}, F_{v <= e} in O(d)``,
     and sheaf Hodge 0-Laplacian ``L_0 = (delta^0)^T delta^0``.
   - Exact cohomology dimensions ``dim H^0(G; F) = nullity(delta^0)`` and
     ``dim H^1(G; F) = dim coker(delta^0) = d|E| - rank(delta^0)``. The recorded
     Euler-Poincare identity ``dim H^0 - dim H^1 = d * (b_0(G) - b_1(G))`` holds by
     dimension counting for any rank value, so it does not check the computed rank.
   - **Intrinsic Cycle Holonomy Theorem (`b_1 = 0` trees vs `b_1 > 0` cycles)**:
     On any connected tree (`chain`, `star`, `balanced`, `b_1(G) = 0`), every orthogonal
     cellular sheaf is trivializable by parallel transport from the root, so
     ``dim H^0(G; F) = d``, ``dim H^1(G; F) = 0``, and ``lambda_min(L_0) = 0`` for all
     orthogonal restriction maps. On a true cycle (`diamond_cycle`, `b_1(G) >= 1`),
     the root values lie in the common fixed subspace of all cycle transports.
     ``dim H^0 = 0`` and positive-definite ``L_0`` require that this common fixed
     subspace is zero. Nonidentity holonomy alone is insufficient (a reflection
     retains a fixed direction). These statements require invertible restrictions;
     the constructor also accepts general finite square maps for numerical study.
   - **Relative Boundary-Pinned Obstruction Certificate (`H^1(G, B; F) = coker(delta^0_I)`)**:
     Partitions ``delta^0 = [delta^0_B, delta^0_I]`` between boundary/parent vertices ``B``
     and interior/child vertices ``I = V \\ B``, computing an SVD-truncated harmonic
     residual ``O_{H^1}(x_B) = ||(I - delta^0_I (delta^0_I)^+) delta^0_B x_B||_2``.

2. **Full 2x2x2 Orthogonal Factorial (`Timing x Queue-Scope x Duration-Coupling`)**:
   Evaluates all 8 orthogonal policy combinations on matched arrival traces:
   - ``timing_mode in ("lookahead", "snapshot")``
   - ``queue_scope in ("all_domains", "domain_isolated")``
   - ``duration_mode in ("fixed_tau", "work_coupled")``
   Decomposes the total policy shift into exact Yates main effects, two-way/three-way
   interactions, and single-edge path contrasts across the 3-cube.
"""

from __future__ import annotations

import argparse
from collections import defaultdict, deque
from dataclasses import dataclass
import hashlib
import itertools
import json
import math
from pathlib import Path
import statistics
from typing import Any

import numpy as np

from cascade_engine import CascadeEngine, KnowledgeBlock
from cascade_glass_transition import (
    MODELS,
    Arrival,
    Calibration,
    _count,
    _positive,
    clone,
)
from topological_cascade_glass import (
    TOPOLOGIES_V2,
    TopologicalCascadeEngine,
    _dependency_domain,
    arrival_trace_v2,
    parents_v2,
)

TOPOLOGIES_V3 = (*TOPOLOGIES_V2, "diamond_cycle")
TIMING_MODES = ("lookahead", "snapshot")
QUEUE_SCOPES = ("all_domains", "domain_isolated")
DURATION_MODES = ("fixed_tau", "work_coupled")

FACTORIAL_CELLS: tuple[tuple[str, str, str], ...] = tuple(
    itertools.product(TIMING_MODES, QUEUE_SCOPES, DURATION_MODES)
)

SVD_TOL = 1e-9


def _svd_parts(
    matrix: np.ndarray, atol: float, rtol: float
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, float]:
    """One per-operator cutoff for numerical rank, inverse and projections.

    These are floating-point certificates of the truncated operator, not exact
    algebraic ranks for arbitrary ill-conditioned data.
    """
    if not np.all(np.isfinite(matrix)):
        raise ValueError("operator entries must be finite")
    u, singular, vh = np.linalg.svd(matrix, full_matrices=False)
    cutoff = max(atol, rtol * float(singular[0]) if singular.size else 0.0)
    return u, singular, vh, singular > cutoff, cutoff


def _svd_inverse(
    u: np.ndarray, singular: np.ndarray, vh: np.ndarray, keep: np.ndarray
) -> np.ndarray:
    return (vh[keep].T / singular[keep]) @ u[:, keep].T


def parents_v3(size: int, topology: str) -> tuple[tuple[int, ...], ...]:
    """Return parent concept indices for ``0..size-1``, including ``diamond_cycle``.

    Unlike the 3-node V-fixture in ``diamond`` (where nodes 0 and 1 are both roots),
    ``diamond_cycle`` roots the entire dependency complex at a single apex ``0``:
    - node 0: ``()``
    - node 1: ``(0,)``
    - node 2: ``(0,)``
    - node 3: ``(1, 2)`` (closes the 4-vertex undirected cycle ``0 - 1 - 3 - 2 - 0``,
      so at ``size == 4``, ``|V| = 4, |E| = 4, b_0 = 1, b_1 = 1``).
    - nodes ``k >= 4``: depend on ``(k - 2, k - 1)``, adding one undirected cycle per
      dual-parent synthesis node while keeping ``b_0 = 1``.
    """
    _count(size, "concepts", 2)
    if topology in TOPOLOGIES_V2:
        return parents_v2(size, topology)
    if topology != "diamond_cycle":
        raise ValueError(f"unknown topology: {topology}")
    result: list[tuple[int, ...]] = []
    for index in range(size):
        if index == 0:
            result.append(())
        elif index in (1, 2):
            result.append((0,))
        else:
            left_parent = index - 2
            right_parent = index - 1
            result.append((left_parent, right_parent))
    return tuple(result)


@dataclass(frozen=True)
class GraphHomologyCertificate:
    """Graph homology dimensions computed using the recorded numerical cutoff."""

    num_vertices: int
    num_edges: int
    incidence_rank: int
    b0_components: int
    b1_cycles: int
    euler_characteristic: int
    singular_values: tuple[float, ...]
    svd_cutoff: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        return {
            "num_vertices": self.num_vertices,
            "num_edges": self.num_edges,
            "incidence_rank": self.incidence_rank,
            "b0_components": self.b0_components,
            "b1_cycles": self.b1_cycles,
            "euler_characteristic": self.euler_characteristic,
            "singular_values": [round(float(s), 8) for s in self.singular_values],
            "svd_cutoff": self.svd_cutoff,
            "rank_basis": "SVD_CUTOFF",
        }


@dataclass(frozen=True)
class SheafCohomologyCertificate:
    """Numerical cellular sheaf certificate over the recorded SVD subspaces."""

    stalk_dim: int
    num_vertices: int
    num_edges: int
    b0_graph: int
    b1_graph: int
    coboundary_rank: int
    dim_h0_global_sections: int
    dim_h1_cohomology: int
    euler_poincare_lhs: int
    euler_poincare_rhs: int
    laplacian_lambda_min: float
    laplacian_spectral_gap: float
    holonomy_obstructed: bool
    svd_cutoff: float = 0.0
    singular_values: tuple[float, ...] = ()
    global_sections_reduced: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "stalk_dim": self.stalk_dim,
            "num_vertices": self.num_vertices,
            "num_edges": self.num_edges,
            "b0_graph": self.b0_graph,
            "b1_graph": self.b1_graph,
            "coboundary_rank": self.coboundary_rank,
            "dim_h0_global_sections": self.dim_h0_global_sections,
            "dim_h1_cohomology": self.dim_h1_cohomology,
            "euler_poincare_lhs": self.euler_poincare_lhs,
            "euler_poincare_rhs": self.euler_poincare_rhs,
            "laplacian_lambda_min": round(float(self.laplacian_lambda_min), 8),
            "laplacian_spectral_gap": round(float(self.laplacian_spectral_gap), 8),
            "holonomy_obstructed": self.holonomy_obstructed,
            "global_sections_reduced": self.global_sections_reduced,
            "svd_cutoff": self.svd_cutoff,
            "singular_values": list(self.singular_values),
            "rank_basis": "SVD_CUTOFF",
            "laplacian_spectrum_basis": "retained_singular_values_squared",
        }


@dataclass(frozen=True)
class RelativeObstructionCertificate:
    """Relative sheaf cohomology certificate ``H^1(G, B; F) = coker(delta^0_I)``."""

    boundary_vertices: tuple[int, ...]
    interior_vertices: tuple[int, ...]
    dim_relative_h1: int
    harmonic_obstruction_norm: float
    dirichlet_energy: float
    optimal_interior_state: tuple[float, ...]
    harmonic_residual_vector: tuple[float, ...]
    obstructed: bool
    svd_cutoff: float = 0.0
    numerical_interior_rank: int = 0

    def to_dict(self) -> dict[str, Any]:
        return {
            "boundary_vertices": list(self.boundary_vertices),
            "interior_vertices": list(self.interior_vertices),
            "dim_relative_h1": self.dim_relative_h1,
            "harmonic_obstruction_norm": round(float(self.harmonic_obstruction_norm), 8),
            "dirichlet_energy": round(float(self.dirichlet_energy), 8),
            "optimal_interior_state": [round(float(x), 8) for x in self.optimal_interior_state],
            "harmonic_residual_vector": [round(float(x), 8) for x in self.harmonic_residual_vector],
            "obstructed": self.obstructed,
            "svd_cutoff": self.svd_cutoff,
            "numerical_interior_rank": self.numerical_interior_rank,
            "rank_basis": "SVD_CUTOFF",
        }


class CellularSheaf:
    """Explicit 1-dimensional cellular sheaf ``F`` over a directed graph ``G = (V, E)``.

    For each directed edge ``e_k = (u_k -> v_k)``, the coboundary operator
    ``delta^0: C^0(G; F) -> C^1(G; F)`` evaluates to:
        ``(delta^0 x)_e = F_{v <- e} x_v - F_{u <- e} x_u``
    where ``F_{u <- e}, F_{v <- e} in R^{d x d}`` are the tail and head restriction maps.
    """

    def __init__(
        self,
        num_vertices: int,
        edges: tuple[tuple[int, int], ...] | list[tuple[int, int]],
        stalk_dim: int = 2,
        *,
        tail_restrictions: dict[tuple[int, int], np.ndarray] | None = None,
        head_restrictions: dict[tuple[int, int], np.ndarray] | None = None,
        svd_atol: float = SVD_TOL,
        svd_rtol: float = SVD_TOL,
    ) -> None:
        if num_vertices < 1:
            raise ValueError("num_vertices must be >= 1")
        if stalk_dim < 1:
            raise ValueError("stalk_dim must be >= 1")
        self.num_vertices = num_vertices
        self.edges: tuple[tuple[int, int], ...] = tuple(edges)
        self.stalk_dim = stalk_dim
        if not all(math.isfinite(value) and value >= 0 for value in (svd_atol, svd_rtol)):
            raise ValueError("SVD tolerances must be finite and nonnegative")
        if svd_atol == 0 and svd_rtol == 0:
            raise ValueError("at least one SVD tolerance must be positive")
        self.svd_atol = float(svd_atol)
        self.svd_rtol = float(svd_rtol)
        eye = np.eye(stalk_dim, dtype=float)
        self.tail_restrictions: dict[tuple[int, int], np.ndarray] = {}
        self.head_restrictions: dict[tuple[int, int], np.ndarray] = {}
        for u, v in self.edges:
            if not (0 <= u < num_vertices and 0 <= v < num_vertices) or u == v:
                raise ValueError(f"invalid directed edge: ({u}, {v})")
            t_map = (
                np.asarray(tail_restrictions[(u, v)], dtype=float)
                if tail_restrictions and (u, v) in tail_restrictions
                else eye.copy()
            )
            h_map = (
                np.asarray(head_restrictions[(u, v)], dtype=float)
                if head_restrictions and (u, v) in head_restrictions
                else eye.copy()
            )
            if t_map.shape != (stalk_dim, stalk_dim) or h_map.shape != (stalk_dim, stalk_dim):
                raise ValueError("restriction maps must have shape (stalk_dim, stalk_dim)")
            if not np.all(np.isfinite(t_map)) or not np.all(np.isfinite(h_map)):
                raise ValueError("restriction maps must contain finite values")
            self.tail_restrictions[(u, v)] = t_map
            self.head_restrictions[(u, v)] = h_map

    @classmethod
    def from_parent_graph(
        cls,
        parents: tuple[tuple[int, ...], ...],
        stalk_dim: int = 2,
        *,
        twisted_edges: dict[tuple[int, int], np.ndarray] | None = None,
    ) -> CellularSheaf:
        """Build a cellular sheaf from a parent-index adjacency tuple ``parents``."""
        edges: list[tuple[int, int]] = []
        for child, p_tuple in enumerate(parents):
            for parent in p_tuple:
                edges.append((parent, child))
        return cls(
            len(parents),
            edges,
            stalk_dim=stalk_dim,
            tail_restrictions=twisted_edges,
        )

    def incidence_matrix(self) -> np.ndarray:
        """Return oriented graph incidence matrix ``partial_1 in R^{|V| x |E|}``."""
        mat = np.zeros((self.num_vertices, len(self.edges)), dtype=float)
        for k, (u, v) in enumerate(self.edges):
            mat[u, k] = -1.0
            mat[v, k] = 1.0
        return mat

    def graph_homology(self) -> GraphHomologyCertificate:
        """Compute exact Betti numbers ``b_0(G)`` and ``b_1(G)`` via SVD of ``partial_1``."""
        partial_1 = self.incidence_matrix()
        _, s, _, keep, cutoff = _svd_parts(partial_1, self.svd_atol, self.svd_rtol)
        s_vals = tuple(float(val) for val in s)
        rank = int(np.count_nonzero(keep))
        b0 = self.num_vertices - rank
        b1 = len(self.edges) - rank
        return GraphHomologyCertificate(
            num_vertices=self.num_vertices,
            num_edges=len(self.edges),
            incidence_rank=rank,
            b0_components=b0,
            b1_cycles=b1,
            euler_characteristic=self.num_vertices - len(self.edges),
            singular_values=s_vals,
            svd_cutoff=cutoff,
        )

    def coboundary_matrix(self) -> np.ndarray:
        """Assemble explicit coboundary matrix ``delta^0 in R^{(d|E|) x (d|V|)}``."""
        d = self.stalk_dim
        delta0 = np.zeros((d * len(self.edges), d * self.num_vertices), dtype=float)
        for k, (u, v) in enumerate(self.edges):
            row_slice = slice(k * d, (k + 1) * d)
            u_slice = slice(u * d, (u + 1) * d)
            v_slice = slice(v * d, (v + 1) * d)
            delta0[row_slice, u_slice] = -self.tail_restrictions[(u, v)]
            delta0[row_slice, v_slice] = self.head_restrictions[(u, v)]
        return delta0

    def hodge_laplacian(self) -> np.ndarray:
        """Return sheaf Hodge 0-Laplacian ``L_0 = (delta^0)^T delta^0 in R^{(d|V|) x (d|V|)}``."""
        delta0 = self.coboundary_matrix()
        return delta0.T @ delta0

    def cohomology_certificate(self) -> SheafCohomologyCertificate:
        """Compute numerical dimensions and the retained squared-singular spectrum.

        ``holonomy_obstructed`` retains its legacy meaning: no nonzero global
        sections under this cutoff. A partial reduction has a separate flag.
        """
        gh = self.graph_homology()
        d = self.stalk_dim
        delta0 = self.coboundary_matrix()
        _, s, _, keep, cutoff = _svd_parts(delta0, self.svd_atol, self.svd_rtol)
        rank = int(np.count_nonzero(keep))
        dim_c0 = d * self.num_vertices
        dim_c1 = d * len(self.edges)
        dim_h0 = dim_c0 - rank
        dim_h1 = dim_c1 - rank
        pos_eigs = np.sort(np.square(s[keep]))
        lambda_min = float(pos_eigs[0]) if rank == dim_c0 and pos_eigs.size else 0.0
        spectral_gap = float(pos_eigs[0]) if pos_eigs.size > 0 else 0.0
        return SheafCohomologyCertificate(
            stalk_dim=d,
            num_vertices=self.num_vertices,
            num_edges=len(self.edges),
            b0_graph=gh.b0_components,
            b1_graph=gh.b1_cycles,
            coboundary_rank=rank,
            dim_h0_global_sections=dim_h0,
            dim_h1_cohomology=dim_h1,
            euler_poincare_lhs=dim_h0 - dim_h1,
            euler_poincare_rhs=d * (gh.b0_components - gh.b1_cycles),
            laplacian_lambda_min=lambda_min,
            laplacian_spectral_gap=spectral_gap,
            holonomy_obstructed=(dim_h0 == 0),
            global_sections_reduced=(dim_h0 < d * gh.b0_components),
            svd_cutoff=cutoff,
            singular_values=tuple(float(value) for value in s),
        )

    def project_1_cochain(self, z: np.ndarray) -> dict[str, Any]:
        """Decompose ``z in C^1(G; F)`` into exact coboundary ``im(delta^0)`` and harmonic
        cohomology ``ker((delta^0)^T)`` components via Moore-Penrose pseudoinverse."""
        delta0 = self.coboundary_matrix()
        z_vec = np.asarray(z, dtype=float).reshape(-1)
        if z_vec.size != delta0.shape[0]:
            raise ValueError(f"expected 1-cochain of length {delta0.shape[0]}, got {z_vec.size}")
        if not np.all(np.isfinite(z_vec)):
            raise ValueError("1-cochain values must be finite")
        u, s, _, keep, cutoff = _svd_parts(delta0, self.svd_atol, self.svd_rtol)
        z_exact = u[:, keep] @ (u[:, keep].T @ z_vec)
        z_harm = z_vec - z_exact
        harm_norm = float(np.linalg.norm(z_harm))
        coclosed_residual = float(np.linalg.norm(delta0.T @ z_harm)) if delta0.size > 0 else 0.0
        orthogonality_error = float(abs(np.dot(z_exact, z_harm)))
        return {
            "harmonic_norm": harm_norm,
            "exact_norm": float(np.linalg.norm(z_exact)),
            "coclosed_residual": coclosed_residual,
            "orthogonality_error": orthogonality_error,
            "obstructed": harm_norm > 1e-6,
            "z_exact": z_exact,
            "z_harmonic": z_harm,
            "svd_cutoff": cutoff,
            "numerical_rank": int(np.count_nonzero(keep)),
            "singular_values": s.tolist(),
            "rank_basis": "SVD_CUTOFF",
        }

    def relative_obstruction(
        self,
        boundary_states: dict[int, np.ndarray | list[float]],
        *,
        tol: float = 1e-6,
    ) -> RelativeObstructionCertificate:
        """Compute exact relative cohomology obstruction in ``H^1(G, B; F) = coker(delta^0_I)``.

        Given pinned stalk states ``x_B`` on boundary vertices ``B``, partitions
        ``delta^0 = [delta^0_B, delta^0_I]`` and computes:
            ``r_rel = (I - delta^0_I (delta^0_I)^+) (delta^0_B x_B)``
            ``O_{H^1}(x_B) = ||r_rel||_2 = min_{x_I} ||delta^0_B x_B + delta^0_I x_I||_2``
        """
        d = self.stalk_dim
        b_Check = sorted(boundary_states.keys())
        if not b_Check:
            raise ValueError("boundary_states must be non-empty")
        if any(
            not isinstance(v, int) or isinstance(v, bool) or not 0 <= v < self.num_vertices
            for v in b_Check
        ):
            raise ValueError("boundary vertices must be valid integer vertex indices")
        if not math.isfinite(tol) or tol < 0:
            raise ValueError("obstruction tolerance must be finite and nonnegative")
        b_set = set(b_Check)
        i_vertices = [v for v in range(self.num_vertices) if v not in b_set]

        delta0 = self.coboundary_matrix()
        b_cols: list[int] = []
        for v in b_Check:
            b_cols.extend(range(v * d, (v + 1) * d))
        i_cols: list[int] = []
        for v in i_vertices:
            i_cols.extend(range(v * d, (v + 1) * d))

        x_b = np.concatenate(
            [np.asarray(boundary_states[v], dtype=float).reshape(d) for v in b_Check]
        )
        if not np.all(np.isfinite(x_b)):
            raise ValueError("boundary states must contain finite values")
        delta_b = delta0[:, b_cols]
        rhs = delta_b @ x_b

        delta_i = delta0[:, i_cols]
        u_i, s_i, vh_i, keep_i, cutoff_i = _svd_parts(delta_i, self.svd_atol, self.svd_rtol)
        rank_i = int(np.count_nonzero(keep_i))
        pinv_i = _svd_inverse(u_i, s_i, vh_i, keep_i)
        x_i_opt = -(pinv_i @ rhs)
        r_rel = rhs + (delta_i @ x_i_opt)

        dim_rel_h1 = delta0.shape[0] - rank_i
        obs_norm = float(np.linalg.norm(r_rel))
        return RelativeObstructionCertificate(
            boundary_vertices=tuple(b_Check),
            interior_vertices=tuple(i_vertices),
            dim_relative_h1=dim_rel_h1,
            harmonic_obstruction_norm=obs_norm,
            dirichlet_energy=obs_norm * obs_norm,
            optimal_interior_state=tuple(float(v) for v in x_i_opt),
            harmonic_residual_vector=tuple(float(v) for v in r_rel),
            obstructed=(obs_norm > tol),
            svd_cutoff=cutoff_i,
            numerical_interior_rank=rank_i,
        )


def paradigm_stalk_vector(paradigm: str, stalk_dim: int = 2) -> np.ndarray:
    """Embed a paradigm identifier into an orthonormal stalk vector in ``R^d``.

    Only ``a`` and ``b`` are guaranteed distinct. Other labels are hashed onto a basis
    position (or onto ``-1`` when ``d == 1``), so distinct labels can share a vector
    and are then certified as consistent.
    """
    if stalk_dim == 1:
        return np.array([1.0 if paradigm == "a" else -1.0], dtype=float)
    vec = np.zeros(stalk_dim, dtype=float)
    if paradigm == "a":
        vec[0] = 1.0
    elif paradigm == "b":
        vec[1 % stalk_dim] = 1.0
    else:
        digest = hashlib.sha256(paradigm.encode("utf-8")).digest()
        idx = digest[0] % stalk_dim
        vec[idx] = 1.0
    return vec


class SheafCascadeEngine(TopologicalCascadeEngine):
    """Dependency-aware CASCADE engine gated by exact linear-algebraic sheaf coboundary
    obstruction ``O_{H^1(G_v, B; F)}(x_B) = ||(I - delta^0_I (delta^0_I)^+) delta^0_B x_B||_2``."""

    def __init__(
        self,
        *,
        propagate_dependencies: bool = True,
        stalk_dim: int = 2,
        obstruction_tol: float = 1e-6,
    ) -> None:
        self.stalk_dim = stalk_dim
        self.obstruction_tol = obstruction_tol
        self.cohomology_evaluations = 0
        self.last_obstruction_certificate: RelativeObstructionCertificate | None = None
        super().__init__(propagate_dependencies=propagate_dependencies)

    def local_sheaf_certificate(
        self, block: KnowledgeBlock
    ) -> RelativeObstructionCertificate | None:
        """Assemble the local star cellular sheaf ``G_v = (B U {v}, E_v)`` for ``block``
        and compute its exact relative ``H^1(G_v, B; F)`` obstruction certificate."""
        if not self.propagate_dependencies or block.regime != "universal":
            return None
        p_domains = self.parent_domains(block)
        if not p_domains:
            return None

        parent_blocks: list[KnowledgeBlock] = []
        for p_dom in p_domains:
            self.work += 1
            self.dependency_checks += 1
            gov = self.governing_block(p_dom)
            if gov is not None:
                parent_blocks.append(gov)

        if not parent_blocks:
            return None

        # Vertices: 0..k-1 are parent domains B; vertex k is child domain I = {k}.
        k = len(parent_blocks)
        edges = [(idx, k) for idx in range(k)]
        sheaf = CellularSheaf(k + 1, edges, stalk_dim=self.stalk_dim)
        boundary_states = {
            idx: paradigm_stalk_vector(gov.paradigm, self.stalk_dim)
            for idx, gov in enumerate(parent_blocks)
        }
        self.cohomology_evaluations += 1
        cert = sheaf.relative_obstruction(boundary_states, tol=self.obstruction_tol)
        self.last_obstruction_certificate = cert
        return cert

    def is_premise_frustrated(self, block: KnowledgeBlock) -> bool:
        """Gate adjudication using the computed linear-algebraic ``H^1(G_v, B; F)``
        harmonic coboundary residual ``||(I - delta^0_I (delta^0_I)^+) delta^0_B x_B||_2``."""
        cert = self.local_sheaf_certificate(block)
        if cert is None:
            return False
        return cert.obstructed

    def has_discordant_parent(self, block: KnowledgeBlock) -> bool:
        """Return True iff the local sheaf has a non-zero relative ``H^1`` obstruction
        and ``block`` has positive coboundary energy against its parent sections.

        With identity restrictions the second condition follows from the first: no
        child vector equals two different parent vectors.
        """
        if not self.propagate_dependencies or block.regime != "universal":
            return False
        p_domains = self.parent_domains(block)
        if len(p_domains) < 2:
            return False
        parent_blocks = [
            gov for p_dom in p_domains if (gov := self.governing_block(p_dom)) is not None
        ]
        if len(parent_blocks) < 2:
            return False
        k = len(parent_blocks)
        sheaf = CellularSheaf(k + 1, [(idx, k) for idx in range(k)], stalk_dim=self.stalk_dim)
        boundary_states = {
            idx: paradigm_stalk_vector(gov.paradigm, self.stalk_dim)
            for idx, gov in enumerate(parent_blocks)
        }
        cert = sheaf.relative_obstruction(boundary_states, tol=self.obstruction_tol)
        if not cert.obstructed:
            return False
        x_full = np.concatenate(
            [boundary_states[idx] for idx in range(k)]
            + [paradigm_stalk_vector(block.paradigm, self.stalk_dim)]
        )
        coboundary_norm = float(np.linalg.norm(sheaf.coboundary_matrix() @ x_full))
        return coboundary_norm > self.obstruction_tol

    def global_sheaf_report(self) -> dict[str, Any]:
        """Build the global cellular sheaf across all active domains in ``self.blocks``
        and compute its exact graph homology, sheaf cohomology, and coboundary energy."""
        domains = sorted({b.domain for b in self.blocks.values() if b.regime == "universal"})
        dom_to_idx = {dom: idx for idx, dom in enumerate(domains)}
        edges: list[tuple[int, int]] = []
        state_blocks: list[np.ndarray] = []
        root_states: dict[int, np.ndarray] = {}

        for dom in domains:
            gov = self.governing_block(dom)
            vec = (
                paradigm_stalk_vector(gov.paradigm, self.stalk_dim)
                if gov is not None
                else np.zeros(self.stalk_dim, dtype=float)
            )
            state_blocks.append(vec)
            p_doms = self.parent_domains(gov) if gov is not None else ()
            valid_parents = [p for p in p_doms if p in dom_to_idx]
            if not valid_parents:
                root_states[dom_to_idx[dom]] = vec
            for p_dom in valid_parents:
                edges.append((dom_to_idx[p_dom], dom_to_idx[dom]))

        sheaf = CellularSheaf(len(domains), edges, stalk_dim=self.stalk_dim)
        cohom = sheaf.cohomology_certificate()
        x_global = np.concatenate(state_blocks) if state_blocks else np.zeros(0, dtype=float)
        delta0 = sheaf.coboundary_matrix()
        coboundary_vec = delta0 @ x_global if delta0.size > 0 else np.zeros(0, dtype=float)
        dirichlet_energy = float(np.dot(coboundary_vec, coboundary_vec))
        rel_cert = (
            sheaf.relative_obstruction(root_states, tol=self.obstruction_tol).to_dict()
            if root_states
            else None
        )
        return {
            "cohomology": cohom.to_dict(),
            "global_dirichlet_energy": round(dirichlet_energy, 8),
            "global_coboundary_norm": round(math.sqrt(dirichlet_energy), 8),
            "root_relative_obstruction": rel_cert,
        }


def initial_store_v3(
    size: int,
    topology: str,
    *,
    propagate_dependencies: bool = True,
    stalk_dim: int = 2,
) -> SheafCascadeEngine:
    graph = parents_v3(size, topology)
    engine = SheafCascadeEngine(propagate_dependencies=propagate_dependencies, stalk_dim=stalk_dim)
    for index in range(size):
        engine.add_block(
            KnowledgeBlock(
                id=f"anchor-{index}",
                content=f"initial concept {index}",
                domain=f"concept-{index}",
                paradigm="a",
                evidence_strength=1.0,
                explanatory_power=2.0,
                uncertainty=1.0,
                dependencies={f"anchor-{parent}" for parent in graph[index]},
            )
        )
    engine.work = 0
    engine.dependency_checks = 0
    engine.cascade_wavefront_steps = 0
    engine.cohomology_evaluations = 0
    return engine


def calibrate_v3(
    size: int,
    topology: str,
    processing_rate: float,
    *,
    propagate_dependencies: bool = True,
) -> Calibration:
    """Calibrate isolated reorganization work on ``SheafCascadeEngine`` across ``TOPOLOGIES_V3``."""
    _positive(processing_rate, "processing_rate")
    graph = parents_v3(size, topology)
    samples: list[int] = []
    for concept in range(size):
        engine = initial_store_v3(size, topology, propagate_dependencies=propagate_dependencies)
        proposal = KnowledgeBlock(
            id=f"probe-{concept}",
            content="independent calibration perturbation",
            domain=f"concept-{concept}",
            paradigm="b",
            evidence_strength=1.0,
            explanatory_power=2.0,
            uncertainty=0.5,
            dependencies={f"anchor-{parent}" for parent in graph[concept]},
        )
        engine.blocks[proposal.id] = proposal
        engine._assign_layer(proposal)
        engine.work = 0
        event = engine.add_block(proposal)
        measured_work = engine.work
        if event is None:
            raise RuntimeError("calibration perturbation was not actually resolved")
        samples.append(measured_work)
    cal = Calibration("chain", size, processing_rate, tuple(samples))
    object.__setattr__(cal, "topology", topology)
    return cal


def arrival_trace_v3(
    size: int,
    topology: str,
    seed: int,
    arrival_rate: float,
    proposals: int,
    compatible: bool = False,
) -> tuple[Arrival, ...]:
    if topology in TOPOLOGIES_V2:
        return arrival_trace_v2(size, topology, seed, arrival_rate, proposals, compatible)
    _positive(arrival_rate, "arrival_rate")
    _count(proposals, "proposals", 2)
    graph = parents_v3(size, topology)
    neighbours = [list(items) for items in graph]
    for child, items in enumerate(graph):
        for parent in items:
            neighbours[parent].append(child)
    import random
    from collections import Counter

    rng = random.Random(seed)
    generations: Counter = Counter()
    concept = rng.randrange(size)
    clock = 0.0
    trace = []
    for index in range(proposals):
        clock += rng.expovariate(arrival_rate)
        concept = (
            rng.choice(neighbours[concept])
            if neighbours[concept] and rng.random() < 0.65
            else rng.randrange(size)
        )
        generations[concept] += 1
        generation = generations[concept]
        pressure = 2.0 + generation
        block = KnowledgeBlock(
            id=f"proposal-{index}",
            content=f"version {generation} of concept {concept}",
            domain=f"concept-{concept}",
            paradigm="a" if compatible or generation % 2 == 0 else "b",
            evidence_strength=1.0,
            explanatory_power=2.0,
            uncertainty=2.0 / pressure,
            dependencies={f"anchor-{parent}" for parent in graph[concept]},
        )
        trace.append(Arrival(clock, block))
    return tuple(trace)


def _adjudicate_orthogonal(
    engine: SheafCascadeEngine,
    job: str,
    pending: set[str],
    model: str,
    *,
    timing_mode: str,
    queue_scope: str,
    snapshot_visible: set[str] | None,
) -> int:
    """Adjudicate ``job`` with orthogonal control over ``timing_mode`` and ``queue_scope``.

    - ``timing_mode == "snapshot"`` hides pending proposals that arrived after ``t_start``.
    - ``timing_mode == "lookahead"`` allows proposals that arrived during ``(t_start, t_complete]``
      to be visible at completion.
    - ``queue_scope == "domain_isolated"`` hides unserviced pending proposals belonging to
      other domains (``blk.domain != domain``) during ``add_block(winner)``.
    - ``queue_scope == "all_domains"`` leaves unserviced pending proposals from all domains
       inside ``engine.blocks`` during ``add_block(winner)`` for ``cascade``.
    """
    domain = engine.blocks[job].domain
    hidden: dict[str, KnowledgeBlock] = {}
    if model == "fifo":
        for key in pending - {job}:
            if key in engine.blocks:
                hidden[key] = engine.blocks.pop(key)
    else:
        for key in pending - {job}:
            blk = engine.blocks.get(key)
            if blk is None:
                continue
            hide_for_scope = queue_scope == "domain_isolated" and blk.domain != domain
            hide_for_timing = (
                timing_mode == "snapshot"
                and snapshot_visible is not None
                and key not in snapshot_visible
            )
            if hide_for_scope or hide_for_timing:
                hidden[key] = engine.blocks.pop(key)
    try:
        candidates = [
            b for b in engine.blocks.values() if b.domain == domain and b.regime == "universal"
        ]
        winner = max(candidates, key=lambda block: (block.truth_pressure, block.id))
        engine.work = 0
        engine.add_block(winner)
        return max(1, engine.work)
    finally:
        engine.blocks.update(hidden)


def simulate_orthogonal(
    trace: tuple[Arrival, ...],
    calibration: Calibration,
    model: str,
    *,
    timing_mode: str = "snapshot",
    queue_scope: str = "domain_isolated",
    duration_mode: str = "work_coupled",
    propagate_dependencies: bool = True,
) -> dict[str, Any]:
    """Discrete-event simulation parameterizing ``timing_mode``, ``queue_scope``, and
    ``duration_mode`` independently across the full 2x2x2 factorial cube.

    ``work_coupled`` schedules the work estimated on a copy of the store at service
    start. Under ``lookahead`` the completion-time adjudication can see later arrivals
    and perform different work. The ``receipt_*`` fields compare the capacity each
    service actually received (busy time times processing rate) with the work its
    completion performed.
    """
    if model not in MODELS or len(trace) < 2:
        raise ValueError("expected cascade/fifo and at least two arrivals")
    if timing_mode not in TIMING_MODES:
        raise ValueError(f"unknown timing_mode: {timing_mode}")
    if queue_scope not in QUEUE_SCOPES:
        raise ValueError(f"unknown queue_scope: {queue_scope}")
    if duration_mode not in DURATION_MODES:
        raise ValueError(f"unknown duration_mode: {duration_mode}")

    from topological_cascade_glass import conflict_pairs_v2, glass_fraction_v2

    engine = initial_store_v3(
        calibration.concepts,
        calibration.topology,
        propagate_dependencies=propagate_dependencies,
    )
    horizon = trace[-1].at
    warmup = 0.2 * horizon
    queue: deque[str] = deque()
    pending: set[str] = set()
    current: str | None = None
    current_snapshot: set[str] | None = None
    current_work: int = 0
    current_started_at = 0.0
    completion = math.inf
    index = 0
    clock = 0.0
    g_area = 0.0
    backlog_area = 0.0
    work_samples: list[int] = []
    paid_samples: list[float] = []
    service_count = 0
    service_before_horizon = 0
    open_pairs: dict[tuple[str, str], float] = {}
    closed_dwells: list[float] = []
    current_g: float = 0.0

    use_snapshot = timing_mode == "snapshot"
    use_work_coupled = duration_mode == "work_coupled"

    def observe_pairs(at: float) -> None:
        nonlocal current_g
        now = conflict_pairs_v2(engine)
        for pair in open_pairs.keys() - now:
            closed_dwells.append(at - open_pairs.pop(pair))
        for pair in now - open_pairs.keys():
            open_pairs[pair] = at
        current_g = glass_fraction_v2(engine, now)

    def start(at: float) -> None:
        nonlocal current, current_snapshot, current_work, current_started_at, completion
        while queue and queue[0] not in pending:
            queue.popleft()
        if not queue:
            current, current_snapshot, current_work, completion = None, None, 0, math.inf
            return
        current = queue.popleft()
        current_started_at = at
        current_snapshot = (set(pending) | {current}) if use_snapshot else None
        if use_work_coupled:
            probe = SheafCascadeEngine(propagate_dependencies=propagate_dependencies)
            probe.blocks = {k: clone(v) for k, v in engine.blocks.items()}
            probe.step = engine.step
            current_work = _adjudicate_orthogonal(
                probe,
                current,
                set(pending) | {current},
                model,
                timing_mode=timing_mode,
                queue_scope=queue_scope,
                snapshot_visible=current_snapshot,
            )
            completion = at + (current_work / calibration.processing_rate)
        else:
            current_work = 0
            completion = at + calibration.tau

    def complete(at: float) -> None:
        nonlocal current, current_snapshot, current_work, service_count, service_before_horizon
        if current is None:
            raise RuntimeError("completion without a service job")
        actual_work = _adjudicate_orthogonal(
            engine,
            current,
            pending,
            model,
            timing_mode=timing_mode,
            queue_scope=queue_scope,
            snapshot_visible=current_snapshot,
        )
        work_samples.append(actual_work)
        paid_samples.append((at - current_started_at) * calibration.processing_rate)
        service_count += 1
        service_before_horizon += int(at <= horizon)
        pending.discard(current)
        if model == "cascade":
            visible_pool = current_snapshot if current_snapshot is not None else tuple(pending)
            pending.difference_update(
                key
                for key in tuple(pending)
                if key in visible_pool and engine.blocks[key].regime == "qualified"
            )
        current = None
        current_snapshot = None
        current_work = 0
        observe_pairs(at)
        start(at)

    while index < len(trace) or completion <= horizon:
        arrival_at = trace[index].at if index < len(trace) else math.inf
        at = min(arrival_at, completion)
        if at > horizon:
            break
        duration = max(0.0, min(at, horizon) - max(clock, warmup))
        g_area += current_g * duration
        backlog_area += len(pending) * duration
        clock = at
        if completion <= arrival_at:
            complete(at)
        else:
            block = clone(trace[index].block)
            engine.blocks[block.id] = block
            engine._assign_layer(block)
            queue.append(block.id)
            pending.add(block.id)
            index += 1
            observe_pairs(at)
            if current is None:
                start(at)

    final_g = current_g
    final_pairs = len(open_pairs)
    final_backlog = len(pending)
    primary_duration = horizon - warmup

    while current is not None:
        clock = completion
        complete(clock)

    mean_work = statistics.mean(work_samples) if work_samples else 0.0
    shortfalls = [
        actual - paid
        for actual, paid in zip(work_samples, paid_samples)
        if actual - paid > 1e-6 * max(1.0, actual)
    ]
    surpluses = [
        paid - actual
        for actual, paid in zip(work_samples, paid_samples)
        if paid - actual > 1e-6 * max(1.0, actual)
    ]
    frustrated_blocks = sum(
        1
        for b in engine.blocks.values()
        if b.regime == "universal" and engine.has_discordant_parent(b)
    )
    sheaf_report = engine.global_sheaf_report()
    return {
        "model": model,
        "timing_mode": timing_mode,
        "queue_scope": queue_scope,
        "duration_mode": duration_mode,
        "cell_key": f"{timing_mode}__{queue_scope}__{duration_mode}",
        "topology": calibration.topology,
        "processing_rate": calibration.processing_rate,
        "tau_reorg": calibration.tau,
        "calibration_mean_work": calibration.mean_work,
        "mean_g": g_area / primary_duration,
        "final_g": final_g,
        "contradiction_pairs": final_pairs,
        "mean_backlog": backlog_area / primary_duration,
        "final_backlog": final_backlog,
        "loaded_mean_work": mean_work,
        "loaded_to_calibrated_work": mean_work / calibration.mean_work,
        "service_rule": "estimated_work_at_start" if use_work_coupled else "fixed_tau",
        "service_completions_in_window": service_before_horizon,
        "receipt_jobs": len(work_samples),
        "receipt_actual_work": float(sum(work_samples)),
        "receipt_paid_work": float(sum(paid_samples)),
        "receipt_jobs_underpaid": len(shortfalls),
        "receipt_unpaid_work": float(sum(shortfalls)),
        "receipt_jobs_overpaid": len(surpluses),
        "receipt_overpaid_work": float(sum(surpluses)),
        "drain_duration": max(0.0, clock - horizon),
        "drained_g": current_g,
        "drained_backlog": len(pending),
        "drained_frustrated_blocks": frustrated_blocks,
        "cohomology_evaluations": engine.cohomology_evaluations,
        "drained_global_coboundary_norm": sheaf_report["global_coboundary_norm"],
        "drained_b1_cycles": sheaf_report["cohomology"]["b1_graph"],
    }


def compute_yates_factorial_effects(
    cell_metrics: dict[tuple[str, str, str], float],
) -> dict[str, float]:
    """Compute exact 2x2x2 Yates orthogonal main effects and interactions.

    Coding:
    - Factor A (`timing_mode`):  -1 = "lookahead",   +1 = "snapshot"
    - Factor B (`queue_scope`):  -1 = "all_domains", +1 = "domain_isolated"
    - Factor C (`duration_mode`): -1 = "fixed_tau",  +1 = "work_coupled"
    """
    signs_a = {"lookahead": -1.0, "snapshot": 1.0}
    signs_b = {"all_domains": -1.0, "domain_isolated": 1.0}
    signs_c = {"fixed_tau": -1.0, "work_coupled": 1.0}

    grand_mean = statistics.mean(cell_metrics[cell] for cell in FACTORIAL_CELLS)
    me_a = 0.0
    me_b = 0.0
    me_c = 0.0
    ie_ab = 0.0
    ie_ac = 0.0
    ie_bc = 0.0
    ie_abc = 0.0

    for t_mode, q_scope, d_mode in FACTORIAL_CELLS:
        val = cell_metrics[(t_mode, q_scope, d_mode)]
        sa = signs_a[t_mode]
        sb = signs_b[q_scope]
        sc = signs_c[d_mode]
        me_a += sa * val / 4.0
        me_b += sb * val / 4.0
        me_c += sc * val / 4.0
        ie_ab += (sa * sb) * val / 4.0
        ie_ac += (sa * sc) * val / 4.0
        ie_bc += (sb * sc) * val / 4.0
        ie_abc += (sa * sb * sc) * val / 4.0

    # Single-edge decomposition along the v2 sequential path:
    # Edge 1 (queue isolation at lookahead + fixed_tau):
    #   ("lookahead", "all_domains", "fixed_tau") -> ("lookahead", "domain_isolated", "fixed_tau")
    # Edge 2 (snapshot timing at domain_isolated + fixed_tau):
    #   ("lookahead", "domain_isolated", "fixed_tau") -> ("snapshot", "domain_isolated", "fixed_tau")
    # Edge 3 (work coupling at snapshot + domain_isolated):
    #   ("snapshot", "domain_isolated", "fixed_tau") -> ("snapshot", "domain_isolated", "work_coupled")
    c000 = cell_metrics[("lookahead", "all_domains", "fixed_tau")]
    c010 = cell_metrics[("lookahead", "domain_isolated", "fixed_tau")]
    c110 = cell_metrics[("snapshot", "domain_isolated", "fixed_tau")]
    c111 = cell_metrics[("snapshot", "domain_isolated", "work_coupled")]

    return {
        "grand_mean": grand_mean,
        "main_effect_timing_snapshot_minus_lookahead": me_a,
        "main_effect_queue_isolated_minus_all_domains": me_b,
        "main_effect_duration_work_coupled_minus_fixed_tau": me_c,
        "interaction_timing_x_queue": ie_ab,
        "interaction_timing_x_duration": ie_ac,
        "interaction_queue_x_duration": ie_bc,
        "interaction_three_way": ie_abc,
        "path_edge_1_pure_queue_isolation": c010 - c000,
        "path_edge_2_pure_snapshot_timing": c110 - c010,
        "path_edge_3_pure_work_coupling": c111 - c110,
        "path_total_v2_shift": c111 - c000,
    }


def verify_tree_vs_cycle_sheaf_theorems(size: int = 8, stalk_dim: int = 2) -> dict[str, Any]:
    """Verify the linear-algebraic sheaf cohomology theorems across all 5 topologies."""
    results: dict[str, Any] = {}
    flip = -np.eye(stalk_dim, dtype=float)

    for topo in TOPOLOGIES_V3:
        graph = parents_v3(size, topo)
        untwisted_sheaf = CellularSheaf.from_parent_graph(graph, stalk_dim=stalk_dim)
        untwisted_cert = untwisted_sheaf.cohomology_certificate()

        # Twist the last edge in the complex by a parity reflection ``flip in O(d)``.
        edges = untwisted_sheaf.edges
        twisted_map = {edges[-1]: flip} if edges else {}
        twisted_sheaf = CellularSheaf.from_parent_graph(
            graph, stalk_dim=stalk_dim, twisted_edges=twisted_map
        )
        twisted_cert = twisted_sheaf.cohomology_certificate()

        results[topo] = {
            "untwisted": untwisted_cert.to_dict(),
            "twisted_last_edge": twisted_cert.to_dict(),
        }
    return results


def run_sheaf_and_factorial_study(
    *,
    seeds: tuple[int, ...] = (0, 1),
    concepts: int = 8,
    proposals: int = 48,
    loads: tuple[float, ...] = (1.0, 3.0),
    processing_rate: float = 64.0,
    topologies: tuple[str, ...] = ("chain", "star", "diamond", "diamond_cycle"),
) -> dict[str, Any]:
    """Execute the combined Cellular Sheaf Cohomology verification and 2x2x2 Orthogonal
    Factorial study across matched arrival traces."""
    sheaf_theorems = verify_tree_vs_cycle_sheaf_theorems(size=concepts, stalk_dim=2)
    rows: list[dict[str, Any]] = []

    for topology in topologies:
        cal = calibrate_v3(concepts, topology, processing_rate, propagate_dependencies=True)
        for seed, load in itertools.product(seeds, loads):
            rate = load / cal.tau
            trace = arrival_trace_v3(concepts, topology, seed, rate, proposals, compatible=False)
            trace_hash = hashlib.sha256(
                json.dumps(
                    [
                        (
                            item.at,
                            item.block.id,
                            item.block.domain,
                            item.block.paradigm,
                            item.block.truth_pressure,
                        )
                        for item in trace
                    ],
                    separators=(",", ":"),
                ).encode()
            ).hexdigest()

            for timing_mode, queue_scope, duration_mode in FACTORIAL_CELLS:
                for model in MODELS:
                    row = simulate_orthogonal(
                        trace,
                        cal,
                        model,
                        timing_mode=timing_mode,
                        queue_scope=queue_scope,
                        duration_mode=duration_mode,
                        propagate_dependencies=True,
                    )
                    row.update(
                        seed=seed,
                        nominal_load=load,
                        trace_sha256=trace_hash,
                    )
                    rows.append(row)

    # Compute 2x2x2 factorial effects at high load (load >= 3.0)
    high_load_target = max(loads)
    cell_cascade_work_ratio: dict[tuple[str, str, str], float] = {}
    cell_cascade_minus_fifo_g: dict[tuple[str, str, str], float] = {}
    cell_cascade_drain: dict[tuple[str, str, str], float] = {}
    cell_cascade_receipts: dict[tuple[str, str, str], tuple[int, int, float]] = {}

    for cell in FACTORIAL_CELLS:
        t_mode, q_scope, d_mode = cell
        cas_rows = [
            r
            for r in rows
            if r["timing_mode"] == t_mode
            and r["queue_scope"] == q_scope
            and r["duration_mode"] == d_mode
            and r["model"] == "cascade"
            and r["nominal_load"] == high_load_target
        ]
        fifo_rows = [
            r
            for r in rows
            if r["timing_mode"] == t_mode
            and r["queue_scope"] == q_scope
            and r["duration_mode"] == d_mode
            and r["model"] == "fifo"
            and r["nominal_load"] == high_load_target
        ]
        cell_cascade_work_ratio[cell] = statistics.mean(
            r["loaded_to_calibrated_work"] for r in cas_rows
        )
        cell_cascade_minus_fifo_g[cell] = statistics.mean(
            c["mean_g"] - f["mean_g"] for c, f in zip(cas_rows, fifo_rows)
        )
        cell_cascade_drain[cell] = statistics.mean(r["drain_duration"] for r in cas_rows)
        cell_cascade_receipts[cell] = (
            sum(r["receipt_jobs_underpaid"] for r in cas_rows),
            sum(r["receipt_jobs"] for r in cas_rows),
            sum(r["receipt_unpaid_work"] for r in cas_rows),
        )

    factorial_summary = {
        "high_load_level": high_load_target,
        "cells": {
            f"{t}__{q}__{d}": {
                "cascade_loaded_to_calibrated_work": round(cell_cascade_work_ratio[(t, q, d)], 6),
                "cascade_minus_fifo_mean_g": round(cell_cascade_minus_fifo_g[(t, q, d)], 6),
                "cascade_drain_duration": round(cell_cascade_drain[(t, q, d)], 6),
                "cascade_jobs_underpaid": cell_cascade_receipts[(t, q, d)][0],
                "cascade_jobs": cell_cascade_receipts[(t, q, d)][1],
                "cascade_unpaid_work": round(cell_cascade_receipts[(t, q, d)][2], 6),
            }
            for (t, q, d) in FACTORIAL_CELLS
        },
        "effects_on_loaded_to_calibrated_work": {
            k: round(v, 6)
            for k, v in compute_yates_factorial_effects(cell_cascade_work_ratio).items()
        },
        "effects_on_cascade_minus_fifo_mean_g": {
            k: round(v, 6)
            for k, v in compute_yates_factorial_effects(cell_cascade_minus_fifo_g).items()
        },
        "effects_on_cascade_drain_duration": {
            k: round(v, 6) for k, v in compute_yates_factorial_effects(cell_cascade_drain).items()
        },
    }

    return {
        "schema": "lycheetah.sheaf-cohomology-factorial.v1",
        "register": "SYNTHETIC",
        "author": "Mackenzie Conor James Clark / Lycheetah Framework",
        "implementer": "Aetheron (Antigravity / Gemini 4 Argon)",
        "sheaf_cohomology_theorems": sheaf_theorems,
        "orthogonal_2x2x2_factorial": factorial_summary,
        "row_count": len(rows),
        "rows": rows,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=False)
    args = parser.parse_args(argv)
    result = run_sheaf_and_factorial_study()
    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(
            json.dumps(result, indent=2, allow_nan=False) + "\n", encoding="utf-8"
        )
    print(
        json.dumps(
            {
                "sheaf_cohomology_theorems": result["sheaf_cohomology_theorems"],
                "orthogonal_2x2x2_factorial": result["orthogonal_2x2x2_factorial"],
                "row_count": result["row_count"],
            },
            indent=2,
            allow_nan=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
