"""
Unit Tests: Structural Analyser Module Verification
===================================================
Tests structural analyser loading and gracefully records BLOCKED if OpenSeesPy
is not installed in the execution environment.
"""

import pytest


@pytest.mark.unit
def test_analyser_import_or_blocked():
    """
    Test Case ID: OSB-UNIT-014
    Title: Structural Analyser Loading Verification
    Category: Unit / Analyser
    Objective: Verify import of plate girder analyser module or report BLOCKED status if OpenSeesPy native solver is missing.
    """
    try:
        from osdagbridge.core.bridge_types.plate_girder import analyser
        assert analyser is not None
    except ModuleNotFoundError as e:
        if "openseespy" in str(e).lower():
            pytest.skip("OpenSeesPy native binary not installed on host — marked BLOCKED")
        else:
            raise e
