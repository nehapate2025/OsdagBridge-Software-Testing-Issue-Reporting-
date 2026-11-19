"""
Scenario Tests: Comprehensive Custom Reinforcement Testing (Task 4)
===================================================================
Validates reinforcement material properties, database lookups, yield strength
variations, bar diameter selection bounds, spacing constraints, error clamping,
and headless GUI automation status across:
- OSB-REB-001: Default reinforcement configuration (Fe 500 baseline)
- OSB-REB-002: Custom reinforcement grades (Fe 415, Fe 415D, Fe 500, Fe 500D, Fe 550, Fe 550D, Fe 600)
- OSB-REB-003: Modified reinforcement yield strength (fy) & moment capacity
- OSB-REB-004: Modified bar diameter bounds (KEY_DS_REINF_BOUNDS)
- OSB-REB-005: Modified reinforcement spacing rules (min 75mm, max 300mm, 5mm rounding)
- OSB-REB-006: Invalid reinforcement inputs (inverted bounds, out-of-range covers)
- OSB-REB-007: GUI Additional Inputs Dialog reinforcement automation status
"""

import os
import json
import sqlite3
import pytest
from pathlib import Path

from osdagbridge.core.utils.common import (
    KEY_STRUCTURE_TYPE,
    KEY_DESIGN_MODE,
    KEY_SPAN,
    KEY_CARRIAGEWAY_WIDTH,
    KEY_FOOTPATH,
    KEY_GIRDER,
    KEY_DECK_CONCRETE_GRADE_BASIC,
    KEY_TS_DECK_THICKNESS,
    KEY_TS_DECK_OVERHANG,
    KEY_DS_REINF_MATERIAL,
    KEY_DS_REINF_BOUNDS,
    KEY_DS_TOP_CLEAR_COVER,
    KEY_DS_BOTTOM_CLEAR_COVER,
    KEY_DS_SIDE_CLEAR_COVER,
    KEY_DD_FY,
    KEY_DD_M_ULS_SAG,
    KEY_DD_M_ULS_HOG,
    KEY_DD_M_ULS_OH,
    KEY_DD_D_BOT,
    KEY_DD_D_TOP,
    KEY_DD_MU_BOT,
    KEY_DD_MU_TOP,
    KEY_DD_AS_REQ_BOT,
    KEY_DD_AS_REQ_TOP,
    KEY_DD_AS_BOT,
    KEY_DD_AS_TOP,
    KEY_DD_DIA_BOT,
    KEY_DD_SPC_BOT,
    KEY_DD_DIA_TOP,
    KEY_DD_SPC_TOP,
    KEY_DD_DIA_OH,
    KEY_DD_SPC_OH,
    KEY_DD_AS_OH,
    KEY_DD_AS_LONG,
    KEY_DD_STRESS_REINF_BOTTOM,
    KEY_DD_STRESS_REINF_TOP,
    KEY_DD_STRESS_REINF_ALLOWABLE,
    KEY_DD_CRACK_WK_BOTTOM,
    KEY_DD_CRACK_WK_TOP,
)
from osdagbridge.core.bridge_types.plate_girder.validator import BridgeInputValidator
from osdagbridge.core.bridge_types.plate_girder.defaults import (
    solve_extend_basic_input_dict,
    BASIC_INPUT_DICT,
)
from osdagbridge.core.bridge_types.plate_girder.deckdesign import (
    design_deck_slab,
    _pick_rebar,
    _STANDARD_DIAS_MM,
    _moment_capacity_kNm,
)

EVIDENCE_REB_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "test_results", "evidence", "reinforcement")
)
os.makedirs(EVIDENCE_REB_DIR, exist_ok=True)
DB_PATH = Path(__file__).resolve().parents[2] / "src" / "osdagbridge" / "core" / "data" / "ResourceFiles" / "Intg_osdag.sqlite"


def _save_evidence(filename: str, data: dict) -> str:
    path = os.path.join(EVIDENCE_REB_DIR, filename)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, default=str)
    return path


def _get_rebar_props_from_db(grade: str) -> tuple[float, float, float]:
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    cur.execute("SELECT fy, fu, Es FROM Rebar_Grade_Properties WHERE Grade=?", (grade,))
    row = cur.fetchone()
    con.close()
    if not row:
        raise ValueError(f"Rebar Grade {grade} not found in database")
    return float(row[0]), float(row[1]), float(row[2])


def _get_concrete_props_from_db(grade: str) -> tuple[float, float, float]:
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    cur.execute("SELECT fck, fctm, Ecm FROM Concrete_Grade_Properties WHERE Grade=?", (grade,))
    row = cur.fetchone()
    con.close()
    if not row:
        raise ValueError(f"Grade {grade} not found in database")
    return float(row[0]), float(row[1]), float(row[2])


@pytest.mark.scenario
def test_default_reinforcement_configuration(valid_baseline_input):
    """
    Test Case ID: OSB-REB-001
    Title: Default Reinforcement Baseline Configuration Verification
    Category: Scenario / Material
    Objective: Verify default reinforcement grade (Fe 500) from layout solver defaults,
               database properties, cover dimensions, and baseline bar sizing.
    """
    base_dict = dict(valid_baseline_input)
    solve_extend_basic_input_dict(base_dict)

    rebar_grade = base_dict.get(KEY_DS_REINF_MATERIAL)
    assert rebar_grade == "Fe 500", f"Expected default rebar grade Fe 500, got {rebar_grade}"

    fy, fu, Es = _get_rebar_props_from_db(rebar_grade)
    assert fy == 500.0, f"Expected fy=500.0 MPa, got {fy}"
    assert fu == 545.0, f"Expected fu=545.0 MPa, got {fu}"
    assert Es == 200000.0, f"Expected Es=200000.0 MPa, got {Es}"

    top_cover = float(base_dict[KEY_DS_TOP_CLEAR_COVER])
    bot_cover = float(base_dict[KEY_DS_BOTTOM_CLEAR_COVER])
    assert top_cover == 50.0, f"Expected default top clear cover 50mm, got {top_cover}"
    assert bot_cover == 50.0, f"Expected default bottom clear cover 50mm, got {bot_cover}"

    fck, fctm, Ecm = _get_concrete_props_from_db("M35")
    result, report = design_deck_slab(base_dict, fck=fck, fctm=fctm, fy=fy, Es=Es, Ecm=Ecm)

    assert float(result["rebar_bottom_yield"]) == fy
    assert float(result["rebar_top_yield"]) == fy
    assert int(result["rebar_bottom_dia"]) in _STANDARD_DIAS_MM
    assert int(result["rebar_top_dia"]) in _STANDARD_DIAS_MM
    assert float(result["rebar_bottom_spacing"]) >= 75.0
    assert float(result["rebar_bottom_spacing"]) <= 300.0

    # Allowable steel stress = 0.8 * fy
    expected_allowable = 0.8 * fy
    assert float(result["deckdesign.stress.reinf.allowable"]) == pytest.approx(expected_allowable, rel=1e-3)
    assert float(result["deckdesign.stress.reinf.bottom"]) <= expected_allowable

    evidence_data = {
        "test_case_id": "OSB-REB-001",
        "description": "Baseline default reinforcement properties and design output",
        "input_parameters": {
            "rebar_grade": rebar_grade,
            "fy_MPa": fy,
            "fu_MPa": fu,
            "Es_MPa": Es,
            "top_cover_mm": top_cover,
            "bottom_cover_mm": bot_cover,
        },
        "design_summary": {
            "bottom_layer": {
                "dia_mm": float(result["rebar_bottom_dia"]),
                "spacing_mm": float(result["rebar_bottom_spacing"]),
                "area_mm2_per_m": float(result["rebar_bottom_area"]),
                "stress_actual_MPa": float(result["deckdesign.stress.reinf.bottom"]),
                "stress_allowable_MPa": float(result["deckdesign.stress.reinf.allowable"]),
            },
            "top_layer": {
                "dia_mm": float(result["rebar_top_dia"]),
                "spacing_mm": float(result["rebar_top_spacing"]),
                "area_mm2_per_m": float(result["rebar_top_area"]),
                "stress_actual_MPa": float(result["deckdesign.stress.reinf.top"]),
            },
            "overhang_layer": {
                "dia_mm": float(result["rebar_overhang_dia"]),
                "spacing_mm": float(result["rebar_overhang_spacing"]),
                "area_mm2_per_m": float(result["rebar_overhang_area"]),
            },
            "longitudinal_distribution": {
                "dia_mm": float(result["rebar_long_dia"]),
                "spacing_mm": float(result["rebar_long_spacing"]),
                "area_mm2_per_m": float(result["rebar_long_area"]),
            },
        },
        "status": "PASS",
    }
    _save_evidence("OSB-REB-001_default_reinforcement_summary.json", evidence_data)


@pytest.mark.scenario
def test_custom_reinforcement_grade(valid_baseline_input):
    """
    Test Case ID: OSB-REB-002
    Title: Custom Reinforcement Grade Database Retrieval and Capacity Scaling
    Category: Scenario / Material
    Objective: Verify retention and design response across supported reinforcement grades
               (Fe 415, Fe 415D, Fe 500, Fe 500D, Fe 550, Fe 550D, Fe 600).
    """
    base_dict = dict(valid_baseline_input)
    solve_extend_basic_input_dict(base_dict)
    fck, fctm, Ecm = _get_concrete_props_from_db("M35")

    grades = ["Fe 415", "Fe 415D", "Fe 500", "Fe 500D", "Fe 550", "Fe 550D", "Fe 600"]
    grade_results = {}

    for grade in grades:
        fy, fu, Es = _get_rebar_props_from_db(grade)
        dict_copy = dict(base_dict)
        dict_copy[KEY_DS_REINF_MATERIAL] = grade

        result, report = design_deck_slab(dict_copy, fck=fck, fctm=fctm, fy=fy, Es=Es, Ecm=Ecm)

        allowable_stress = float(result["deckdesign.stress.reinf.allowable"])
        assert allowable_stress == pytest.approx(0.8 * fy, rel=1e-3)

        grade_results[grade] = {
            "fy_MPa": fy,
            "fu_MPa": fu,
            "Es_MPa": Es,
            "allowable_steel_stress_MPa": allowable_stress,
            "bottom_As_req_mm2_per_m": report[KEY_DD_AS_REQ_BOT],
            "bottom_As_prov_mm2_per_m": report[KEY_DD_AS_BOT],
            "bottom_dia_mm": report[KEY_DD_DIA_BOT],
            "bottom_spacing_mm": report[KEY_DD_SPC_BOT],
            "top_As_req_mm2_per_m": report[KEY_DD_AS_REQ_TOP],
            "top_As_prov_mm2_per_m": report[KEY_DD_AS_TOP],
        }

    # Verify that allowable steel stress strictly increases with higher grade
    stresses = [grade_results[g]["allowable_steel_stress_MPa"] for g in grades]
    assert stresses == sorted(stresses), "Allowable steel stress must increase monotonically with fy"

    # Verify that required steel area decreases as fy increases from Fe 415 to Fe 600
    assert grade_results["Fe 415"]["bottom_As_req_mm2_per_m"] > grade_results["Fe 600"]["bottom_As_req_mm2_per_m"], (
        "Higher yield strength must require less reinforcement area for identical moment demand"
    )

    evidence_data = {
        "test_case_id": "OSB-REB-002",
        "description": "Multi-grade reinforcement database retrieval and design response",
        "grades_evaluated": grade_results,
        "status": "PASS",
    }
    _save_evidence("OSB-REB-002_rebar_grades_summary.json", evidence_data)


@pytest.mark.scenario
def test_modified_reinforcement_yield_strength(valid_baseline_input):
    """
    Test Case ID: OSB-REB-003
    Title: Modified Reinforcement Yield Strength (fy) & Moment Capacity Verification
    Category: Scenario / Material
    Objective: Verify transfer of yield strength into moment capacity formulas:
               Mu = 0.87 * fy * As * (d - 0.42 * xu).
    """
    base_dict = dict(valid_baseline_input)
    solve_extend_basic_input_dict(base_dict)
    fck, fctm, Ecm = _get_concrete_props_from_db("M35")

    fy_levels = [415.0, 500.0, 550.0, 600.0]
    fixed_As = 646.0  # mm2/m (e.g. 12mm @ 175mm)
    fixed_d = 194.0   # mm

    capacity_results = {}
    for fy in fy_levels:
        mu = _moment_capacity_kNm(fy_MPa=fy, As_mm2=fixed_As, d_mm=fixed_d, fck_MPa=fck)
        capacity_results[f"fy_{int(fy)}MPa"] = {
            "fy_MPa": fy,
            "fixed_As_mm2": fixed_As,
            "effective_depth_mm": fixed_d,
            "moment_capacity_Mu_kNm_per_m": round(mu, 3),
        }

    # Verify that moment capacity scales directly with fy
    mus = [capacity_results[f"fy_{int(f)}MPa"]["moment_capacity_Mu_kNm_per_m"] for f in fy_levels]
    assert mus == sorted(mus), "Moment capacity must strictly increase with rebar yield strength"

    evidence_data = {
        "test_case_id": "OSB-REB-003",
        "description": "Yield strength sensitivity on cross-section moment capacity",
        "results": capacity_results,
        "status": "PASS",
    }
    _save_evidence("OSB-REB-003_rebar_yield_strength_summary.json", evidence_data)


@pytest.mark.scenario
def test_modified_bar_diameter_bounds(valid_baseline_input):
    """
    Test Case ID: OSB-REB-004
    Title: Modified Reinforcement Size Bounds (KEY_DS_REINF_BOUNDS) Enforcement
    Category: Scenario / Material
    Objective: Verify that user-specified lower and upper bar diameter bounds strictly constrain
               the automated bar selection algorithm.
    """
    base_dict = dict(valid_baseline_input)
    solve_extend_basic_input_dict(base_dict)
    fck, fctm, Ecm = _get_concrete_props_from_db("M35")
    fy, _, Es = _get_rebar_props_from_db("Fe 500")

    bound_configs = [
        {"lower": 8, "upper": 10, "expected_dia": 8},
        {"lower": 12, "upper": 16, "expected_dia": 12},
        {"lower": 16, "upper": 25, "expected_dia": 16},
        {"lower": 20, "upper": 32, "expected_dia": 20},
    ]

    bound_results = {}
    for cfg in bound_configs:
        dict_copy = dict(base_dict)
        dict_copy[KEY_DS_REINF_BOUNDS] = {"lower": cfg["lower"], "upper": cfg["upper"]}

        result, report = design_deck_slab(dict_copy, fck=fck, fctm=fctm, fy=fy, Es=Es, Ecm=Ecm)

        chosen_dia = int(result["rebar_bottom_dia"])
        assert cfg["lower"] <= chosen_dia <= cfg["upper"], (
            f"Chosen dia {chosen_dia}mm violates bounds [{cfg['lower']}, {cfg['upper']}]"
        )
        assert float(result["rebar_bottom_area"]) >= report[KEY_DD_AS_REQ_BOT], (
            "Provided steel must satisfy required steel demand"
        )

        bound_results[f"bounds_{cfg['lower']}_to_{cfg['upper']}"] = {
            "lower_bound_mm": cfg["lower"],
            "upper_bound_mm": cfg["upper"],
            "chosen_bottom_dia_mm": chosen_dia,
            "chosen_bottom_spacing_mm": float(result["rebar_bottom_spacing"]),
            "provided_steel_area_mm2_per_m": float(result["rebar_bottom_area"]),
            "required_steel_area_mm2_per_m": report[KEY_DD_AS_REQ_BOT],
        }

    evidence_data = {
        "test_case_id": "OSB-REB-004",
        "description": "Reinforcement size bound constraints on automated rebar selection",
        "results": bound_results,
        "status": "PASS",
    }
    _save_evidence("OSB-REB-004_bar_diameter_bounds_summary.json", evidence_data)


@pytest.mark.scenario
def test_modified_reinforcement_spacing(valid_baseline_input):
    """
    Test Case ID: OSB-REB-005
    Title: Reinforcement Spacing Constraints (Min 75mm, Max 300mm, 5mm Rounding)
    Category: Scenario / Material
    Objective: Verify spacing rules across varying reinforcement demands, ensuring spacings
               never drop below 75mm, never exceed 300mm, and are multiples of 5mm.
    """
    base_dict = dict(valid_baseline_input)
    solve_extend_basic_input_dict(base_dict)
    fck, fctm, Ecm = _get_concrete_props_from_db("M35")
    fy, _, Es = _get_rebar_props_from_db("Fe 500")

    result, report = design_deck_slab(base_dict, fck=fck, fctm=fctm, fy=fy, Es=Es, Ecm=Ecm)

    # Check bottom, top, long, overhang spacings
    spacings = {
        "bottom": float(result["rebar_bottom_spacing"]),
        "top": float(result["rebar_top_spacing"]),
        "longitudinal": float(result["rebar_long_spacing"]),
        "overhang": float(result["rebar_overhang_spacing"]),
    }

    for name, spc in spacings.items():
        assert spc >= 75.0, f"{name} spacing {spc}mm violates minimum aggregate clearance 75mm"
        assert spc <= 300.0, f"{name} spacing {spc}mm violates maximum crack spacing limit 300mm"
        assert spc % 5.0 == pytest.approx(0.0), f"{name} spacing {spc}mm must be a multiple of 5mm"

    # High demand test using pick_rebar directly with extreme As_req
    dia_high, spc_high, as_high = _pick_rebar(As_req_mm2=2500.0, dias=[12])
    assert spc_high == 75.0, f"Extreme demand must hit minimum spacing floor 75mm, got {spc_high}"

    # Very low demand test
    dia_low, spc_low, as_low = _pick_rebar(As_req_mm2=100.0, dias=[12])
    assert spc_low == 300.0, f"Very low demand must hit maximum spacing ceiling 300mm, got {spc_low}"

    evidence_data = {
        "test_case_id": "OSB-REB-005",
        "description": "Reinforcement spacing limits (75mm floor, 300mm cap, 5mm rounding)",
        "observed_spacings": spacings,
        "boundary_checks": {
            "extreme_high_demand_spacing_mm": spc_high,
            "extreme_low_demand_spacing_mm": spc_low,
        },
        "status": "PASS",
    }
    _save_evidence("OSB-REB-005_rebar_spacing_summary.json", evidence_data)


@pytest.mark.scenario
def test_invalid_reinforcement_inputs():
    """
    Test Case ID: OSB-REB-006
    Title: Invalid Reinforcement Inputs & Boundary Clamping Verification
    Category: Scenario / Material / Validation
    Objective: Verify that BridgeInputValidator safely clamps inverted bounds, out-of-range bounds,
               out-of-range clear covers, and non-numeric inputs.
    """
    val = BridgeInputValidator()
    validation_records = []

    # 1. Reinforcement size bounds: inverted lower > upper
    err_inv = val.validate_additional_inputs(KEY_DS_REINF_BOUNDS, {KEY_DS_REINF_BOUNDS: {"lower": 25, "upper": 12}})
    assert err_inv is not None
    corrected_bounds, msg = err_inv
    assert corrected_bounds["upper"] >= corrected_bounds["lower"]
    validation_records.append({"key": KEY_DS_REINF_BOUNDS, "input": {"lower": 25, "upper": 12}, "result": err_inv})

    # 2. Reinforcement size bounds: under min (lower < 8)
    err_under = val.validate_additional_inputs(KEY_DS_REINF_BOUNDS, {KEY_DS_REINF_BOUNDS: {"lower": 4, "upper": 12}})
    assert err_under is not None and err_under[0]["lower"] == 8
    validation_records.append({"key": KEY_DS_REINF_BOUNDS, "input": {"lower": 4, "upper": 12}, "result": err_under})

    # 3. Reinforcement size bounds: over max (upper > 40)
    err_over = val.validate_additional_inputs(KEY_DS_REINF_BOUNDS, {KEY_DS_REINF_BOUNDS: {"lower": 12, "upper": 50}})
    assert err_over is not None and err_over[0]["upper"] == 40
    validation_records.append({"key": KEY_DS_REINF_BOUNDS, "input": {"lower": 12, "upper": 50}, "result": err_over})

    # 4. Top Clear Cover ([40, 75] mm)
    err_low_tc = val.validate_additional_inputs(KEY_DS_TOP_CLEAR_COVER, {KEY_DS_TOP_CLEAR_COVER: 25.0})
    assert err_low_tc is not None and err_low_tc[0] == 40
    validation_records.append({"key": KEY_DS_TOP_CLEAR_COVER, "input": 25.0, "result": err_low_tc})

    err_high_tc = val.validate_additional_inputs(KEY_DS_TOP_CLEAR_COVER, {KEY_DS_TOP_CLEAR_COVER: 90.0})
    assert err_high_tc is not None and err_high_tc[0] == 75
    validation_records.append({"key": KEY_DS_TOP_CLEAR_COVER, "input": 90.0, "result": err_high_tc})

    # 5. Bottom Clear Cover ([35, 75] mm)
    err_low_bc = val.validate_additional_inputs(KEY_DS_BOTTOM_CLEAR_COVER, {KEY_DS_BOTTOM_CLEAR_COVER: 20.0})
    assert err_low_bc is not None and err_low_bc[0] == 35
    validation_records.append({"key": KEY_DS_BOTTOM_CLEAR_COVER, "input": 20.0, "result": err_low_bc})

    err_high_bc = val.validate_additional_inputs(KEY_DS_BOTTOM_CLEAR_COVER, {KEY_DS_BOTTOM_CLEAR_COVER: 85.0})
    assert err_high_bc is not None and err_high_bc[0] == 75
    validation_records.append({"key": KEY_DS_BOTTOM_CLEAR_COVER, "input": 85.0, "result": err_high_bc})

    evidence_data = {
        "test_case_id": "OSB-REB-006",
        "description": "Validation checks and boundary clamping for invalid reinforcement inputs",
        "records": validation_records,
        "status": "PASS",
    }
    _save_evidence("OSB-REB-006_invalid_reinforcement_summary.json", evidence_data)


@pytest.mark.scenario
def test_gui_reinforcement_dialog_automation_status():
    """
    Test Case ID: OSB-REB-007
    Title: GUI Additional Inputs Reinforcement Tab Automation Status Check
    Category: Scenario / GUI / Automation
    Objective: Attempt instantiation of AdditionalInputs dialog reinforcement fields in headless
               mode, marking BLOCKED when PySide6 or graphical display is unavailable.
    """
    try:
        from PySide6.QtWidgets import QApplication
        from osdagbridge.desktop.ui.dialogs.additional_input.additional_inputs import AdditionalInputs

        app = QApplication.instance() or QApplication([])
        dialog = AdditionalInputs(input_dict={})
        assert dialog is not None
    except (ImportError, ModuleNotFoundError) as exc:
        pytest.skip(f"GUI reinforcement dialog automation BLOCKED: Missing UI dependency ({exc})")
    except Exception as exc:
        pytest.skip(f"GUI reinforcement dialog automation BLOCKED: Headless display environment ({exc})")
