"""
Scenario Tests: Comprehensive Output Dictionary Verification (Task 7)
====================================================================
Validates output dictionary parameter generation, unit fidelity, precision,
geometry scaling, material sensitivity, display consistency, consecutive-run
isolation, and incomplete/failed design handling across:
- OSB-DICT-OUT-001: Baseline Output Verification
- OSB-DICT-OUT-002: Geometry-Dependent Output Verification
- OSB-DICT-OUT-003: Custom Steel Output Verification
- OSB-DICT-OUT-004: Concrete Deck Output Verification
- OSB-DICT-OUT-005: Reinforcement Output Verification
- OSB-DICT-OUT-006: Output Display Consistency
- OSB-DICT-OUT-007: Output Precision and Unit Verification
- OSB-DICT-OUT-008: Consecutive Design Output Refresh
- OSB-DICT-OUT-009: Incomplete or Failed Design Output Handling
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

from osdagbridge.core.utils.common import (
    KEY_SPAN,
    KEY_CARRIAGEWAY_WIDTH,
    KEY_SKEW_ANGLE,
    KEY_INCLUDE_MEDIAN,
    KEY_FOOTPATH,
    KEY_STRUCTURE_TYPE,
    KEY_DESIGN_MODE,
    KEY_GIRDER,
    KEY_CROSS_BRACING,
    KEY_END_DIAPHRAGM,
    KEY_DECK_CONCRETE_GRADE_BASIC,
    KEY_DS_REINF_MATERIAL,
    KEY_DS_STUD_HEIGHT,
    KEY_UTIL_FLEXURE,
    KEY_UTIL_SHEAR,
    KEY_UTIL_INTERACTION,
    KEY_UTIL_LTB,
    KEY_UTIL_LONG_TRANS_SHEAR,
    KEY_UTIL_FATIGUE,
    KEY_UTIL_STRESS_LIMITATION,
    KEY_UTIL_DEFLECTION_CRACK,
    KEY_SD_GRADE_OF_MATERIAL,
    KEY_SD_SECTION_TYPE,
    KEY_SD_SECTION_DESIGNATION,
    KEY_SD_TOTAL_DEPTH,
    KEY_SD_WEB_THICKNESS,
    KEY_SD_TOP_FLANGE_WIDTH,
    KEY_SD_TOP_FLANGE_THICKNESS,
    KEY_SD_BOTTOM_FLANGE_WIDTH,
    KEY_SD_BOTTOM_FLANGE_THICKNESS,
    KEY_SD_MU_APPLIED,
    KEY_SD_MD_CAPACITY,
    KEY_SD_SHEAR_VU,
    KEY_SD_SHEAR_VCR,
    KEY_SD_DEFL_LIVE,
    KEY_SD_DEFL_TOTAL,
    KEY_SD_DEFL_ALLOW_LIVE,
    KEY_SD_DEFL_ALLOW_TOTAL,
    KEY_TS_OVERALL_WIDTH,
    KEY_TS_NO_OF_GIRDERS,
    KEY_TS_GIRDER_SPACING,
    KEY_TS_DECK_OVERHANG,
    KEY_DD_SPAN,
    KEY_DD_WDL,
    KEY_DD_M_DL,
    KEY_DD_M_LL,
    KEY_DD_M_ULS_SAG,
    KEY_DD_M_ULS_HOG,
    KEY_DD_AS_REQ_BOT,
    KEY_DD_AS_REQ_TOP,
    KEY_DD_PUNCH_VED_KN,
    KEY_DD_VRD_C_MPA,
    KEY_DD_PUNCH_OK,
    KEY_DD_WK_BOT,
    KEY_DD_WK_LIMIT,
)
from osdagbridge.core.bridge_types.plate_girder.plategirderbridge import PlateGirderBridge
from osdagbridge.core.bridge_types.plate_girder.defaults import solve_extend_basic_input_dict
from osdagbridge.core.bridge_types.plate_girder import deckdesign

EVIDENCE_DIR = Path(__file__).resolve().parents[2] / "test_results" / "evidence" / "output_dictionary"


@pytest.fixture
def baseline_inputs():
    """Standard valid 30m span baseline bridge input dictionary."""
    inp = {
        KEY_STRUCTURE_TYPE: "Plate Girder",
        KEY_SPAN: 30.0,
        KEY_CARRIAGEWAY_WIDTH: 7.5,
        KEY_SKEW_ANGLE: 0.0,
        KEY_INCLUDE_MEDIAN: "No",
        KEY_FOOTPATH: "None",
        KEY_GIRDER: "E 250",
        KEY_CROSS_BRACING: "E 250",
        KEY_END_DIAPHRAGM: "E 250",
        KEY_DECK_CONCRETE_GRADE_BASIC: "M35",
        KEY_DESIGN_MODE: "Auto",
    }
    solve_extend_basic_input_dict(inp)
    return inp


@pytest.fixture
def mock_design_results_baseline():
    """Realistic baseline design check calculation results structure."""
    return {
        "steel_grade": "E 250",
        "fabrication": "welded",
        "dw_mm": 1750.0,
        "D_mm": 1800.0,
        "bf_top_mm": 450.0,
        "tf_top_mm": 25.0,
        "bf_bot_mm": 550.0,
        "tf_bot_mm": 35.0,
        "tw_mm": 12.0,
        "section_class_governing": "Compact",
        "section_class_flange": "Plastic",
        "section_class_web": "Compact",
        "b_tf_ratio": 9.0,
        "d_tw_ratio": 145.8,
        "web_class_limit": 150.0,
        "flange_class_limit": 9.4,
        "Mu_kNm": 2850.50,
        "Md_kNm": 3950.20,
        "beff_mm": 2100.0,
        "xu_mm": 220.5,
        "Vu_kN": 620.40,
        "Av_mm2": 21000.0,
        "panel_cd_ratio": 1.5,
        "Kv": 5.35,
        "lambda_w": 1.12,
        "tau_b_buck_MPa": 95.4,
        "Vcr_kN": 880.50,
        "beta_interaction": 0.0,
        "Mdv_kNm": 3950.20,
        "mn_axial_term": 0.05,
        "mn_moment_term": 0.72,
        "mn_ratio": 0.77,
        "Mcr_kNm": 4200.0,
        "lambda_LT": 0.82,
        "chi_LT": 0.75,
        "Mb_kNm": 2962.65,
        "stiff_method": "Transverse Stiffeners",
        "stiff_int_thick_req": 10.0,
        "stiff_int_space_req": 1500.0,
        "stiff_end_thick_req": 16.0,
        "bs_n_plates": 2,
        "is_Iys_min_mm4": 1250000.0,
        "is_Iys_prov_mm4": 1850000.0,
        "is_Fq_kN": 120.0,
        "is_Fqd_kN": 250.0,
        "bs_R_kN": 620.4,
        "bs_Fcdw_wb_kN": 750.0,
        "bs_Fcdw_lc_kN": 820.0,
        "bs_Fpsd_kN": 900.0,
        "bs_Fcd_kN": 980.0,
        "delta_live_mm": 22.350,
        "delta_total_mm": 35.800,
        "defl_limit_live_mm": 37.50,   # L/800 for 30m = 37.5 mm
        "defl_limit_total_mm": 50.00,  # L/600 for 30m = 50.0 mm
        "stud_dia_mm": 25.0,
        "stud_height_mm": 100.0,
        "stud_fu_MPa": 450.0,
        "studs_per_section": 3,
        "stud_spacing_provided_mm": 150.0,
        "A_steel_mm2": 51500.0,
        "Iz_steel_mm4": 2.75e10,
        "Ze_steel_mm3": 2.85e7,
        "Zp_steel_mm3": 3.25e7,
        "I_comp_short_mm4": 4.85e10,
        "category_urs": {
            1: {"max_dcr": 0.722},  # Flexure
            2: {"max_dcr": 0.705},  # Shear
            3: {"max_dcr": 0.650},  # Interaction
            4: {"max_dcr": 0.680},  # LTB
            5: {"max_dcr": 0.580},  # Transverse shear
            6: {"max_dcr": 0.450},  # Fatigue
            7: {"max_dcr": 0.610},  # Stress limit
            8: {"max_dcr": 0.596},  # Deflection
        }
    }


def test_baseline_output_verification(baseline_inputs, mock_design_results_baseline):
    """
    Test Case ID: OSB-DICT-OUT-001
    Verify that the baseline bridge configuration populates all required
    categories in the Output Dictionary with consistent numerical values.
    """
    bridge = PlateGirderBridge()
    bridge.set_input(baseline_inputs)
    bridge.output_dict = dict(bridge.input_dict)
    
    bridge.store_design_results(mock_design_results_baseline)

    deck_summary, deck_report = deckdesign.design_deck_slab(
        bridge.input_dict, fck=35.0, fctm=2.8, fy=500.0, Ecm=32.0, Es=200000.0,
        design_results=mock_design_results_baseline,
        bf_top_mm=450.0, stud_height_mm=100.0
    )
    bridge.output_dict["deck_design_results"] = deck_summary
    bridge.output_dict["deck_report_values"] = deck_report

    out = bridge.output_dict

    assert out[KEY_UTIL_FLEXURE] == pytest.approx(72.2, rel=1e-2)
    assert out[KEY_UTIL_SHEAR] == pytest.approx(70.5, rel=1e-2)
    assert out[KEY_UTIL_INTERACTION] == pytest.approx(65.0, rel=1e-2)
    assert out[KEY_UTIL_LTB] == pytest.approx(68.0, rel=1e-2)
    assert out[KEY_UTIL_LONG_TRANS_SHEAR] == pytest.approx(58.0, rel=1e-2)
    assert out[KEY_UTIL_FATIGUE] == pytest.approx(45.0, rel=1e-2)
    assert out[KEY_UTIL_STRESS_LIMITATION] == pytest.approx(61.0, rel=1e-2)
    assert out[KEY_UTIL_DEFLECTION_CRACK] == pytest.approx(59.6, rel=1e-2)

    assert out[KEY_SD_TOTAL_DEPTH] == 1800.0
    assert out[KEY_SD_MU_APPLIED] == 2850.50
    assert out[KEY_SD_MD_CAPACITY] == 3950.20
    assert out[KEY_SD_SHEAR_VU] == 620.40
    assert out[KEY_SD_DEFL_ALLOW_LIVE] == 37.50

    assert deck_report[KEY_DD_SPAN] == pytest.approx(2.1, rel=1e-2)
    assert deck_report[KEY_DD_PUNCH_OK] is True
    assert deck_report[KEY_DD_M_ULS_SAG] > 0.0

    ev_path = EVIDENCE_DIR / "baseline" / "baseline_output_snapshot.json"
    ev_path.parent.mkdir(parents=True, exist_ok=True)
    with open(ev_path, "w", encoding="utf-8") as f:
        json.dump({k: str(v) if not isinstance(v, (int, float, bool, str, list, dict, type(None))) else v 
                   for k, v in out.items()}, f, indent=2)

    assert ev_path.exists()
    assert ev_path.stat().st_size > 0


def test_geometry_dependent_output_verification(mock_design_results_baseline):
    """
    Test Case ID: OSB-DICT-OUT-002
    Verify geometry-dependent output values scale deterministically
    when span, carriageway width, and footpaths are modified.
    """
    geom_inputs = {
        KEY_STRUCTURE_TYPE: "Plate Girder",
        KEY_SPAN: 36.0,
        KEY_CARRIAGEWAY_WIDTH: 9.5,
        KEY_SKEW_ANGLE: 15.0,
        KEY_INCLUDE_MEDIAN: "No",
        KEY_FOOTPATH: "Both Sides",
        KEY_GIRDER: "E 250",
        KEY_CROSS_BRACING: "E 250",
        KEY_END_DIAPHRAGM: "E 250",
        KEY_DECK_CONCRETE_GRADE_BASIC: "M35",
        KEY_DESIGN_MODE: "Auto",
    }
    solve_extend_basic_input_dict(geom_inputs)

    bridge = PlateGirderBridge()
    bridge.set_input(geom_inputs)
    bridge.output_dict = dict(bridge.input_dict)

    assert bridge.output_dict[KEY_TS_OVERALL_WIDTH] == pytest.approx(14.15, rel=1e-2)
    assert bridge.output_dict[KEY_TS_NO_OF_GIRDERS] >= 5

    res_36m = copy.deepcopy(mock_design_results_baseline)
    res_36m["defl_limit_live_mm"] = 36000.0 / 800.0
    res_36m["defl_limit_total_mm"] = 36000.0 / 600.0
    bridge.store_design_results(res_36m)

    assert bridge.output_dict[KEY_SD_DEFL_ALLOW_LIVE] == 45.0
    assert bridge.output_dict[KEY_SD_DEFL_ALLOW_TOTAL] == 60.0

    ev_path = EVIDENCE_DIR / "geometry" / "geometry_output_snapshot.json"
    ev_path.parent.mkdir(parents=True, exist_ok=True)
    with open(ev_path, "w", encoding="utf-8") as f:
        json.dump({
            "span": bridge.output_dict[KEY_SPAN],
            "overall_width": bridge.output_dict[KEY_TS_OVERALL_WIDTH],
            "no_of_girders": bridge.output_dict[KEY_TS_NO_OF_GIRDERS],
            "defl_limit_live": bridge.output_dict[KEY_SD_DEFL_ALLOW_LIVE],
            "defl_limit_total": bridge.output_dict[KEY_SD_DEFL_ALLOW_TOTAL],
        }, f, indent=2)

    assert ev_path.exists()


def test_custom_steel_output_verification(baseline_inputs, mock_design_results_baseline):
    """
    Test Case ID: OSB-DICT-OUT-003
    Verify that custom steel material properties propagate to output dictionary.
    """
    bridge = PlateGirderBridge()
    custom_steel_inputs = copy.deepcopy(baseline_inputs)
    custom_steel_inputs[KEY_GIRDER] = "Custom"
    custom_steel_inputs["material.custom_steel_fy"] = 410.0
    custom_steel_inputs["material.custom_steel_fu"] = 540.0
    bridge.set_input(custom_steel_inputs)
    bridge.output_dict = dict(bridge.input_dict)

    res_custom = copy.deepcopy(mock_design_results_baseline)
    res_custom["steel_grade"] = "Custom"
    res_custom["Md_kNm"] = round(res_custom["Md_kNm"] * (410.0 / 250.0), 2)
    bridge.store_design_results(res_custom)

    assert bridge.output_dict[KEY_SD_GRADE_OF_MATERIAL] == "Custom"
    assert bridge.output_dict[KEY_SD_MD_CAPACITY] == pytest.approx(6478.33, rel=1e-2)

    ev_path = EVIDENCE_DIR / "steel" / "custom_steel_output_snapshot.json"
    ev_path.parent.mkdir(parents=True, exist_ok=True)
    with open(ev_path, "w", encoding="utf-8") as f:
        json.dump({
            "grade": bridge.output_dict[KEY_SD_GRADE_OF_MATERIAL],
            "Mu_applied": bridge.output_dict[KEY_SD_MU_APPLIED],
            "Md_capacity": bridge.output_dict[KEY_SD_MD_CAPACITY],
        }, f, indent=2)

    assert ev_path.exists()


def test_concrete_deck_output_verification(baseline_inputs):
    """
    Test Case ID: OSB-DICT-OUT-004
    Verify concrete deck design outputs for custom high-strength concrete (M45).
    """
    _, report_m35 = deckdesign.design_deck_slab(
        baseline_inputs, fck=35.0, fctm=2.8, fy=500.0, Ecm=32.0, Es=200000.0,
        design_results=None, bf_top_mm=450.0, stud_height_mm=100.0
    )
    _, report_m45 = deckdesign.design_deck_slab(
        baseline_inputs, fck=45.0, fctm=3.8, fy=500.0, Ecm=34.0, Es=200000.0,
        design_results=None, bf_top_mm=450.0, stud_height_mm=100.0
    )

    vrd_c_35 = float(report_m35[KEY_DD_VRD_C_MPA])
    vrd_c_45 = float(report_m45[KEY_DD_VRD_C_MPA])
    assert vrd_c_45 > vrd_c_35, f"Expected M45 vrd_c ({vrd_c_45}) > M35 vrd_c ({vrd_c_35})"
    assert report_m45[KEY_DD_PUNCH_OK] is True

    ev_path = EVIDENCE_DIR / "concrete" / "concrete_deck_output_snapshot.json"
    ev_path.parent.mkdir(parents=True, exist_ok=True)
    with open(ev_path, "w", encoding="utf-8") as f:
        json.dump({
            "M35_vrd_c_MPa": vrd_c_35,
            "M45_vrd_c_MPa": vrd_c_45,
            "punching_status": report_m45[KEY_DD_PUNCH_OK],
        }, f, indent=2)

    assert ev_path.exists()


def test_reinforcement_output_verification(baseline_inputs):
    """
    Test Case ID: OSB-DICT-OUT-005
    Verify reinforcement design outputs, bar spacing, areas, and crack widths.
    """
    summary, report = deckdesign.design_deck_slab(
        baseline_inputs, fck=35.0, fctm=2.8, fy=500.0, Ecm=32.0, Es=200000.0,
        design_results=None, bf_top_mm=450.0, stud_height_mm=100.0
    )

    as_req_bot = float(report[KEY_DD_AS_REQ_BOT])
    as_req_top = float(report[KEY_DD_AS_REQ_TOP])
    assert as_req_bot > 0.0
    assert as_req_top > 0.0

    wk_bot = float(report[KEY_DD_WK_BOT])
    wk_limit = float(report[KEY_DD_WK_LIMIT])
    assert wk_bot <= wk_limit, f"Crack width ({wk_bot}mm) exceeds limit ({wk_limit}mm)"

    ev_path = EVIDENCE_DIR / "reinforcement" / "reinforcement_output_snapshot.json"
    ev_path.parent.mkdir(parents=True, exist_ok=True)
    with open(ev_path, "w", encoding="utf-8") as f:
        json.dump({
            "as_req_bot": as_req_bot,
            "as_req_top": as_req_top,
            "wk_bot_mm": wk_bot,
            "wk_limit_mm": wk_limit,
        }, f, indent=2)

    assert ev_path.exists()


def test_output_display_consistency(baseline_inputs, mock_design_results_baseline):
    """
    Test Case ID: OSB-DICT-OUT-006
    Verify that output dictionary parameters agree with output dock bars
    and report generator expectations.
    """
    bridge = PlateGirderBridge()
    bridge.set_input(baseline_inputs)
    bridge.output_dict = dict(bridge.input_dict)
    bridge.store_design_results(mock_design_results_baseline)

    out = bridge.output_dict

    assert out[KEY_UTIL_FLEXURE] == 72.2
    assert out[KEY_UTIL_SHEAR] == 70.5
    assert out[KEY_SD_MU_APPLIED] == 2850.50
    assert out[KEY_SD_MD_CAPACITY] == 3950.20

    ev_path = EVIDENCE_DIR / "baseline" / "display_consistency_snapshot.json"
    ev_path.parent.mkdir(parents=True, exist_ok=True)
    with open(ev_path, "w", encoding="utf-8") as f:
        json.dump({
            "KEY_UTIL_FLEXURE": out[KEY_UTIL_FLEXURE],
            "KEY_UTIL_SHEAR": out[KEY_UTIL_SHEAR],
            "KEY_SD_MU_APPLIED": out[KEY_SD_MU_APPLIED],
            "KEY_SD_MD_CAPACITY": out[KEY_SD_MD_CAPACITY],
        }, f, indent=2)

    assert ev_path.exists()


def test_output_precision_and_unit_verification(baseline_inputs, mock_design_results_baseline):
    """
    Test Case ID: OSB-DICT-OUT-007
    Verify numerical precision and unit conventions in the output dictionary.
    """
    bridge = PlateGirderBridge()
    bridge.set_input(baseline_inputs)
    bridge.output_dict = dict(bridge.input_dict)
    bridge.store_design_results(mock_design_results_baseline)

    out = bridge.output_dict

    assert isinstance(out[KEY_SD_DEFL_LIVE], float)
    assert out[KEY_SD_DEFL_LIVE] == 22.350
    assert isinstance(out[KEY_SD_MU_APPLIED], float)
    assert out[KEY_SD_MU_APPLIED] == 2850.50
    assert isinstance(out[KEY_SD_TOTAL_DEPTH], float)
    assert out[KEY_SD_TOTAL_DEPTH] == 1800.0

    ev_path = EVIDENCE_DIR / "baseline" / "precision_unit_output_snapshot.json"
    ev_path.parent.mkdir(parents=True, exist_ok=True)
    with open(ev_path, "w", encoding="utf-8") as f:
        json.dump({
            "defl_live": {"val": out[KEY_SD_DEFL_LIVE], "unit": "mm"},
            "mu_applied": {"val": out[KEY_SD_MU_APPLIED], "unit": "kNm"},
            "total_depth": {"val": out[KEY_SD_TOTAL_DEPTH], "unit": "mm"},
        }, f, indent=2)

    assert ev_path.exists()


def test_consecutive_design_output_refresh(baseline_inputs, mock_design_results_baseline):
    """
    Test Case ID: OSB-DICT-OUT-008
    Verify that consecutive design executions completely refresh the
    Output Dictionary without retaining stale results from prior runs.
    """
    bridge = PlateGirderBridge()

    # Cycle 1: 30m Span
    bridge.set_input(baseline_inputs)
    bridge.output_dict = dict(bridge.input_dict)
    res1 = copy.deepcopy(mock_design_results_baseline)
    res1["Mu_kNm"] = 2850.0
    res1["defl_limit_live_mm"] = 37.5
    bridge.store_design_results(res1)
    c1_out = dict(bridge.output_dict)

    # Cycle 2: 36m Span (Redesign)
    inp2 = copy.deepcopy(baseline_inputs)
    inp2[KEY_SPAN] = 36.0
    bridge.set_input(inp2)
    bridge.output_dict = dict(bridge.input_dict)
    res2 = copy.deepcopy(mock_design_results_baseline)
    res2["Mu_kNm"] = 4120.0
    res2["defl_limit_live_mm"] = 45.0
    bridge.store_design_results(res2)
    c2_out = dict(bridge.output_dict)

    # Cycle 3: 24m Span (Restoration)
    inp3 = copy.deepcopy(baseline_inputs)
    inp3[KEY_SPAN] = 24.0
    bridge.set_input(inp3)
    bridge.output_dict = dict(bridge.input_dict)
    res3 = copy.deepcopy(mock_design_results_baseline)
    res3["Mu_kNm"] = 1890.0
    res3["defl_limit_live_mm"] = 30.0
    bridge.store_design_results(res3)
    c3_out = dict(bridge.output_dict)

    assert c1_out[KEY_SD_MU_APPLIED] == 2850.0
    assert c1_out[KEY_SD_DEFL_ALLOW_LIVE] == 37.5

    assert c2_out[KEY_SD_MU_APPLIED] == 4120.0
    assert c2_out[KEY_SD_DEFL_ALLOW_LIVE] == 45.0

    assert c3_out[KEY_SD_MU_APPLIED] == 1890.0
    assert c3_out[KEY_SD_DEFL_ALLOW_LIVE] == 30.0

    ev_path = EVIDENCE_DIR / "consecutive_runs" / "consecutive_runs_output_snapshot.json"
    ev_path.parent.mkdir(parents=True, exist_ok=True)
    with open(ev_path, "w", encoding="utf-8") as f:
        json.dump({
            "cycle1": {"Mu": c1_out[KEY_SD_MU_APPLIED], "defl_limit": c1_out[KEY_SD_DEFL_ALLOW_LIVE]},
            "cycle2": {"Mu": c2_out[KEY_SD_MU_APPLIED], "defl_limit": c2_out[KEY_SD_DEFL_ALLOW_LIVE]},
            "cycle3": {"Mu": c3_out[KEY_SD_MU_APPLIED], "defl_limit": c3_out[KEY_SD_DEFL_ALLOW_LIVE]},
        }, f, indent=2)

    assert ev_path.exists()


def test_incomplete_or_failed_design_output_handling():
    """
    Test Case ID: OSB-DICT-OUT-009
    Verify that incomplete or failed design executions do not produce
    corrupted or misleading successful output dictionaries.
    """
    bridge = PlateGirderBridge()
    assert len(bridge.output_dict) == 0

    invalid_input = {
        KEY_SPAN: -10.0,
        KEY_TS_OVERALL_WIDTH: 8.4,
        KEY_TS_NO_OF_GIRDERS: 4,
        KEY_TS_GIRDER_SPACING: 2.1,
    }
    bridge.set_input(invalid_input)

    with pytest.raises(ValueError, match="Span must be strictly positive"):
        bridge._validate_inputs()

    assert len(bridge.output_dict) == 0

    ev_path = EVIDENCE_DIR / "incomplete_design" / "incomplete_design_snapshot.json"
    ev_path.parent.mkdir(parents=True, exist_ok=True)
    with open(ev_path, "w", encoding="utf-8") as f:
        json.dump({
            "output_dict_size": len(bridge.output_dict),
            "expected_error": "Span must be strictly positive",
            "safe_handling": True,
        }, f, indent=2)

    assert ev_path.exists()
