"""
Unit Tests: Input Validation Engine
===================================
Tests field validation, boundary clamping, numeric conversion, and error reporting
using BridgeInputValidator.
"""

import pytest

from osdagbridge.core.bridge_types.plate_girder.validator import BridgeInputValidator
from osdagbridge.core.utils.common import (
    KEY_SPAN,
    KEY_CARRIAGEWAY_WIDTH,
    KEY_SKEW_ANGLE,
)


@pytest.fixture
def validator():
    return BridgeInputValidator()


@pytest.mark.unit
def test_validate_span_valid_range(validator):
    """
    Test Case ID: OSB-UNIT-005
    Title: Span Valid Range Validation
    Category: Unit / Validation
    Objective: Verify that spans within the software scope (20.0m to 45.0m) pass without validation errors.
    """
    for span in [20.0, 25.0, 30.0, 35.0, 40.0, 45.0]:
        res = validator.validate_basic_inputs(KEY_SPAN, {KEY_SPAN: span})
        assert res is None, f"Expected valid span {span} to return None, got {res}"


@pytest.mark.unit
def test_validate_span_under_minimum(validator):
    """
    Test Case ID: OSB-UNIT-006
    Title: Span Under Minimum Scope Clamping
    Category: Unit / Validation
    Objective: Verify that spans below 20.0m are clamped to 20.0m with an informative error message.
    """
    res = validator.validate_basic_inputs(KEY_SPAN, {KEY_SPAN: 15.0})
    assert res is not None, "Span < 20.0m must produce a validation response"
    clamped_val, msg = res
    assert clamped_val == 20.0, f"Expected clamped value 20.0, got {clamped_val}"
    assert "between 20.0 m and 45.0 m" in msg


@pytest.mark.unit
def test_validate_span_over_maximum(validator):
    """
    Test Case ID: OSB-UNIT-007
    Title: Span Over Maximum Scope Clamping
    Category: Unit / Validation
    Objective: Verify that spans exceeding 45.0m are clamped to 45.0m with an informative error message.
    """
    res = validator.validate_basic_inputs(KEY_SPAN, {KEY_SPAN: 55.0})
    assert res is not None, "Span > 45.0m must produce a validation response"
    clamped_val, msg = res
    assert clamped_val == 45.0, f"Expected clamped value 45.0, got {clamped_val}"
    assert "between 20.0 m and 45.0 m" in msg


@pytest.mark.unit
def test_validate_span_non_numeric(validator):
    """
    Test Case ID: OSB-UNIT-008
    Title: Span Non-Numeric Input Rejection
    Category: Unit / Validation
    Objective: Verify that non-numeric strings for span trigger a numeric conversion error.
    """
    res = validator.validate_basic_inputs(KEY_SPAN, {KEY_SPAN: "invalid_span"})
    assert res is not None, "Non-numeric span must produce a validation error"
    clamped_val, msg = res
    assert clamped_val == 20.0
    assert "numeric value" in msg.lower()


@pytest.mark.unit
def test_validate_carriageway_width(validator):
    """
    Test Case ID: OSB-UNIT-009
    Title: Carriageway Width Validation
    Category: Unit / Validation
    Objective: Verify that valid carriageway widths pass validation.
    """
    res_valid = validator.validate_basic_inputs(KEY_CARRIAGEWAY_WIDTH, {KEY_CARRIAGEWAY_WIDTH: 7.5})
    assert res_valid is None, f"Expected 7.5m carriageway to be valid, got {res_valid}"


@pytest.mark.unit
def test_validate_skew_angle_range(validator):
    """
    Test Case ID: OSB-UNIT-010
    Title: Skew Angle Validation Limits
    Category: Unit / Validation
    Objective: Verify skew angle boundaries (0 to 45 degrees).
    """
    res_valid = validator.validate_basic_inputs(KEY_SKEW_ANGLE, {KEY_SKEW_ANGLE: 15.0})
    assert res_valid is None, f"Expected 15 deg skew to be valid, got {res_valid}"
