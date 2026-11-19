"""
Scenario Tests: Basic Bridge Geometry Input Testing (Task 2)
============================================================
Comprehensive test suite verifying that:
1. Baseline geometry inputs are correctly configured and processed.
2. Span variations scale preliminary girder depth bounds deterministically.
3. Carriageway and cross-section width modifications update girder layouts.
4. Custom girder counts override defaults and satisfy structural width equations.
5. Deck thickness geometry is validated within code bounds [100, 500] mm.
6. Combined multi-parameter geometric configurations solve deterministically.
7. Invalid geometric inputs are safely rejected or clamped with descriptive errors.
8. GUI automation status is transparently tested and reported.
"""

import os
import copy
import json
import pytest

from osdagbridge.core.utils.common import (
    KEY_SPAN,
    KEY_CARRIAGEWAY_WIDTH,
    KEY_INCLUDE_MEDIAN,
    KEY_FOOTPATH,
    KEY_SKEW_ANGLE,
    KEY_STRUCTURE_TYPE,
    KEY_DESIGN_MODE,
    KEY_GIRDER,
    KEY_DECK_CONCRETE_GRADE_BASIC,
    KEY_TS_OVERALL_WIDTH,
    KEY_TS_NO_OF_GIRDERS,
    KEY_TS_GIRDER_SPACING,
    KEY_TS_DECK_OVERHANG,
    KEY_TS_DECK_THICKNESS,
    KEY_TS_FOOTPATH_WIDTH,
    KEY_TS_FOOTPATH_THICKNESS,
    KEY_CB_WIDTH,
    KEY_RL_WIDTH,
    KEY_MD_WIDTH,
    SPAN_MIN,
    SPAN_MAX,
    CARRIAGEWAY_WIDTH_MIN,
    CARRIAGEWAY_WIDTH_MAX_LIMIT,
    SKEW_ANGLE_MIN,
    SKEW_ANGLE_MAX,
)
from osdagbridge.core.bridge_types.plate_girder.defaults import (
    solve_extend_basic_input_dict,
    seed_no_of_girders,
)
from osdagbridge.core.bridge_types.plate_girder.initial_sizing import BridgeConfigurationSolver
from osdagbridge.core.bridge_types.plate_girder.validator import BridgeInputValidator

EVIDENCE_GEOM_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "test_results", "evidence", "geometry")
)
os.makedirs(EVIDENCE_GEOM_DIR, exist_ok=True)


def _save_evidence(filename: str, data: dict) -> str:
    path = os.path.join(EVIDENCE_GEOM_DIR, filename)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, default=str)
    return path


@pytest.mark.scenario
def test_baseline_geometry(valid_baseline_input):
    """
    Test Case ID: OSB-GEO-001
    Title: Baseline Bridge Geometry Validation
    Category: Scenario / Geometry
    Objective: Verify that baseline 30m span highway bridge geometry correctly initializes,
               solves layout (8.40m overall width, 4 girders, 2.10m spacing, 1.05m overhang),
               and depth bounds follow IRC guidelines [1.20m, 2.00m].
    """
    input_dict = copy.deepcopy(valid_baseline_input)
    solve_extend_basic_input_dict(input_dict)

    # 1. Verify Basic Geometry Parameters
    assert input_dict[KEY_SPAN] == 30.0, f"Expected span 30.0m, got {input_dict[KEY_SPAN]}"
    assert input_dict[KEY_CARRIAGEWAY_WIDTH] == 7.5, f"Expected carriageway 7.5m, got {input_dict[KEY_CARRIAGEWAY_WIDTH]}"
    assert input_dict.get(KEY_INCLUDE_MEDIAN, "No") == "No"
    assert input_dict.get(KEY_FOOTPATH, "None") == "None"

    # 2. Verify Derived Cross-Section Layout
    # Overall width = 7.5 + 2 * 0.45 = 8.40 m
    assert input_dict[KEY_TS_OVERALL_WIDTH] == pytest.approx(8.40, rel=1e-3)
    assert input_dict[KEY_TS_NO_OF_GIRDERS] == 4
    assert input_dict[KEY_TS_GIRDER_SPACING] == pytest.approx(2.10, rel=1e-3)
    assert input_dict[KEY_TS_DECK_OVERHANG] == pytest.approx(1.05, rel=1e-3)

    # 3. Verify Preliminary Depth Bounds
    solver = BridgeConfigurationSolver(carriageway_width=7.5)
    min_d, max_d = solver.get_preliminary_depth_bounds(30.0)
    assert min_d == pytest.approx(1.20, rel=1e-3)  # 30 / 25
    assert max_d == pytest.approx(2.00, rel=1e-3)  # 30 / 15

    # 4. Save Persistent Evidence Artifact
    _save_evidence("OSB-GEO-001_baseline_dict.json", input_dict)


@pytest.mark.scenario
def test_modified_span_length(valid_baseline_input):
    """
    Test Case ID: OSB-GEO-002
    Title: Modified Span Length Scaling and Processing
    Category: Scenario / Geometry
    Objective: Verify that modifying span length across the valid scope [20m, 45m] is correctly retained
               in the Input Dictionary and scales preliminary depth bounds [Span/25, Span/15] deterministically.
    """
    test_spans = [25.0, 36.0, 42.0]
    span_evidence = {}

    solver = BridgeConfigurationSolver(carriageway_width=7.5)

    for span in test_spans:
        d = copy.deepcopy(valid_baseline_input)
        d[KEY_SPAN] = span
        solve_extend_basic_input_dict(d)

        # Confirm span retention
        assert d[KEY_SPAN] == span, f"Span value mutated or lost for {span}m"

        # Verify preliminary depth bounds
        min_depth, max_depth = solver.get_preliminary_depth_bounds(span)
        expected_min = span / 25.0
        expected_max = span / 15.0

        assert min_depth == pytest.approx(expected_min, rel=1e-3)
        assert max_depth == pytest.approx(expected_max, rel=1e-3)

        span_evidence[f"span_{span}m"] = {
            "span_m": span,
            "min_depth_m": min_depth,
            "max_depth_m": max_depth,
            "no_of_girders": d.get(KEY_TS_NO_OF_GIRDERS),
            "girder_spacing_m": d.get(KEY_TS_GIRDER_SPACING),
        }

    _save_evidence("OSB-GEO-002_modified_span_summary.json", span_evidence)


@pytest.mark.scenario
def test_modified_bridge_width(valid_baseline_input):
    """
    Test Case ID: OSB-GEO-003
    Title: Modified Carriageway and Bridge Width Processing
    Category: Scenario / Geometry
    Objective: Verify that modifying carriageway width dynamically updates overall bridge width,
               seeded girder counts, and girder spacing.
    """
    # Test case 1: 8.5m carriageway (wider 2-lane bridge)
    d_85 = copy.deepcopy(valid_baseline_input)
    d_85[KEY_CARRIAGEWAY_WIDTH] = 8.5
    solve_extend_basic_input_dict(d_85)

    # Overall = 8.5 + 2*0.45 = 9.40 m
    assert d_85[KEY_TS_OVERALL_WIDTH] == pytest.approx(9.40, rel=1e-3)
    assert d_85[KEY_TS_NO_OF_GIRDERS] == 4
    assert d_85[KEY_TS_GIRDER_SPACING] == pytest.approx(2.35, rel=1e-3)
    assert d_85[KEY_TS_DECK_OVERHANG] == pytest.approx(1.175, rel=1e-3)

    # Test case 2: 10.5m carriageway (3-lane bridge)
    d_105 = copy.deepcopy(valid_baseline_input)
    d_105[KEY_CARRIAGEWAY_WIDTH] = 10.5
    solve_extend_basic_input_dict(d_105)

    # Overall = 10.5 + 2*0.45 = 11.40 m -> triggers 5 girders
    assert d_105[KEY_TS_OVERALL_WIDTH] == pytest.approx(11.40, rel=1e-3)
    assert d_105[KEY_TS_NO_OF_GIRDERS] == 5
    assert d_105[KEY_TS_GIRDER_SPACING] == pytest.approx(2.28, rel=1e-3)
    assert d_105[KEY_TS_DECK_OVERHANG] == pytest.approx(1.14, rel=1e-3)

    # Test case 3: 12.0m dual carriageway with 1.2m median
    d_dual = copy.deepcopy(valid_baseline_input)
    d_dual[KEY_CARRIAGEWAY_WIDTH] = 12.0
    d_dual[KEY_INCLUDE_MEDIAN] = "Yes"
    d_dual[KEY_MD_WIDTH] = 1.2
    solve_extend_basic_input_dict(d_dual)

    # Overall = 2 * 12.0 + 1.2 + 2 * 0.45 = 26.10 m
    assert d_dual[KEY_TS_OVERALL_WIDTH] == pytest.approx(26.10, rel=1e-3)
    assert d_dual[KEY_TS_NO_OF_GIRDERS] >= 10

    _save_evidence("OSB-GEO-003_modified_width_summary.json", {
        "case_8.5m": {"overall_width": d_85[KEY_TS_OVERALL_WIDTH], "girders": d_85[KEY_TS_NO_OF_GIRDERS], "spacing": d_85[KEY_TS_GIRDER_SPACING]},
        "case_10.5m": {"overall_width": d_105[KEY_TS_OVERALL_WIDTH], "girders": d_105[KEY_TS_NO_OF_GIRDERS], "spacing": d_105[KEY_TS_GIRDER_SPACING]},
        "case_dual_12.0m": {"overall_width": d_dual[KEY_TS_OVERALL_WIDTH], "girders": d_dual[KEY_TS_NO_OF_GIRDERS]},
    })


@pytest.mark.scenario
def test_modified_girder_configuration(valid_baseline_input):
    """
    Test Case ID: OSB-GEO-004
    Title: Modified Girder Count and Spacing Override
    Category: Scenario / Geometry
    Objective: Verify that specifying a custom girder count (5 girders instead of default 4 on 8.40m bridge)
               is honored by the layout solver and satisfies the width continuity equation.
    """
    d = copy.deepcopy(valid_baseline_input)
    d[KEY_TS_NO_OF_GIRDERS] = 5
    solve_extend_basic_input_dict(d)

    assert d[KEY_TS_NO_OF_GIRDERS] == 5, "Custom girder count 5 was not retained"
    assert d[KEY_TS_GIRDER_SPACING] == pytest.approx(1.68, rel=1e-3)
    assert d[KEY_TS_DECK_OVERHANG] == pytest.approx(0.84, rel=1e-3)

    # Check width identity: (n_girders - 1) * spacing + 2 * overhang == overall_width
    computed_width = (5 - 1) * d[KEY_TS_GIRDER_SPACING] + 2 * d[KEY_TS_DECK_OVERHANG]
    assert computed_width == pytest.approx(d[KEY_TS_OVERALL_WIDTH], rel=1e-4)

    _save_evidence("OSB-GEO-004_custom_girders_dict.json", d)


@pytest.mark.scenario
def test_modified_deck_geometry():
    """
    Test Case ID: OSB-GEO-005
    Title: Modified Deck Geometry and Thickness Limits
    Category: Scenario / Geometry
    Objective: Verify that deck thickness conforms to design limits [100mm, 500mm] in validator,
               and document default substitution behavior in typical section defaults.
    """
    validator = BridgeInputValidator()

    # 1. Validation across acceptable thickness range [100, 500] mm
    valid_thicknesses = [150.0, 200.0, 250.0, 280.0, 300.0, 450.0]
    for t in valid_thicknesses:
        err = validator.validate_additional_inputs(KEY_TS_DECK_THICKNESS, {KEY_TS_DECK_THICKNESS: t})
        assert err is None, f"Expected deck thickness {t} mm to be valid, got {err}"

    # 2. Out-of-bounds rejection / clamping
    err_under = validator.validate_additional_inputs(KEY_TS_DECK_THICKNESS, {KEY_TS_DECK_THICKNESS: 80.0})
    assert err_under is not None and err_under[0] == 100.0

    err_over = validator.validate_additional_inputs(KEY_TS_DECK_THICKNESS, {KEY_TS_DECK_THICKNESS: 550.0})
    assert err_over is not None and err_over[0] == 500.0

    # 3. Document unexpected default substitution in _update_typical_section_defaults
    # Note: solve_extend_basic_input_dict unconditionally overwrites KEY_TS_DECK_THICKNESS with 250.0
    d = {KEY_SPAN: 30.0, KEY_CARRIAGEWAY_WIDTH: 7.5, KEY_TS_DECK_THICKNESS: 300.0}
    solve_extend_basic_input_dict(d)
    # Documents that current defaults.py resets deck thickness to 250.0
    actual_t = d.get(KEY_TS_DECK_THICKNESS)
    assert actual_t == 250.0, "Expected documented default substitution (250.0mm) to occur"

    _save_evidence("OSB-GEO-005_deck_geometry_evidence.json", {
        "valid_thicknesses": valid_thicknesses,
        "clamped_under": err_under,
        "clamped_over": err_over,
        "defaults_substitution_observed": actual_t,
    })


@pytest.mark.scenario
def test_combined_geometry_modification():
    """
    Test Case ID: OSB-GEO-006
    Title: Combined Geometry Modification
    Category: Scenario / Geometry
    Objective: Verify combined modification of multiple geometric parameters in a single design configuration:
               36m span, 8.5m carriageway, 15° skew angle, dual 1.5m footpaths, railings, and crash barriers.
    """
    combined_input = {
        KEY_STRUCTURE_TYPE: "Plate Girder",
        KEY_DESIGN_MODE: "Optimized",
        KEY_SPAN: 36.0,
        KEY_CARRIAGEWAY_WIDTH: 8.5,
        KEY_INCLUDE_MEDIAN: "No",
        KEY_FOOTPATH: "Both Sides",
        KEY_SKEW_ANGLE: 15.0,
        KEY_GIRDER: "E350",
        KEY_DECK_CONCRETE_GRADE_BASIC: "M40",
        "project.title": "Combined Geometry 36m Bridge",
    }
    solve_extend_basic_input_dict(combined_input)

    # Overall width: Carriageway (8.5) + 2*Barrier (2*0.45) + 2*Footpath (2*1.5) + 2*Railing (2*0.375)
    # = 8.5 + 0.90 + 3.0 + 0.75 = 13.15 m
    assert combined_input[KEY_TS_OVERALL_WIDTH] == pytest.approx(13.15, rel=1e-3)
    assert combined_input[KEY_TS_NO_OF_GIRDERS] == 6
    assert combined_input[KEY_TS_GIRDER_SPACING] == pytest.approx(2.1917, rel=1e-3)
    assert combined_input[KEY_TS_DECK_OVERHANG] == pytest.approx(1.0958, rel=1e-3)

    # Check structural equation
    calc_w = (6 - 1) * combined_input[KEY_TS_GIRDER_SPACING] + 2 * combined_input[KEY_TS_DECK_OVERHANG]
    assert calc_w == pytest.approx(13.15, rel=1e-4)

    _save_evidence("OSB-GEO-006_combined_geometry_dict.json", combined_input)


@pytest.mark.scenario
def test_invalid_geometry_handling():
    """
    Test Case ID: OSB-GEO-007
    Title: Invalid Geometry Input Rejection and Clamping
    Category: Scenario / Geometry
    Objective: Verify that invalid geometric parameters (negative dimensions, out-of-scope spans,
               unsupported skew angles) are safely rejected or clamped with descriptive error messages.
    """
    validator = BridgeInputValidator()

    # 1. Span out of scope
    res_under = validator.validate_basic_inputs(KEY_SPAN, {KEY_SPAN: 15.0})
    assert res_under is not None
    assert res_under[0] == SPAN_MIN
    assert "between 20.0 m and 45.0 m" in res_under[1]

    res_over = validator.validate_basic_inputs(KEY_SPAN, {KEY_SPAN: 50.0})
    assert res_over is not None
    assert res_over[0] == SPAN_MAX
    assert "between 20.0 m and 45.0 m" in res_over[1]

    # 2. Non-numeric span
    res_str = validator.validate_basic_inputs(KEY_SPAN, {KEY_SPAN: "invalid_span"})
    assert res_str is not None
    assert res_str[0] == SPAN_MIN
    assert "numeric value" in res_str[1]

    # 3. Negative carriageway width
    res_neg_cw = validator.validate_basic_inputs(KEY_CARRIAGEWAY_WIDTH, {KEY_CARRIAGEWAY_WIDTH: -5.0, KEY_INCLUDE_MEDIAN: "No"})
    assert res_neg_cw is not None
    assert "Minimum carriageway width" in res_neg_cw[1] or res_neg_cw[0] >= CARRIAGEWAY_WIDTH_MIN

    # 4. Out-of-bounds skew angle (> 15 degrees)
    res_skew = validator.validate_basic_inputs(KEY_SKEW_ANGLE, {KEY_SKEW_ANGLE: 60.0})
    assert res_skew is not None
    assert res_skew[0] == SKEW_ANGLE_MAX
    assert "between -15.0° and 15.0°" in res_skew[1]

    _save_evidence("OSB-GEO-007_invalid_geometry_summary.json", {
        "span_under": res_under,
        "span_over": res_over,
        "span_non_numeric": res_str,
        "carriageway_negative": res_neg_cw,
        "skew_over": res_skew,
    })


@pytest.mark.scenario
def test_gui_input_dock_automation_status():
    """
    Test Case ID: OSB-GEO-008
    Title: GUI InputDock Interface Automation Status Check
    Category: Scenario / Geometry
    Objective: Attempt direct headless instantiation of InputDock; marks BLOCKED if PySide6
               GUI framework is missing from the environment.
    """
    try:
        from PySide6.QtWidgets import QApplication
        from osdagbridge.desktop.ui.docks.input_dock import InputDock
    except (ImportError, ModuleNotFoundError) as err:
        pytest.skip(f"PySide6 GUI framework missing on host environment: {err} — marked BLOCKED")

    try:
        app = QApplication.instance() or QApplication([])
        dock = InputDock(backend=None, parent=None)
        assert dock is not None
    except Exception as exc:
        pytest.fail(f"InputDock instantiation crashed: {exc}")
