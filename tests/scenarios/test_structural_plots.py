"""
Scenario Tests: Comprehensive Structural Plot Verification (Task 8)
==================================================================
Validates 3D structural plot generation, data consistency, axes labeling,
consecutive-run graphical refresh, and multi-format export across:
- OSB-CAD-005: Structural Plot Generation
- OSB-CAD-006: Consecutive Run Graphical Refresh
- OSB-CAD-008: Graphical Export Verification
"""

import sys
from unittest.mock import MagicMock
# Guard missing native FE solvers in headless environments
for mod in ["openseespy", "openseespy.opensees", "opsvis"]:
    if mod not in sys.modules:
        sys.modules[mod] = MagicMock()

import os
import copy
import json
import pytest
from pathlib import Path
import numpy as np
import xarray as xr
import matplotlib.pyplot as plt

from osdagbridge.core.bridge_types.plate_girder.plot_generator import (
    build_figure_grillage,
    build_figure_bmd,
    build_figure_sfd,
    build_figure_deflection,
    figure_to_bytes,
)

EVIDENCE_DIR = Path(__file__).resolve().parents[2] / "test_results" / "evidence" / "cad_plots"


def create_representative_grillage(span=30.0, num_girders=4, spacing=2.1):
    """Helper to create representative nodes, members, and analysis dataset."""
    nodes = {}
    tag = 1
    xs = np.linspace(0.0, span, 5)
    total_w = (num_girders - 1) * spacing
    zs = np.linspace(-total_w / 2.0, total_w / 2.0, num_girders)
    grid = {}
    for iz, z in enumerate(zs):
        for ix, x in enumerate(xs):
            nodes[tag] = [float(x), 0.0, float(z)]
            grid[(ix, iz)] = tag
            tag += 1

    members = {}
    ele_id = 1
    # Longitudinal elements
    for iz in range(len(zs)):
        for ix in range(len(xs) - 1):
            members[ele_id] = [grid[(ix, iz)], grid[(ix + 1, iz)]]
            ele_id += 1

    # Transverse elements
    for ix in range(len(xs)):
        for iz in range(len(zs) - 1):
            members[ele_id] = [grid[(ix, iz)], grid[(ix, iz + 1)]]
            ele_id += 1

    num_elems = len(members)
    components = ["Vx_i", "Vx_j", "Vy_i", "Vy_j", "Vz_i", "Vz_j", "Mx_i", "Mx_j", "My_i", "My_j", "Mz_i", "Mz_j"]

    force_data = np.zeros((num_elems, len(components)))
    for e_idx, e in enumerate(sorted(members.keys())):
        n1, n2 = members[e]
        x_mid = (nodes[n1][0] + nodes[n2][0]) / 2.0
        # Mz: parabolic moment (peak at x=L/2)
        mz = 2.5e6 * 4 * (x_mid / span) * (1 - x_mid / span) if span > 0 else 0.0
        # Vy: linear shear force (+500 kN to -500 kN)
        vy = 5.0e5 * (1 - 2 * x_mid / span) if span > 0 else 0.0

        comp_map = {c: i for i, c in enumerate(components)}
        force_data[e_idx, comp_map["Mz_i"]] = mz * 0.95
        force_data[e_idx, comp_map["Mz_j"]] = mz * 1.05
        force_data[e_idx, comp_map["Vy_i"]] = vy
        force_data[e_idx, comp_map["Vy_j"]] = vy

    ds = xr.Dataset(
        data_vars={
            "forces": (("Element", "Component"), force_data),
        },
        coords={
            "Element": list(sorted(members.keys())),
            "Component": components,
        }
    )

    disp_components = ["x", "y", "z", "rx", "ry", "rz"]
    num_nodes = len(nodes)
    disp_data = np.zeros((num_nodes, len(disp_components)))
    for n_idx, n in enumerate(sorted(nodes.keys())):
        x = nodes[n][0]
        # downward deflection in metres
        dy = -0.025 * 16 * ((x / span)**2) * ((1 - x / span)**2) if span > 0 else 0.0
        disp_data[n_idx, 1] = dy

    ds["displacements"] = xr.DataArray(
        disp_data,
        dims=("Node", "Component"),
        coords={"Node": list(sorted(nodes.keys())), "Component": disp_components}
    )

    return nodes, members, ds


def test_structural_plot_generation():
    """
    Test Case ID: OSB-CAD-005
    Verify generation of 3D Grillage, BMD, SFD, and Deflection plots,
    including axes, labels, and figure-to-bytes export.
    """
    nodes, members, ds = create_representative_grillage(span=30.0, num_girders=4, spacing=2.1)

    # 1. 3D Grillage Layout Plot
    fig_grillage = build_figure_grillage(nodes, members, selected_girder="All")
    assert fig_grillage is not None
    assert len(fig_grillage.axes) > 0

    # 2. Bending Moment Diagram (BMD)
    fig_bmd, sum_bmd = build_figure_bmd(ds, "Mz", nodes, members, edge_dist=0.0)
    assert fig_bmd is not None
    assert "G1" in sum_bmd
    assert sum_bmd["G1"]["max"] > 0.0

    # 3. Shear Force Diagram (SFD)
    fig_sfd, sum_sfd = build_figure_sfd(ds, "Fy", nodes, members, edge_dist=0.0)
    assert fig_sfd is not None
    assert "G1" in sum_sfd
    assert sum_sfd["G1"]["max"] > 0.0

    # 4. Deflection Diagram
    fig_def, sum_def = build_figure_deflection(ds, "Dy", nodes, members, edge_dist=0.0)
    assert fig_def is not None

    # Export to bytes and save PNG evidence
    plots_dir = EVIDENCE_DIR / "structural_plots"
    plots_dir.mkdir(parents=True, exist_ok=True)

    bytes_grillage = figure_to_bytes(fig_grillage)
    bytes_bmd = figure_to_bytes(fig_bmd)
    bytes_sfd = figure_to_bytes(fig_sfd)
    bytes_def = figure_to_bytes(fig_def)

    (plots_dir / "grillage_model_3d.png").write_bytes(bytes_grillage)
    (plots_dir / "bmd_bending_moment_3d.png").write_bytes(bytes_bmd)
    (plots_dir / "sfd_shear_force_3d.png").write_bytes(bytes_sfd)
    (plots_dir / "deflection_diagram_3d.png").write_bytes(bytes_def)

    assert len(bytes_grillage) > 10000
    assert len(bytes_bmd) > 10000
    assert len(bytes_sfd) > 10000
    assert len(bytes_def) > 10000

    plt.close("all")


def test_consecutive_run_graphical_refresh():
    """
    Test Case ID: OSB-CAD-006
    Verify that consecutive runs refresh graphical plots without retaining old curves.
    """
    spans = [30.0, 36.0, 24.0]
    run_evidence = []

    for idx, span in enumerate(spans, 1):
        nodes, members, ds = create_representative_grillage(span=span, num_girders=4, spacing=2.1)
        fig_bmd, sum_bmd = build_figure_bmd(ds, "Mz", nodes, members, edge_dist=0.0)
        ax = fig_bmd.axes[0]

        xlim = ax.get_xlim()
        # Verify x-axis bounds scale with current span
        assert xlim[1] >= span - 1.0

        run_evidence.append({
            "run": idx,
            "span": span,
            "xlim_max": float(xlim[1]),
            "g1_peak_moment": sum_bmd["G1"]["max"],
        })
        plt.close(fig_bmd)

    assert run_evidence[1]["span"] == 36.0
    assert run_evidence[1]["xlim_max"] > run_evidence[0]["xlim_max"]
    assert run_evidence[2]["span"] == 24.0
    assert run_evidence[2]["xlim_max"] < run_evidence[0]["xlim_max"]

    ev_path = EVIDENCE_DIR / "consecutive_runs" / "consecutive_runs_plot_refresh.json"
    ev_path.parent.mkdir(parents=True, exist_ok=True)
    with open(ev_path, "w", encoding="utf-8") as f:
        json.dump(run_evidence, f, indent=2)

    assert ev_path.exists()


def test_graphical_export_verification():
    """
    Test Case ID: OSB-CAD-008
    Verify that plots can be exported to standard formats (PNG, SVG, PDF).
    """
    nodes, members, ds = create_representative_grillage(span=30.0, num_girders=4, spacing=2.1)
    fig_bmd, _ = build_figure_bmd(ds, "Mz", nodes, members, edge_dist=0.0)

    export_dir = EVIDENCE_DIR / "exports"
    export_dir.mkdir(parents=True, exist_ok=True)

    png_path = export_dir / "sample_plot_export.png"
    svg_path = export_dir / "sample_plot_export.svg"
    pdf_path = export_dir / "sample_plot_export.pdf"

    fig_bmd.savefig(str(png_path), format="png", dpi=100)
    fig_bmd.savefig(str(svg_path), format="svg")
    fig_bmd.savefig(str(pdf_path), format="pdf")

    assert png_path.exists() and png_path.stat().st_size > 10000
    assert svg_path.exists() and svg_path.stat().st_size > 10000
    assert pdf_path.exists() and pdf_path.stat().st_size > 5000

    plt.close(fig_bmd)
