"""
Integration Tests: Design Execution and Reporting Subsystems
============================================================
Tests end-to-end bridge instantiation, BOQ quantity calculations,
and report generation styling integration.
"""

import os
import pytest
from typing import Dict, Any

from osdagbridge.core.boq.boq_generator import calculate_material_quantities
from osdagbridge.core.reports.styles import (
    PAGE_SIZE,
    MARGIN_TOP,
    MARGIN_BOTTOM,
    COLOR_OSDAG_GREEN,
    get_geometry_setup_latex,
    get_header_footer_latex,
    get_table_styling_latex,
)
from osdagbridge.core.reports.table_utils import make_repeated_header


@pytest.mark.integration
def test_plate_girder_bridge_instantiation(valid_baseline_input):
    """
    Test Case ID: OSB-INT-007
    Title: Plate Girder Bridge Class Lifecycle and Instantiation
    Category: Integration / Core Execution
    Objective: Verify PlateGirderBridge lifecycle; marks BLOCKED if OpenSeesPy dependency is missing.
    """
    try:
        from osdagbridge.core.bridge_types.plate_girder.plategirderbridge import PlateGirderBridge
    except (ImportError, ModuleNotFoundError) as err:
        pytest.skip(f"OpenSeesPy dependency missing on this host environment: {err} — marked BLOCKED")

    try:
        bridge = PlateGirderBridge()
        assert bridge is not None
    except Exception as exc:
        pytest.fail(f"PlateGirderBridge instantiation failed with error: {exc}")


@pytest.mark.integration
def test_boq_material_quantities_integration(valid_baseline_input, baseline_design_result):
    """
    Test Case ID: OSB-INT-008
    Title: BOQ Material Quantities Calculation Integration
    Category: Integration / BOQ
    Objective: Verify calculate_material_quantities processes baseline inputs and output dictionary to produce material take-off values.
    """
    from osdagbridge.core.bridge_types.plate_girder.defaults import solve_extend_basic_input_dict
    expanded_inputs = solve_extend_basic_input_dict(valid_baseline_input.copy())

    quantities = calculate_material_quantities(expanded_inputs, baseline_design_result)

    assert isinstance(quantities, dict), "Expected quantities to be a dictionary"
    assert "steel_girders_vol_formula" in quantities, "Missing steel_girders_vol_formula in BOQ"
    assert "bracing_diag_vol_formula" in quantities, "Missing bracing_diag_vol_formula in BOQ"
    assert "bracing_top_vol_formula" in quantities, "Missing bracing_top_vol_formula in BOQ"


@pytest.mark.integration
def test_report_generator_styles_integration():
    """
    Test Case ID: OSB-INT-009
    Title: PDF Report Generator Styling Integration
    Category: Integration / Reporting
    Objective: Verify report styling configuration initializes with standardized typography and geometry.
    """
    assert PAGE_SIZE == "a4paper", f"Expected a4paper, got {PAGE_SIZE}"
    assert MARGIN_TOP == "1.0in", f"Expected 1.0in top margin, got {MARGIN_TOP}"
    assert MARGIN_BOTTOM == "1.25in", f"Expected 1.25in bottom margin, got {MARGIN_BOTTOM}"
    assert COLOR_OSDAG_GREEN == "#91B014", f"Expected Osdag green #91B014, got {COLOR_OSDAG_GREEN}"

    geom_latex = get_geometry_setup_latex()
    assert "\\usepackage" in geom_latex
    assert "geometry" in geom_latex

    header_latex = get_header_footer_latex("Test Project", "JOB-001", "2026-11-19", "v1.0")
    assert "fancyhead" in header_latex
    assert "fancyfoot" in header_latex

    tbl_styling = get_table_styling_latex()
    assert len(tbl_styling) > 0
