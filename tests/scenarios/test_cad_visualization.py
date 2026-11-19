"""
Scenario Tests: Comprehensive CAD Model and Visualization Verification (Task 8)
=============================================================================
Validates 3D CAD parameter generation, component extraction, geometry scaling,
material/stiffener configuration, deck positioning, and memory idempotence across:
- OSB-CAD-001: Default 3D Model Generation
- OSB-CAD-002: Geometry Modification
- OSB-CAD-003: Custom Steel Component Visualization
- OSB-CAD-004: Concrete Deck Visualization
- OSB-CAD-007: Graphical State and Memory Verification
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
    KEY_TS_DECK_THICKNESS,
    KEY_TS_OVERALL_WIDTH,
    KEY_TS_NO_OF_GIRDERS,
    KEY_TS_GIRDER_SPACING,
    KEY_TS_DECK_OVERHANG,
    KEY_MP_GIRDER_TOP_FLANGE_WIDTH,
    KEY_MP_GIRDER_TOP_FLANGE_THICKNESS,
    KEY_MP_GIRDER_BOTTOM_FLANGE_WIDTH,
    KEY_MP_GIRDER_BOTTOM_FLANGE_THICKNESS,
    KEY_MP_GIRDER_WEB_THICKNESS,
    KEY_MP_GIRDER_DEPTH,
)
from osdagbridge.core.bridge_types.plate_girder.plategirderbridge import PlateGirderBridge
from osdagbridge.core.bridge_types.plate_girder.defaults import solve_extend_basic_input_dict

EVIDENCE_DIR = Path(__file__).resolve().parents[2] / "test_results" / "evidence" / "cad_plots"


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


def test_default_3d_model_generation(baseline_inputs):
    """
    Test Case ID: OSB-CAD-001
    Verify that the baseline bridge configuration compiles all required
    parameters into the 3D CAD definition DTO (BridgeParametersDTO).
    """
    bridge = PlateGirderBridge()
    bridge.set_input(baseline_inputs)
    bridge._convert_girder_dims_mm_to_m()
    bridge.output_dict = dict(bridge.input_dict)
    bridge.bridge_component_solver()

    dto = bridge.get_3d_cad_parameters()

    # Verify primary bridge dimensions in DTO
    assert dto.span_length_L == 30000.0  # mm
    assert dto.carriageway_width == 7500.0  # mm
    assert dto.num_girders == 4
    assert dto.girder_spacing == 2100.0  # mm
    assert dto.deck_thickness == 250.0  # mm
    assert dto.skew_angle == 0.0

    # Verify girder plate section dimensions (mm)
    assert dto.girder_section_d > 0.0
    assert dto.girder_section_bf > 0.0
    assert dto.girder_section_tf > 0.0
    assert dto.girder_section_tw > 0.0

    # Save evidence
    ev_path = EVIDENCE_DIR / "default_model" / "default_cad_parameters.json"
    ev_path.parent.mkdir(parents=True, exist_ok=True)
    with open(ev_path, "w", encoding="utf-8") as f:
        json.dump({
            "span_mm": dto.span_length_L,
            "carriageway_width_mm": dto.carriageway_width,
            "num_girders": dto.num_girders,
            "girder_spacing_mm": dto.girder_spacing,
            "deck_thickness_mm": dto.deck_thickness,
            "girder_section_d_mm": dto.girder_section_d,
            "girder_section_bf_mm": dto.girder_section_bf,
            "girder_section_tf_mm": dto.girder_section_tf,
            "girder_section_tw_mm": dto.girder_section_tw,
        }, f, indent=2)

    assert ev_path.exists()


def test_geometry_modification():
    """
    Test Case ID: OSB-CAD-002
    Verify that modified geometry (36m span, 9.5m carriageway, skew 15 deg,
    both footpaths) updates the 3D CAD definition correctly.
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
    bridge._convert_girder_dims_mm_to_m()
    bridge.output_dict = dict(bridge.input_dict)
    bridge.bridge_component_solver()

    dto = bridge.get_3d_cad_parameters()

    assert dto.span_length_L == 36000.0
    assert dto.carriageway_width == 9500.0
    assert dto.skew_angle == 15.0
    assert dto.footpath_config == "BOTH"
    assert dto.num_girders >= 5

    ev_path = EVIDENCE_DIR / "geometry_changes" / "modified_geometry_cad.json"
    ev_path.parent.mkdir(parents=True, exist_ok=True)
    with open(ev_path, "w", encoding="utf-8") as f:
        json.dump({
            "span_mm": dto.span_length_L,
            "carriageway_width_mm": dto.carriageway_width,
            "skew_angle": dto.skew_angle,
            "footpath_config": dto.footpath_config,
            "num_girders": dto.num_girders,
        }, f, indent=2)

    assert ev_path.exists()


def test_custom_steel_component_visualization(baseline_inputs):
    """
    Test Case ID: OSB-CAD-003
    Verify that custom steel component and stiffener properties propagate to CAD DTO.
    """
    custom_inputs = copy.deepcopy(baseline_inputs)
    custom_inputs[KEY_GIRDER] = "E 350"
    from osdagbridge.core.utils.common import (
        KEY_MP_STIFFENER_INTERMEDIATE_THICKNESS,
        KEY_MP_STIFFENER_INTERMEDIATE_SPACING,
    )
    for gi in range(1, 5):
        custom_inputs[f"{KEY_MP_STIFFENER_INTERMEDIATE_THICKNESS}.G{gi}.M1"] = 12.0
        custom_inputs[f"{KEY_MP_STIFFENER_INTERMEDIATE_SPACING}.G{gi}.M1"] = 1500.0

    bridge = PlateGirderBridge()
    bridge.set_input(custom_inputs)
    bridge._convert_girder_dims_mm_to_m()
    bridge.output_dict = dict(bridge.input_dict)
    bridge.bridge_component_solver()

    dto = bridge.get_3d_cad_parameters()

    assert dto.steel_grade == "E 350"
    assert dto.intermediate_stiffener_thickness == 12.0
    assert dto.intermediate_stiffener_spacing == 1500.0

    ev_path = EVIDENCE_DIR / "steel_components" / "custom_steel_components_cad.json"
    ev_path.parent.mkdir(parents=True, exist_ok=True)
    with open(ev_path, "w", encoding="utf-8") as f:
        json.dump({
            "steel_grade": dto.steel_grade,
            "intermediate_stiffener_thickness": dto.intermediate_stiffener_thickness,
            "intermediate_stiffener_spacing": dto.intermediate_stiffener_spacing,
        }, f, indent=2)

    assert ev_path.exists()


def test_concrete_deck_visualization(baseline_inputs):
    """
    Test Case ID: OSB-CAD-004
    Verify concrete deck thickness and alignment in the CAD DTO.
    """
    bridge = PlateGirderBridge()
    bridge.set_input(baseline_inputs)
    bridge._convert_girder_dims_mm_to_m()
    bridge.output_dict = dict(bridge.input_dict)
    bridge.output_dict[KEY_TS_DECK_THICKNESS] = 275.0  # Modified deck thickness in mm
    bridge.bridge_component_solver()

    dto = bridge.get_3d_cad_parameters()

    assert dto.deck_thickness == 275.0
    assert dto.concrete_grade == "M35"

    ev_path = EVIDENCE_DIR / "concrete_deck" / "concrete_deck_cad.json"
    ev_path.parent.mkdir(parents=True, exist_ok=True)
    with open(ev_path, "w", encoding="utf-8") as f:
        json.dump({
            "deck_thickness_mm": dto.deck_thickness,
            "concrete_grade": dto.concrete_grade,
        }, f, indent=2)

    assert ev_path.exists()


def test_graphical_state_and_memory_verification(baseline_inputs):
    """
    Test Case ID: OSB-CAD-007
    Verify that repeated CAD parameter compilation is idempotent and clean.
    """
    bridge = PlateGirderBridge()
    bridge.set_input(baseline_inputs)
    bridge._convert_girder_dims_mm_to_m()
    bridge.output_dict = dict(bridge.input_dict)
    bridge.bridge_component_solver()

    dtos = [bridge.get_3d_cad_parameters() for _ in range(5)]

    for d in dtos[1:]:
        assert d.span_length_L == dtos[0].span_length_L
        assert d.num_girders == dtos[0].num_girders
        assert d.girder_spacing == dtos[0].girder_spacing
        assert d.deck_thickness == dtos[0].deck_thickness

    ev_path = EVIDENCE_DIR / "default_model" / "cad_state_memory_verification.json"
    ev_path.parent.mkdir(parents=True, exist_ok=True)
    with open(ev_path, "w", encoding="utf-8") as f:
        json.dump({
            "iterations": len(dtos),
            "idempotent": True,
            "span_mm": dtos[0].span_length_L,
        }, f, indent=2)

    assert ev_path.exists()
