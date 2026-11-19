"""
Reporting and Evidence Tests: Snapshot Export and Chart Generation
==================================================================
Validates persistence of input/output dictionaries as structured evidence artifacts
and automated headless generation of engineering verification charts.
"""

import os
import json
import pytest

from osdagbridge.core.reports.chart_utils import create_ur_bar_chart
from osdagbridge.core.utils.common import KEY_SPAN


@pytest.mark.reporting
def test_export_input_dict_snapshot(valid_baseline_input, evidence_tracker):
    """
    Test Case ID: OSB-REP-001
    Title: Input Dictionary Snapshot Export
    Category: Reporting / Evidence
    Objective: Verify evidence tracker exports full input dictionary to test_results/evidence/ as valid readable JSON.
    """
    file_path = evidence_tracker.save_json_snapshot(
        test_id="OSB-REP-001",
        snapshot_name="input_baseline",
        data=valid_baseline_input,
    )

    assert os.path.exists(file_path), f"Evidence file was not created: {file_path}"
    assert os.path.getsize(file_path) > 0, "Evidence file is empty"

    with open(file_path, "r", encoding="utf-8") as f:
        loaded = json.load(f)

    assert loaded["project.title"] == valid_baseline_input["project.title"]
    assert loaded[KEY_SPAN] == valid_baseline_input[KEY_SPAN]


@pytest.mark.reporting
def test_export_output_dict_snapshot(baseline_design_result, evidence_tracker):
    """
    Test Case ID: OSB-REP-002
    Title: Output Dictionary Snapshot Export
    Category: Reporting / Evidence
    Objective: Verify evidence tracker exports full design output dictionary to test_results/evidence/ as valid readable JSON.
    """
    file_path = evidence_tracker.save_json_snapshot(
        test_id="OSB-REP-002",
        snapshot_name="output_baseline",
        data=baseline_design_result,
    )

    assert os.path.exists(file_path), f"Evidence file was not created: {file_path}"
    assert os.path.getsize(file_path) > 0, "Evidence file is empty"

    with open(file_path, "r", encoding="utf-8") as f:
        loaded = json.load(f)

    assert "summary" in loaded
    assert loaded["summary"]["design_status"] == "PASS"
    assert "design_results" in loaded


@pytest.mark.reporting
def test_chart_generation_and_export(evidence_tracker):
    """
    Test Case ID: OSB-REP-003
    Title: Verification Chart Generation and Export
    Category: Reporting / Evidence
    Objective: Verify create_ur_bar_chart generates a high-resolution 300 DPI chart image and saves it to test_results/evidence/.
    """
    chart_filename = os.path.join(evidence_tracker.evidence_dir, "OSB-REP-003_ur_chart.png")

    categories = ["Moment", "Shear", "LTB", "Deflection"]
    values = [0.78, 0.52, 0.84, 0.58]
    title = "Plate Girder G1 — Utilization Ratios (UR)"

    result_path = create_ur_bar_chart(
        categories=categories,
        values=values,
        title=title,
        output_path=chart_filename,
    )

    assert os.path.exists(result_path), f"Chart file not found: {result_path}"
    assert os.path.getsize(result_path) > 1000, "Chart image file is unexpectedly small"
