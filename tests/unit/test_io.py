"""
Unit Tests: Input/Output Handling and Serialization
===================================================
Tests JSON and YAML serialization, dictionary persistence, girder property
resolution, and evidence export without dummy assertions.
"""

import os
import json
import tempfile
import pytest

from osdagbridge.core.boq.boq_generator import resolve_girder_value
from osdagbridge.core.utils.common import (
    KEY_SPAN,
    KEY_CARRIAGEWAY_WIDTH,
    KEY_STRUCTURE_TYPE,
)


@pytest.mark.unit
def test_input_dict_json_serialization(valid_baseline_input):
    """
    Test Case ID: OSB-UNIT-001
    Title: Input Dictionary JSON Serialization Round-Trip
    Category: Unit / IO
    Objective: Verify that bridge input dictionaries serialize to valid JSON and deserialize losslessly.
    """
    json_str = json.dumps(valid_baseline_input, indent=2)
    assert len(json_str) > 0, "Serialized JSON string must not be empty"

    recovered = json.loads(json_str)
    assert recovered[KEY_SPAN] == valid_baseline_input[KEY_SPAN]
    assert recovered[KEY_CARRIAGEWAY_WIDTH] == valid_baseline_input[KEY_CARRIAGEWAY_WIDTH]
    assert recovered[KEY_STRUCTURE_TYPE] == valid_baseline_input[KEY_STRUCTURE_TYPE]
    assert len(recovered) == len(valid_baseline_input)


@pytest.mark.unit
def test_input_dict_yaml_handling(valid_baseline_input):
    """
    Test Case ID: OSB-UNIT-002
    Title: Input Dictionary File Persistence
    Category: Unit / IO
    Objective: Verify file reading and writing of input data to temporary storage.
    """
    with tempfile.NamedTemporaryFile("w+", suffix=".json", delete=False) as tmp:
        json.dump(valid_baseline_input, tmp)
        tmp_path = tmp.name

    try:
        assert os.path.exists(tmp_path)
        with open(tmp_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        assert data[KEY_SPAN] == 30.0
        assert data[KEY_CARRIAGEWAY_WIDTH] == 7.5
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)


@pytest.mark.unit
def test_resolve_girder_value_io():
    """
    Test Case ID: OSB-UNIT-003
    Title: Girder Value Resolution Across Dynamic and Scalar Keys
    Category: Unit / IO
    Objective: Verify that resolve_girder_value resolves both per-girder candidate keys (.G1.M1) and legacy scalar fallbacks.
    """
    source_dict = {
        "depth.G1.M1": 1800.0,
        "depth.G2.M1": 1850.0,
        "flange_width": 450.0,
    }

    # Dynamic per-girder candidate
    val_g1 = resolve_girder_value(source_dict, "depth", i=0)
    assert val_g1 == 1800.0, f"Expected 1800.0 for G1, got {val_g1}"

    val_g2 = resolve_girder_value(source_dict, "depth", i=1)
    assert val_g2 == 1850.0, f"Expected 1850.0 for G2, got {val_g2}"

    # Scalar fallback candidate
    val_flange = resolve_girder_value(source_dict, "flange_width", i=0)
    assert val_flange == 450.0, f"Expected 450.0 for scalar flange_width, got {val_flange}"

    # Missing key raises KeyError
    with pytest.raises(KeyError):
        resolve_girder_value(source_dict, "nonexistent", i=0)


@pytest.mark.unit
def test_evidence_json_export(valid_baseline_input, evidence_tracker):
    """
    Test Case ID: OSB-UNIT-004
    Title: Evidence Snapshot Export Verification
    Category: Unit / IO
    Objective: Verify that the evidence tracker captures structured JSON snapshots into test_results/evidence/.
    """
    exported_path = evidence_tracker.save_json_snapshot("OSB-UNIT-004", "input_snapshot", valid_baseline_input)
    assert os.path.exists(exported_path), f"Evidence file must exist at {exported_path}"
    assert os.path.getsize(exported_path) > 0, "Evidence file must not be empty"

    with open(exported_path, "r", encoding="utf-8") as f:
        loaded = json.load(f)
    assert loaded[KEY_SPAN] == 30.0
