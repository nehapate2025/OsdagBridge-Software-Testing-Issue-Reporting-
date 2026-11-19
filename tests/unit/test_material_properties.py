"""
Unit Tests: Custom Material Properties Validation
=================================================
Tests validation of custom steel and concrete material properties
using BridgeInputValidator.
"""

import pytest

from osdagbridge.core.bridge_types.plate_girder.validator import BridgeInputValidator
from osdagbridge.core.utils.common import (
    KEY_MATERIAL_GIRDER_DENSITY,
    KEY_MATERIAL_GIRDER_FY,
    KEY_MATERIAL_GIRDER_FU,
    KEY_MATERIAL_GIRDER_E,
    KEY_MATERIAL_DECK_FCK,
    KEY_MATERIAL_DECK_DENSITY,
)


@pytest.fixture
def validator():
    return BridgeInputValidator()


@pytest.mark.unit
def test_validate_girder_weight_density_valid(validator):
    """
    Test Case ID: OSB-UNIT-MAT-001
    Title: Steel Girder Weight Density Valid Range
    Category: Unit / Materials
    Objective: Verify that standard steel weight densities (e.g. 78.5 kN/m³) pass validation.
    """
    res = validator.validate_material_inputs(KEY_MATERIAL_GIRDER_DENSITY, {KEY_MATERIAL_GIRDER_DENSITY: 78.5})
    assert res is None, f"Expected 78.5 kN/m³ to be valid, got {res}"


@pytest.mark.unit
def test_validate_girder_weight_density_out_of_bounds(validator):
    """
    Test Case ID: OSB-UNIT-MAT-002
    Title: Steel Girder Weight Density Boundary Clamping
    Category: Unit / Materials
    Objective: Verify that out-of-bounds weight density is clamped to allowed bounds [50.0, 120.0] kN/m³.
    """
    # Too low (< 50.0)
    res_low = validator.validate_material_inputs(KEY_MATERIAL_GIRDER_DENSITY, {KEY_MATERIAL_GIRDER_DENSITY: 30.0})
    assert res_low is not None
    assert res_low[0] == 50.0

    # Too high (> 120.0)
    res_high = validator.validate_material_inputs(KEY_MATERIAL_GIRDER_DENSITY, {KEY_MATERIAL_GIRDER_DENSITY: 150.0})
    assert res_high is not None
    assert res_high[0] == 120.0


@pytest.mark.unit
def test_validate_girder_yield_strength(validator):
    """
    Test Case ID: OSB-UNIT-MAT-003
    Title: Steel Yield Strength Fy Validation
    Category: Unit / Materials
    Objective: Verify Fy within [100.0, 1200.0] MPa passes and out-of-bounds is clamped.
    """
    res_e250 = validator.validate_material_inputs(KEY_MATERIAL_GIRDER_FY, {KEY_MATERIAL_GIRDER_FY: 250.0})
    assert res_e250 is None

    res_e350 = validator.validate_material_inputs(KEY_MATERIAL_GIRDER_FY, {KEY_MATERIAL_GIRDER_FY: 350.0})
    assert res_e350 is None

    res_too_low = validator.validate_material_inputs(KEY_MATERIAL_GIRDER_FY, {KEY_MATERIAL_GIRDER_FY: 50.0})
    assert res_too_low is not None
    assert res_too_low[0] == 100.0


@pytest.mark.unit
def test_validate_girder_tensile_strength(validator):
    """
    Test Case ID: OSB-UNIT-MAT-004
    Title: Steel Ultimate Tensile Strength Fu Validation
    Category: Unit / Materials
    Objective: Verify Fu within [100.0, 1500.0] MPa passes validation.
    """
    res_fu_valid = validator.validate_material_inputs(KEY_MATERIAL_GIRDER_FU, {KEY_MATERIAL_GIRDER_FU: 410.0})
    assert res_fu_valid is None

    res_fu_high = validator.validate_material_inputs(KEY_MATERIAL_GIRDER_FU, {KEY_MATERIAL_GIRDER_FU: 1800.0})
    assert res_fu_high is not None
    assert res_fu_high[0] == 1500.0


@pytest.mark.unit
def test_validate_concrete_grade_compressive_strength(validator):
    """
    Test Case ID: OSB-UNIT-MAT-005
    Title: Concrete Compressive Strength fck Validation
    Category: Unit / Materials
    Objective: Verify fck within [10.0, 80.0] MPa passes validation.
    """
    res_m35 = validator.validate_material_inputs(KEY_MATERIAL_DECK_FCK, {KEY_MATERIAL_DECK_FCK: 35.0})
    assert res_m35 is None

    res_m45 = validator.validate_material_inputs(KEY_MATERIAL_DECK_FCK, {KEY_MATERIAL_DECK_FCK: 45.0})
    assert res_m45 is None

    res_fck_low = validator.validate_material_inputs(KEY_MATERIAL_DECK_FCK, {KEY_MATERIAL_DECK_FCK: 5.0})
    assert res_fck_low is not None
    assert res_fck_low[0] == 10.0
