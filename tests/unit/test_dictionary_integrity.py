"""
Unit Tests: Dictionary Integrity and Immutability
=================================================
Tests input dictionary expansion, canonical key presence, and state isolation
across execution routines.
"""

import pytest

from osdagbridge.core.bridge_types.plate_girder.defaults import solve_extend_basic_input_dict
from osdagbridge.core.utils.common import (
    KEY_SPAN,
    KEY_CARRIAGEWAY_WIDTH,
    KEY_STRUCTURE_TYPE,
    KEY_DESIGN_MODE,
    KEY_GIRDER,
    KEY_DECK_CONCRETE_GRADE_BASIC,
    KEY_FOOTPATH,
    KEY_TS_NO_OF_GIRDERS,
    KEY_TS_DECK_THICKNESS,
    KEY_TS_GIRDER_SPACING,
)


@pytest.mark.unit
def test_solve_extend_basic_input_dict_expansion(valid_baseline_input):
    """
    Test Case ID: OSB-UNIT-011
    Title: Input Dictionary Expansion from Basic Inputs
    Category: Unit / Dictionary Integrity
    Objective: Verify that 7 basic inputs expand into the complete default layout dictionary (>500 keys).
    """
    inp = valid_baseline_input.copy()
    initial_keys_count = len(inp)
    assert initial_keys_count < 15, "Initial basic dictionary must be concise"

    solve_extend_basic_input_dict(inp)
    expanded_keys_count = len(inp)
    assert expanded_keys_count >= 500, f"Expected >= 500 keys after expansion, got {expanded_keys_count}"

    # Verify structural layout keys populated
    assert KEY_TS_NO_OF_GIRDERS in inp
    assert int(inp[KEY_TS_NO_OF_GIRDERS]) >= 2
    assert KEY_TS_DECK_THICKNESS in inp
    assert float(inp[KEY_TS_DECK_THICKNESS]) >= 150.0
    assert KEY_TS_GIRDER_SPACING in inp


@pytest.mark.unit
def test_canonical_keys_presence(valid_baseline_input):
    """
    Test Case ID: OSB-UNIT-012
    Title: Canonical Design Keys Presence Verification
    Category: Unit / Dictionary Integrity
    Objective: Verify that mandatory canonical keys exist in baseline input.
    """
    mandatory_keys = [
        KEY_STRUCTURE_TYPE,
        KEY_DESIGN_MODE,
        KEY_SPAN,
        KEY_CARRIAGEWAY_WIDTH,
        KEY_FOOTPATH,
        KEY_GIRDER,
        KEY_DECK_CONCRETE_GRADE_BASIC,
    ]
    for k in mandatory_keys:
        assert k in valid_baseline_input, f"Mandatory key {k} missing from baseline input"


@pytest.mark.unit
def test_input_dict_deep_isolation(valid_baseline_input):
    """
    Test Case ID: OSB-UNIT-013
    Title: Input Dictionary Mutation Isolation
    Category: Unit / Dictionary Integrity
    Objective: Verify that mutating a working copy does not alter the original fixture data.
    """
    original_span = valid_baseline_input[KEY_SPAN]
    working_copy = valid_baseline_input.copy()

    working_copy[KEY_SPAN] = 42.0
    working_copy["new_temporary_key"] = "test_val"

    assert valid_baseline_input[KEY_SPAN] == original_span, "Fixture must remain unmodified"
    assert "new_temporary_key" not in valid_baseline_input
