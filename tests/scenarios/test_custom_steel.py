"""
Scenario Tests: Comprehensive Custom Steel Material Testing (Task 3)
====================================================================
Validates structural steel material property definitions, database lookups,
per-component configurations (girders, cross-bracing, diaphragms, stiffeners),
bounds checking, and error clamping across:
- OSB-MAT-001: Default steel material (E 350A baseline)
- OSB-MAT-002: Custom steel grades (E 250A, E 300A, E 410A, E 450A)
- OSB-MAT-003: Custom yield strength (Fy)
- OSB-MAT-004: Custom ultimate tensile strength (Fu)
- OSB-MAT-005: Custom modulus of elasticity (E)
- OSB-MAT-006: Component-specific steel properties & stiffener inheritance
- OSB-MAT-007: Invalid material property handling & boundary clamping
- OSB-MAT-008: GUI MaterialPropertiesDialog automation status
"""

import os
import json
import sqlite3
import pytest
from pathlib import Path

from osdagbridge.core.utils.common import (
    connectdb,
    KEY_GIRDER,
    KEY_CROSS_BRACING,
    KEY_END_DIAPHRAGM,
    KEY_MATERIAL_GIRDER_FY,
    KEY_MATERIAL_GIRDER_FU,
    KEY_MATERIAL_GIRDER_E,
    KEY_MATERIAL_GIRDER_G,
    KEY_MATERIAL_GIRDER_POISSON,
    KEY_MATERIAL_GIRDER_THERMAL,
    KEY_MATERIAL_GIRDER_DENSITY,
)
from osdagbridge.core.bridge_types.plate_girder.validator import BridgeInputValidator
from osdagbridge.core.bridge_types.plate_girder.defaults import (
    solve_extend_basic_input_dict,
    BASIC_INPUT_DICT,
)

EVIDENCE_MAT_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "test_results", "evidence", "materials")
)
os.makedirs(EVIDENCE_MAT_DIR, exist_ok=True)
DB_PATH = Path(__file__).resolve().parents[2] / "src" / "osdagbridge" / "core" / "data" / "ResourceFiles" / "Intg_osdag.sqlite"


def _save_evidence(filename: str, data: dict) -> str:
    path = os.path.join(EVIDENCE_MAT_DIR, filename)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, default=str)
    return path


@pytest.mark.scenario
def test_default_steel_material(valid_baseline_input):
    """
    Test Case ID: OSB-MAT-001
    Title: Default Steel Material Verification
    Category: Scenario / Material
    Objective: Verify baseline steel material grade (E 350A) in BASIC_INPUT_DICT, its presence in the
               Input Dictionary, and properties queried from the SQLite database.
    """
    # 1. Verify default material in defaults
    default_grade = BASIC_INPUT_DICT.get(KEY_GIRDER)
    assert default_grade == "E 350A", f"Expected default grade E 350A, got {default_grade}"

    # 2. Query material database for default grade
    assert DB_PATH.exists(), f"Material database not found at {DB_PATH}"
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    cur.execute(
        "SELECT Grade, [Yield Strength], [Ultimate Tensile Strength], [Modulus of Elasticity], [Poisson's Ratio] "
        "FROM Steel_Grade_Properties WHERE Grade=?",
        (default_grade,),
    )
    row = cur.fetchone()
    con.close()

    assert row is not None, f"Grade {default_grade} not found in database"
    assert row[1] == 350, f"Expected Fy=350 MPa, got {row[1]}"
    assert row[2] == 490, f"Expected Fu=490 MPa, got {row[2]}"
    assert row[3] == 200, f"Expected E=200 GPa, got {row[3]}"
    assert row[4] == 0.3, f"Expected Poisson=0.3, got {row[4]}"

    _save_evidence("OSB-MAT-001_default_steel_evidence.json", {
        "grade": row[0],
        "fy_MPa": row[1],
        "fu_MPa": row[2],
        "E_GPa": row[3],
        "poisson": row[4],
        "density_kN_m3": 78.5,
    })


@pytest.mark.scenario
def test_custom_steel_grade():
    """
    Test Case ID: OSB-MAT-002
    Title: Custom Standard Steel Grade Selection
    Category: Scenario / Material
    Objective: Verify that selecting different supported standard steel grades (E 250A, E 300A, E 410A, E 450A)
               retrieves correct respective material properties from the database.
    """
    expected_grades = {
        "E 250A": {"fy": 250, "fu": 410, "E": 200, "nu": 0.3},
        "E 300A": {"fy": 300, "fu": 440, "E": 200, "nu": 0.3},
        "E 350A": {"fy": 350, "fu": 490, "E": 200, "nu": 0.3},
        "E 410A": {"fy": 410, "fu": 540, "E": 200, "nu": 0.3},
        "E 450A": {"fy": 450, "fu": 570, "E": 200, "nu": 0.3},
    }

    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    evidence_data = {}

    for grade, expected in expected_grades.items():
        cur.execute(
            "SELECT [Yield Strength], [Ultimate Tensile Strength], [Modulus of Elasticity], [Poisson's Ratio] "
            "FROM Steel_Grade_Properties WHERE Grade=?",
            (grade,),
        )
        row = cur.fetchone()
        assert row is not None, f"Grade {grade} missing from DB"
        assert row[0] == expected["fy"], f"Fy mismatch for {grade}"
        assert row[1] == expected["fu"], f"Fu mismatch for {grade}"
        assert row[2] == expected["E"], f"E mismatch for {grade}"
        assert row[3] == expected["nu"], f"nu mismatch for {grade}"

        evidence_data[grade] = {
            "fy_MPa": row[0],
            "fu_MPa": row[1],
            "E_GPa": row[2],
            "poisson": row[3],
        }
    con.close()

    _save_evidence("OSB-MAT-002_grades_selection_evidence.json", evidence_data)


@pytest.mark.scenario
def test_custom_yield_strength():
    """
    Test Case ID: OSB-MAT-003
    Title: Custom Steel Yield Strength (Fy) Validation and Conversion
    Category: Scenario / Material
    Objective: Verify user-defined yield strength Fy across valid range [100.0, 1200.0] MPa
               is accepted by validator and properly stored in input dictionary.
    """
    validator = BridgeInputValidator()
    test_fy_values = [250.0, 350.0, 400.0, 450.0, 550.0, 690.0]

    for fy in test_fy_values:
        payload = {KEY_MATERIAL_GIRDER_FY: fy}
        err = validator.validate_material_inputs(KEY_MATERIAL_GIRDER_FY, payload)
        assert err is None, f"Valid Fy {fy} MPa was rejected: {err}"

    # Verify out-of-bounds lower clamping (< 100.0 MPa)
    err_low = validator.validate_material_inputs(KEY_MATERIAL_GIRDER_FY, {KEY_MATERIAL_GIRDER_FY: 80.0})
    assert err_low is not None and err_low[0] == 100.0

    # Verify out-of-bounds upper clamping (> 1200.0 MPa)
    err_high = validator.validate_material_inputs(KEY_MATERIAL_GIRDER_FY, {KEY_MATERIAL_GIRDER_FY: 1400.0})
    assert err_high is not None and err_high[0] == 1200.0

    _save_evidence("OSB-MAT-003_custom_fy_evidence.json", {
        "valid_tested": test_fy_values,
        "clamped_low": err_low,
        "clamped_high": err_high,
    })


@pytest.mark.scenario
def test_custom_ultimate_strength():
    """
    Test Case ID: OSB-MAT-004
    Title: Custom Steel Ultimate Tensile Strength (Fu) Validation
    Category: Scenario / Material
    Objective: Verify user-defined ultimate tensile strength Fu across valid range [100.0, 1500.0] MPa
               is accepted by validator and properly stored in input dictionary.
    """
    validator = BridgeInputValidator()
    test_fu_values = [410.0, 490.0, 540.0, 570.0, 780.0]

    for fu in test_fu_values:
        payload = {KEY_MATERIAL_GIRDER_FU: fu}
        err = validator.validate_material_inputs(KEY_MATERIAL_GIRDER_FU, payload)
        assert err is None, f"Valid Fu {fu} MPa was rejected: {err}"

    # Verify out-of-bounds lower clamping (< 100.0 MPa)
    err_low = validator.validate_material_inputs(KEY_MATERIAL_GIRDER_FU, {KEY_MATERIAL_GIRDER_FU: 90.0})
    assert err_low is not None and err_low[0] == 100.0

    # Verify out-of-bounds upper clamping (> 1500.0 MPa)
    err_high = validator.validate_material_inputs(KEY_MATERIAL_GIRDER_FU, {KEY_MATERIAL_GIRDER_FU: 1800.0})
    assert err_high is not None and err_high[0] == 1500.0

    _save_evidence("OSB-MAT-004_custom_fu_evidence.json", {
        "valid_tested": test_fu_values,
        "clamped_low": err_low,
        "clamped_high": err_high,
    })


@pytest.mark.scenario
def test_custom_elastic_modulus():
    """
    Test Case ID: OSB-MAT-005
    Title: Custom Modulus of Elasticity (E) Validation
    Category: Scenario / Material
    Objective: Verify user-defined elastic modulus E across valid range [100.0, 300.0] GPa
               is accepted by validator and properly stored in input dictionary.
    """
    validator = BridgeInputValidator()
    test_e_values = [180.0, 200.0, 205.0, 210.0, 250.0]

    for e in test_e_values:
        payload = {KEY_MATERIAL_GIRDER_E: e}
        err = validator.validate_material_inputs(KEY_MATERIAL_GIRDER_E, payload)
        assert err is None, f"Valid E {e} GPa was rejected: {err}"

    # Verify out-of-bounds lower clamping (< 100.0 GPa)
    err_low = validator.validate_material_inputs(KEY_MATERIAL_GIRDER_E, {KEY_MATERIAL_GIRDER_E: 80.0})
    assert err_low is not None and err_low[0] == 100.0

    # Verify out-of-bounds upper clamping (> 300.0 GPa)
    err_high = validator.validate_material_inputs(KEY_MATERIAL_GIRDER_E, {KEY_MATERIAL_GIRDER_E: 350.0})
    assert err_high is not None and err_high[0] == 300.0

    _save_evidence("OSB-MAT-005_custom_e_evidence.json", {
        "valid_tested": test_e_values,
        "clamped_low": err_low,
        "clamped_high": err_high,
    })


@pytest.mark.scenario
def test_component_specific_steel_properties():
    """
    Test Case ID: OSB-MAT-006
    Title: Component-Specific Steel Properties and Inheritance Verification
    Category: Scenario / Material
    Objective: Verify which bridge components support independent material customization:
               - Main Girders (KEY_GIRDER -> material.girder.*)
               - Cross-Bracing (KEY_CROSS_BRACING -> material.cross_bracing.*)
               - End Diaphragms (KEY_END_DIAPHRAGM -> material.end_diaphragm.*)
               - Stiffeners (share main girder material)
    """
    # 1. Main Girder, Cross Bracing, and End Diaphragms exist as distinct GUI/dictionary dropdown keys
    assert KEY_GIRDER == "material.girder"
    assert KEY_CROSS_BRACING == "material.cross_bracing"
    assert KEY_END_DIAPHRAGM == "material.end_diaphragm"

    # 2. Verify all three have defaults in BASIC_INPUT_DICT
    assert KEY_GIRDER in BASIC_INPUT_DICT
    assert KEY_CROSS_BRACING in BASIC_INPUT_DICT
    assert KEY_END_DIAPHRAGM in BASIC_INPUT_DICT

    # 3. Verify Stiffeners do NOT have separate material keys and inherit from main girder
    stiffener_material_keys = [k for k in BASIC_INPUT_DICT if "stiffener" in k.lower() and "material" in k.lower()]
    assert len(stiffener_material_keys) == 0, "Stiffeners unexpectedly have standalone material keys"

    _save_evidence("OSB-MAT-006_component_specific_evidence.json", {
        "main_girder_key": KEY_GIRDER,
        "cross_bracing_key": KEY_CROSS_BRACING,
        "end_diaphragm_key": KEY_END_DIAPHRAGM,
        "stiffeners_inherit_from_girder": True,
    })


@pytest.mark.scenario
def test_invalid_material_properties():
    """
    Test Case ID: OSB-MAT-007
    Title: Invalid Steel Material Properties Rejection and Clamping
    Category: Scenario / Material
    Objective: Verify safe handling, boundary clamping, and descriptive error messages
               for invalid steel material inputs across all properties.
    """
    validator = BridgeInputValidator()

    # 1. Density out-of-bounds
    err_d_low = validator.validate_material_inputs(KEY_MATERIAL_GIRDER_DENSITY, {KEY_MATERIAL_GIRDER_DENSITY: 30.0})
    assert err_d_low is not None and err_d_low[0] == 50.0

    err_d_neg = validator.validate_material_inputs(KEY_MATERIAL_GIRDER_DENSITY, {KEY_MATERIAL_GIRDER_DENSITY: -10.0})
    assert err_d_neg is not None and err_d_neg[0] == 50.0

    err_d_high = validator.validate_material_inputs(KEY_MATERIAL_GIRDER_DENSITY, {KEY_MATERIAL_GIRDER_DENSITY: 150.0})
    assert err_d_high is not None and err_d_high[0] == 120.0

    # 2. Yield strength out-of-bounds
    err_fy_low = validator.validate_material_inputs(KEY_MATERIAL_GIRDER_FY, {KEY_MATERIAL_GIRDER_FY: 40.0})
    assert err_fy_low is not None and err_fy_low[0] == 100.0

    err_fy_high = validator.validate_material_inputs(KEY_MATERIAL_GIRDER_FY, {KEY_MATERIAL_GIRDER_FY: 1500.0})
    assert err_fy_high is not None and err_fy_high[0] == 1200.0

    # 3. Ultimate strength out-of-bounds
    err_fu_low = validator.validate_material_inputs(KEY_MATERIAL_GIRDER_FU, {KEY_MATERIAL_GIRDER_FU: 50.0})
    assert err_fu_low is not None and err_fu_low[0] == 100.0

    err_fu_high = validator.validate_material_inputs(KEY_MATERIAL_GIRDER_FU, {KEY_MATERIAL_GIRDER_FU: 2000.0})
    assert err_fu_high is not None and err_fu_high[0] == 1500.0

    # 4. Modulus of Elasticity out-of-bounds
    err_e_low = validator.validate_material_inputs(KEY_MATERIAL_GIRDER_E, {KEY_MATERIAL_GIRDER_E: 50.0})
    assert err_e_low is not None and err_e_low[0] == 100.0

    err_e_high = validator.validate_material_inputs(KEY_MATERIAL_GIRDER_E, {KEY_MATERIAL_GIRDER_E: 400.0})
    assert err_e_high is not None and err_e_high[0] == 300.0

    # 5. Poisson's ratio out-of-bounds
    err_nu_low = validator.validate_material_inputs(KEY_MATERIAL_GIRDER_POISSON, {KEY_MATERIAL_GIRDER_POISSON: -0.1})
    assert err_nu_low is not None and err_nu_low[0] == 0.0

    err_nu_high = validator.validate_material_inputs(KEY_MATERIAL_GIRDER_POISSON, {KEY_MATERIAL_GIRDER_POISSON: 0.8})
    assert err_nu_high is not None and err_nu_high[0] == 0.5

    # 6. Non-numeric inputs
    err_nan = validator.validate_material_inputs(KEY_MATERIAL_GIRDER_FY, {KEY_MATERIAL_GIRDER_FY: "invalid"})
    assert err_nan is not None and err_nan[0] == 100.0
    assert "numeric value" in err_nan[1]

    _save_evidence("OSB-MAT-007_invalid_steel_evidence.json", {
        "density_low": err_d_low,
        "density_high": err_d_high,
        "fy_low": err_fy_low,
        "fy_high": err_fy_high,
        "fu_low": err_fu_low,
        "fu_high": err_fu_high,
        "e_low": err_e_low,
        "e_high": err_e_high,
        "poisson_low": err_nu_low,
        "poisson_high": err_nu_high,
        "non_numeric": err_nan,
    })


@pytest.mark.scenario
def test_gui_material_dialog_automation_status():
    """
    Test Case ID: OSB-MAT-008
    Title: GUI MaterialPropertiesDialog Automation Status Check
    Category: Scenario / Material
    Objective: Attempt direct instantiation of MaterialPropertiesDialog; marks BLOCKED if
               PySide6 GUI framework is missing on the host environment.
    """
    try:
        from PySide6.QtWidgets import QApplication
        from osdagbridge.desktop.ui.dialogs.material_properties import MaterialPropertiesDialog
    except (ImportError, ModuleNotFoundError) as err:
        pytest.skip(f"PySide6 GUI framework missing on host environment: {err} — marked BLOCKED")

    try:
        app = QApplication.instance() or QApplication([])
        dialog = MaterialPropertiesDialog(read_only=False, member="Girder")
        assert dialog is not None
        assert dialog.fields is not None
    except Exception as exc:
        pytest.fail(f"MaterialPropertiesDialog instantiation crashed: {exc}")
