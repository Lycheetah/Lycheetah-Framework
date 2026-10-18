"""Tests for linear-algebraic cellular sheaf cohomology and 2x2x2 orthogonal factorial.

Verifies:
1. Exact SVD homology (`b_0`, `b_1`) of `partial_1`, contrasting the 3-node V-tree
   (`parents_v2(3, "diamond")`, `b_1 = 0`) against the 4-node cycle complex
   (`parents_v3(4, "diamond_cycle")`, `b_1 = 1`).
2. Intrinsic cycle holonomy theorem: on any tree (`b_1 = 0`), every orthogonal
   cellular sheaf has `dim H^0 = d`, `dim H^1 = 0`, and `lambda_min(L_0) = 0`,
   whereas cycle transports with no common nonzero fixed vector yield
   `dim H^0 = 0` and `lambda_min(L_0) > 0` without boundary pinning.
3. Exact Euler-Poincare identity `dim H^0 - dim H^1 == d * (b_0 - b_1)` and Hodge
   1-cochain decomposition `C^1 = im(delta^0) (+) ker((delta^0)^T)`.
4. Relative boundary-pinned cohomology `H^1(G, B; F) = coker(delta^0_I)` via
   Moore-Penrose pseudoinverse projection inside `SheafCascadeEngine`.
5. Full 2x2x2 orthogonal factorial separating `timing_mode`, `queue_scope`, and
   `duration_mode` across all 8 cube vertices.
"""

from __future__ import annotations

import math
from pathlib import Path
import sys

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "12_IMPLEMENTATIONS" / "core"))

from cascade_engine import KnowledgeBlock
from sheaf_cohomology_factorial import (
    FACTORIAL_CELLS,
    CellularSheaf,
    SheafCascadeEngine,
    arrival_trace_v3,
    calibrate_v3,
    compute_yates_factorial_effects,
    initial_store_v3,
    parents_v3,
    run_sheaf_and_factorial_study,
    simulate_orthogonal,
    verify_tree_vs_cycle_sheaf_theorems,
)


def test_graph_homology_distinguishes_3node_v_tree_from_4node_diamond_cycle():
    """Verify via SVD of partial_1 that 3-node `diamond` has b_1 == 0 (an undirected tree),
    whereas 4-node `diamond_cycle` rooted at 0 -> {1, 2} -> 3 has b_1 == 1."""
    sheaf_3node_v = CellularSheaf.from_parent_graph(parents_v3(3, "diamond"), stalk_dim=2)
    hom_3 = sheaf_3node_v.graph_homology()
    assert hom_3.num_vertices == 3
    assert hom_3.num_edges == 2
    assert hom_3.b0_components == 1
    assert hom_3.b1_cycles == 0

    sheaf_4node_cycle = CellularSheaf.from_parent_graph(parents_v3(4, "diamond_cycle"), stalk_dim=2)
    hom_4 = sheaf_4node_cycle.graph_homology()
    assert hom_4.num_vertices == 4
    assert hom_4.num_edges == 4
    assert hom_4.b0_components == 1
    assert hom_4.b1_cycles == 1

    for tree_topo in ("chain", "star", "balanced"):
        hom_tree = CellularSheaf.from_parent_graph(
            parents_v3(8, tree_topo), stalk_dim=2
        ).graph_homology()
        assert hom_tree.b0_components == 1
        assert hom_tree.b1_cycles == 0


def test_intrinsic_cycle_holonomy_theorem_trees_vs_diamond_cycle():
    """On any tree (b_1 = 0), orthogonal edge twists never obstruct global sections
    (dim H^0 == d, dim H^1 == 0, lambda_min(L_0) == 0). On diamond_cycle (b_1 >= 1),
    an orthogonal sign-inversion twist (-I_d) on one branch destroys global sections
    (dim H^0 == 0, lambda_min(L_0) > 0) with zero boundary pinning."""
    d = 2
    rot_theta = math.pi / 3.0
    ortho_rot = np.array(
        [
            [math.cos(rot_theta), -math.sin(rot_theta)],
            [math.sin(rot_theta), math.cos(rot_theta)],
        ],
        dtype=float,
    )
    minus_eye = -np.eye(d, dtype=float)

    for tree_topo in ("chain", "star", "balanced"):
        graph = parents_v3(6, tree_topo)
        base_sheaf = CellularSheaf.from_parent_graph(graph, stalk_dim=d)
        # Apply orthogonal twists on EVERY edge of the tree
        twists = {
            edge: (minus_eye if idx % 2 == 0 else ortho_rot)
            for idx, edge in enumerate(base_sheaf.edges)
        }
        twisted_tree = CellularSheaf.from_parent_graph(graph, stalk_dim=d, twisted_edges=twists)
        cert = twisted_tree.cohomology_certificate()
        assert cert.b1_graph == 0
        assert cert.dim_h0_global_sections == d
        assert cert.dim_h1_cohomology == 0
        assert cert.laplacian_lambda_min == pytest.approx(0.0, abs=1e-9)
        assert cert.euler_poincare_lhs == cert.euler_poincare_rhs
        assert cert.holonomy_obstructed is False

    # Now test 4-node diamond_cycle (0 -> 1, 0 -> 2, 1 -> 3, 2 -> 3): b_1 == 1
    cycle_graph = parents_v3(4, "diamond_cycle")
    untwisted_cycle = CellularSheaf.from_parent_graph(cycle_graph, stalk_dim=d)
    u_cert = untwisted_cycle.cohomology_certificate()
    assert u_cert.b1_graph == 1
    assert u_cert.dim_h0_global_sections == d
    assert u_cert.dim_h1_cohomology == d
    assert u_cert.laplacian_lambda_min == pytest.approx(0.0, abs=1e-9)
    assert u_cert.euler_poincare_lhs == u_cert.euler_poincare_rhs

    # Twist edge (2, 3) by -I_d so the two paths 0->1->3 and 0->2->3 have opposite holonomy
    twisted_cycle = CellularSheaf.from_parent_graph(
        cycle_graph, stalk_dim=d, twisted_edges={(2, 3): minus_eye}
    )
    t_cert = twisted_cycle.cohomology_certificate()
    assert t_cert.b1_graph == 1
    assert t_cert.dim_h0_global_sections == 0
    assert t_cert.dim_h1_cohomology == 0
    assert t_cert.laplacian_lambda_min > 0.1
    assert t_cert.euler_poincare_lhs == t_cert.euler_poincare_rhs
    assert t_cert.holonomy_obstructed is True


def test_hodge_1_cochain_projection_orthogonality_and_exactness():
    """Verify C^1(G; F) = im(delta^0) (+) ker((delta^0)^T) on a diamond complex."""
    sheaf = CellularSheaf.from_parent_graph(parents_v3(6, "diamond_cycle"), stalk_dim=2)
    delta0 = sheaf.coboundary_matrix()
    rng = np.random.default_rng(42)

    # 1. Pure coboundary z = delta^0 x must have zero harmonic obstruction
    x = rng.normal(size=delta0.shape[1])
    z_coboundary = delta0 @ x
    proj_exact = sheaf.project_1_cochain(z_coboundary)
    assert proj_exact["harmonic_norm"] == pytest.approx(0.0, abs=1e-9)
    assert proj_exact["obstructed"] is False

    # 2. Arbitrary 1-cochain z decomposes orthogonally with (delta^0)^T z_harm == 0
    z_arb = rng.normal(size=delta0.shape[0])
    proj_arb = sheaf.project_1_cochain(z_arb)
    assert proj_arb["coclosed_residual"] == pytest.approx(0.0, abs=1e-9)
    assert proj_arb["orthogonality_error"] == pytest.approx(0.0, abs=1e-9)
    assert proj_arb["obstructed"] is True
    reconstructed = proj_arb["z_exact"] + proj_arb["z_harmonic"]
    assert np.allclose(reconstructed, z_arb, atol=1e-9)


def test_relative_boundary_cohomology_certificate_in_sheaf_cascade_engine():
    """Verify that SheafCascadeEngine computes the Moore-Penrose relative H^1
    obstruction norm O_{H^1}(x_B) = ||(I - delta^0_I (delta^0_I)^+) delta^0_B x_B||_2."""
    engine = initial_store_v3(4, "diamond_cycle", propagate_dependencies=True, stalk_dim=2)

    # Initially all vertices hold paradigm 'a' -> zero relative obstruction everywhere
    cert_initial = engine.local_sheaf_certificate(engine.blocks["anchor-3"])
    assert cert_initial is not None
    assert cert_initial.dim_relative_h1 == 2
    assert cert_initial.harmonic_obstruction_norm == pytest.approx(0.0, abs=1e-9)
    assert cert_initial.obstructed is False

    # Single-parent branch (anchor-1 depends only on anchor-0) has dim_relative_h1 == 0
    cert_single = engine.local_sheaf_certificate(engine.blocks["anchor-1"])
    assert cert_single is not None
    assert cert_single.dim_relative_h1 == 0
    assert cert_single.harmonic_obstruction_norm == pytest.approx(0.0, abs=1e-9)

    # Shift concept-1 to paradigm 'b' while concept-2 remains in paradigm 'a'.
    # Now synthesis node concept-3 has parents {concept-1 ('b'=[0,1]), concept-2 ('a'=[1,0])}.
    # The least-squares interior state is [0.5, 0.5], and the irreducible relative H^1
    # coboundary residual has Euclidean norm sqrt(4 * 0.5^2) == 1.0!
    engine.add_block(
        KnowledgeBlock(
            id="shift-1-b",
            content="branch 1 shifts to b",
            domain="concept-1",
            paradigm="b",
            evidence_strength=1.0,
            explanatory_power=2.0,
            uncertainty=0.25,
            dependencies={"anchor-0"},
        )
    )
    cert_split = engine.local_sheaf_certificate(engine.blocks["anchor-3"])
    assert cert_split is not None
    assert cert_split.dim_relative_h1 == 2
    assert cert_split.optimal_interior_state == pytest.approx((0.5, 0.5), abs=1e-7)
    assert cert_split.harmonic_obstruction_norm == pytest.approx(1.0, abs=1e-7)
    assert cert_split.dirichlet_energy == pytest.approx(1.0, abs=1e-7)
    assert cert_split.obstructed is True
    assert engine.is_premise_frustrated(engine.blocks["anchor-3"]) is True


def test_orthogonal_2x2x2_factorial_separates_queue_scope_timing_and_duration():
    """Verify across the 8 factorial cells that:
    1. `queue_scope` ("all_domains" vs "domain_isolated") is the factor driving the
       cross-domain scan work inflation, even when `timing_mode="lookahead"` is fixed.
    2. The three single-edge path contrasts sum identically to the total v2 shift."""
    cal = calibrate_v3(6, "star", 64.0, propagate_dependencies=True)
    trace = arrival_trace_v3(6, "star", 0, 3.0 / cal.tau, 36, compatible=False)

    cell_work: dict[tuple[str, str, str], float] = {}
    cell_g_diff: dict[tuple[str, str, str], float] = {}

    for cell in FACTORIAL_CELLS:
        t_mode, q_scope, d_mode = cell
        cas = simulate_orthogonal(
            trace,
            cal,
            "cascade",
            timing_mode=t_mode,
            queue_scope=q_scope,
            duration_mode=d_mode,
        )
        fifo = simulate_orthogonal(
            trace,
            cal,
            "fifo",
            timing_mode=t_mode,
            queue_scope=q_scope,
            duration_mode=d_mode,
        )
        cell_work[cell] = cas["loaded_to_calibrated_work"]
        cell_g_diff[cell] = cas["mean_g"] - fifo["mean_g"]

    # Holding timing_mode="lookahead" and duration_mode="fixed_tau" constant,
    # isolating the serviced domain's queue eliminates cross-domain scan inflation!
    assert (
        cell_work[("lookahead", "domain_isolated", "fixed_tau")]
        < cell_work[("lookahead", "all_domains", "fixed_tau")]
    )

    work_effects = compute_yates_factorial_effects(cell_work)
    assert work_effects["main_effect_queue_isolated_minus_all_domains"] < 0.0
    assert (
        work_effects["path_edge_1_pure_queue_isolation"]
        + work_effects["path_edge_2_pure_snapshot_timing"]
        + work_effects["path_edge_3_pure_work_coupling"]
    ) == pytest.approx(work_effects["path_total_v2_shift"], abs=1e-12)

    g_effects = compute_yates_factorial_effects(cell_g_diff)
    assert (
        g_effects["path_edge_1_pure_queue_isolation"]
        + g_effects["path_edge_2_pure_snapshot_timing"]
        + g_effects["path_edge_3_pure_work_coupling"]
    ) == pytest.approx(g_effects["path_total_v2_shift"], abs=1e-12)


def test_run_sheaf_and_factorial_study_smoke():
    result = run_sheaf_and_factorial_study(
        seeds=(0,),
        concepts=6,
        proposals=24,
        loads=(1.0, 3.0),
        topologies=("star", "diamond_cycle"),
    )
    assert result["row_count"] == 1 * 2 * 2 * 8 * 2
    assert (
        result["sheaf_cohomology_theorems"]["star"]["twisted_last_edge"]["holonomy_obstructed"]
        is False
    )
    assert (
        result["sheaf_cohomology_theorems"]["diamond_cycle"]["twisted_last_edge"][
            "holonomy_obstructed"
        ]
        is True
    )


def test_consensus_arena_sheaf_cohomology_report_tracks_dirichlet_energy_drop():
    """Verify ConsensusArena.sheaf_cohomology_report() computes exact coboundary
    Dirichlet energy ||delta^0 x||_2^2 before and after Psi-Consensus deliberation."""
    from lycheetah.consensus import ConsensusArena

    arena = ConsensusArena(anchor=[1.0, 0.0, 0.0])
    arena.add_agent("a1", [0.98, 0.15, 0.0])
    arena.add_agent("a2", [0.96, -0.15, 0.0])
    arena.add_agent("a3", [0.99, 0.0, 0.12])

    before = arena.sheaf_cohomology_report()
    assert before["cohomology"]["num_vertices"] == 3
    assert before["cohomology"]["num_edges"] == 3
    assert before["cohomology"]["b1_graph"] == 1
    assert before["cohomology"]["dim_h0_global_sections"] == 3
    assert before["cohomology"]["dim_h1_cohomology"] == 3
    assert before["dirichlet_energy"] > 0.01

    verdict = arena.deliberate()
    assert verdict.converged is True
    after = arena.sheaf_cohomology_report()
    assert after["dirichlet_energy"] < before["dirichlet_energy"] * 1e-2
    assert after["dirichlet_energy"] < 1e-3
    assert after["coboundary_norm"] < 0.025


def test_nonidentity_reflection_retains_a_fixed_global_direction():
    sheaf = CellularSheaf.from_parent_graph(
        parents_v3(4, "diamond_cycle"),
        stalk_dim=2,
        twisted_edges={(2, 3): np.diag([1.0, -1.0])},
    )
    cert = sheaf.cohomology_certificate()
    assert cert.dim_h0_global_sections == 1
    assert cert.dim_h1_cohomology == 1
    assert cert.laplacian_lambda_min == 0
    assert cert.holonomy_obstructed is False
    assert cert.global_sections_reduced is True


def test_rank_and_projection_use_the_same_relative_svd_cutoff():
    scale = np.diag([1e12, 1.0])
    sheaf = CellularSheaf(
        2,
        [(0, 1)],
        stalk_dim=2,
        tail_restrictions={(0, 1): scale},
        head_restrictions={(0, 1): scale},
    )
    cert = sheaf.cohomology_certificate()
    projection = sheaf.project_1_cochain(np.array([0.0, 1.0]))
    assert cert.coboundary_rank == 1
    assert projection["numerical_rank"] == cert.coboundary_rank
    assert projection["svd_cutoff"] == cert.svd_cutoff
    assert cert.dim_h1_cohomology == 1
    assert projection["harmonic_norm"] == pytest.approx(1.0)
    assert cert.to_dict()["rank_basis"] == "SVD_CUTOFF"


def test_relative_dimension_and_inverse_share_the_interior_mask():
    scale = np.diag([1e12, 1.0])
    sheaf = CellularSheaf(
        2,
        [(0, 1)],
        stalk_dim=2,
        tail_restrictions={(0, 1): scale},
        head_restrictions={(0, 1): scale},
    )
    relative = sheaf.relative_obstruction({0: [0.0, 1.0]})
    assert relative.numerical_interior_rank == 1
    assert relative.dim_relative_h1 == 1
    assert relative.harmonic_obstruction_norm == pytest.approx(1.0)


def test_explicit_absolute_only_cutoff_retains_the_small_direction():
    scale = np.diag([1e12, 1.0])
    sheaf = CellularSheaf(
        2,
        [(0, 1)],
        stalk_dim=2,
        tail_restrictions={(0, 1): scale},
        head_restrictions={(0, 1): scale},
        svd_rtol=0.0,
    )
    cert = sheaf.cohomology_certificate()
    assert cert.coboundary_rank == 2
    assert cert.dim_h1_cohomology == 0
    assert sheaf.project_1_cochain(np.array([0.0, 1.0]))["harmonic_norm"] < 1e-12


@pytest.mark.parametrize("value", [math.nan, math.inf, -math.inf])
def test_nonfinite_sheaf_inputs_are_rejected(value):
    with pytest.raises(ValueError, match="finite"):
        CellularSheaf(2, [(0, 1)], tail_restrictions={(0, 1): np.diag([value, 1.0])})
    sheaf = CellularSheaf(2, [(0, 1)])
    with pytest.raises(ValueError, match="finite"):
        sheaf.project_1_cochain(np.array([value, 0.0]))
    with pytest.raises(ValueError, match="finite"):
        sheaf.relative_obstruction({0: [value, 0.0]})


def test_edgeless_relative_solution_retains_interior_dimensions():
    sheaf = CellularSheaf(3, [], stalk_dim=2)
    cert = sheaf.relative_obstruction({0: [1.0, 0.0]})
    assert len(cert.optimal_interior_state) == 4
    assert cert.harmonic_obstruction_norm == 0


@pytest.mark.parametrize("vertex", [-1, 2, True])
def test_invalid_boundary_vertices_are_rejected(vertex):
    sheaf = CellularSheaf(2, [(0, 1)])
    with pytest.raises(ValueError, match="vertex"):
        sheaf.relative_obstruction({vertex: [1.0, 0.0]})
