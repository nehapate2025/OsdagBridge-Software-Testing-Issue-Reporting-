"""
Integration Tests: Plate Girder API and Solver Subsystems
=========================================================
Tests BridgeConfigurationSolver, preliminary sizing bounds, and sizing increment
algorithms without placeholder assertions.
"""

import pytest

from osdagbridge.core.bridge_types.plate_girder.initial_sizing import (
    BridgeConfigurationSolver,
    ceil_to_size_increment,
)


@pytest.mark.integration
def test_bridge_configuration_solver_width():
    """
    Test Case ID: OSB-INT-001
    Title: Bridge Configuration Solver Total Width Calculation
    Category: Integration / API
    Objective: Verify BridgeConfigurationSolver accurately calculates overall bridge width from components per IRC:5.
    """
    solver = BridgeConfigurationSolver(
        carriageway_width=7.5,
        crash_barrier_width=0.45,
        footpath_width=1.5,
        railing_width=0.25,
        median_width=0.0,
        n_footpaths=2,
    )
    # Overall = 7.5 + 2*0.45 + 2*(1.5 + 0.25) + 0.0 = 7.5 + 0.90 + 3.50 = 11.90 m
    total_w = solver.calculate_overall_bridge_width()
    assert abs(total_w - 11.90) < 1e-4, f"Expected 11.90 m, got {total_w}"


@pytest.mark.integration
def test_preliminary_depth_bounds():
    """
    Test Case ID: OSB-INT-002
    Title: Preliminary Girder Depth Bounds Calculation
    Category: Integration / API
    Objective: Verify preliminary depth bounds follow standard [Span/25, Span/15] range.
    """
    solver = BridgeConfigurationSolver(carriageway_width=7.5)
    span = 30.0
    min_d, max_d = solver.get_preliminary_depth_bounds(span)

    # 30.0 / 25 = 1.20 m; 30.0 / 15 = 2.00 m
    assert abs(min_d - 1.20) < 1e-3, f"Expected min depth 1.20 m, got {min_d}"
    assert abs(max_d - 2.00) < 1e-3, f"Expected max depth 2.00 m, got {max_d}"


@pytest.mark.integration
def test_initial_sizing_increments():
    """
    Test Case ID: OSB-INT-003
    Title: Size Increment Rounding Utility
    Category: Integration / API
    Objective: Verify that ceil_to_size_increment correctly rounds up dimensions to practical fabrication steps (10 mm).
    """
    assert ceil_to_size_increment(1.234) == pytest.approx(1.24, rel=1e-4)
    assert ceil_to_size_increment(1.200) == pytest.approx(1.20, rel=1e-4)
    assert ceil_to_size_increment(1.201) == pytest.approx(1.21, rel=1e-4)
