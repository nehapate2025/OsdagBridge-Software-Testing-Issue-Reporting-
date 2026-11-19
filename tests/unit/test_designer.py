"""
Unit Tests: Structural Designer Module Verification
===================================================
Tests structural designer loading and gracefully records BLOCKED if OpenSeesPy
is not installed in the execution environment.
"""

import pytest


@pytest.mark.unit
def test_designer_import_or_blocked():
    """
    Test Case ID: OSB-UNIT-015
    Title: Structural Designer Loading Verification
    Category: Unit / Designer
    Objective: Verify import of plate girder designer module or report BLOCKED status if OpenSeesPy native solver is missing.
    """
    try:
        from osdagbridge.core.bridge_types.plate_girder import designer
        assert designer is not None
    except ModuleNotFoundError as e:
        if "openseespy" in str(e).lower():
            pytest.skip("OpenSeesPy native binary not installed on host — marked BLOCKED")
        else:
            raise e
