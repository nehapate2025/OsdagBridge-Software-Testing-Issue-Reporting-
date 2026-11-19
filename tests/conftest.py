"""
OsdagBridge Testing Framework — Root Conftest and Fixtures
==========================================================
Provides centralized test fixtures, metadata tracking, evidence recording,
and automated execution logging into CSV registers.
"""

import os
import sys
import json
import time
import datetime
import pytest
from pathlib import Path
from typing import Dict, Any

# Ensure src/ is on Python search path
SRC_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src"))
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

from osdagbridge.core.utils.common import (
    KEY_SPAN,
    KEY_CARRIAGEWAY_WIDTH,
    KEY_FOOTPATH,
    KEY_DESIGN_MODE,
    KEY_STRUCTURE_TYPE,
    KEY_DECK_CONCRETE_GRADE_BASIC,
    KEY_GIRDER,
    KEY_MATERIAL_GIRDER_FY,
    KEY_MATERIAL_GIRDER_FU,
    KEY_MATERIAL_GIRDER_E,
    KEY_MATERIAL_GIRDER_DENSITY,
    KEY_MATERIAL_GIRDER_POISSON,
    KEY_MATERIAL_DECK_FCK,
    KEY_MATERIAL_DECK_FCTM,
    KEY_MATERIAL_DECK_ECM,
    KEY_MATERIAL_DECK_THERMAL,
    KEY_MATERIAL_DECK_DENSITY,
    KEY_SKEW_ANGLE,
)

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
TEST_RESULTS_DIR = os.path.join(PROJECT_ROOT, "test_results")
EVIDENCE_DIR = os.path.join(TEST_RESULTS_DIR, "evidence")
EXEC_LOG_CSV = os.path.join(TEST_RESULTS_DIR, "test_execution_log.csv")
REGISTER_CSV = os.path.join(TEST_RESULTS_DIR, "test_case_register.csv")

os.makedirs(EVIDENCE_DIR, exist_ok=True)


# =============================================================================
# REUSABLE FIXTURES
# =============================================================================

@pytest.fixture
def valid_baseline_input() -> Dict[str, Any]:
    """
    Valid baseline bridge input parameters.
    Source: Standard project defaults for 30m span composite plate girder bridge.
    """
    return {
        KEY_STRUCTURE_TYPE: "Plate Girder",
        KEY_DESIGN_MODE: "Optimized",
        KEY_SPAN: 30.0,
        KEY_CARRIAGEWAY_WIDTH: 7.5,
        KEY_FOOTPATH: "None",
        KEY_GIRDER: "E250",
        KEY_DECK_CONCRETE_GRADE_BASIC: "M35",
        "project.title": "Baseline 30m Highway Bridge",
        "project.job_number": "OSB-TEST-001",
        "project.designer": "OsdagBridge Test Suite",
    }


@pytest.fixture
def modified_geometry_input() -> Dict[str, Any]:
    """
    Modified bridge geometry: 36m span, 8.5m carriageway, 2 footpaths (1.5m each),
    0.5m median, 15 degree skew angle.
    Source: Modified test configuration to exercise layout scaling.
    """
    return {
        KEY_STRUCTURE_TYPE: "Plate Girder",
        KEY_DESIGN_MODE: "Optimized",
        KEY_SPAN: 36.0,
        KEY_CARRIAGEWAY_WIDTH: 8.5,
        KEY_FOOTPATH: "Both Sides",
        "typical_section.footpath_width": 1.5,
        "typical_section.median_width": 0.5,
        KEY_SKEW_ANGLE: 15.0,
        KEY_GIRDER: "E350",
        KEY_DECK_CONCRETE_GRADE_BASIC: "M40",
        "project.title": "Modified Geometry 36m Highway Bridge",
        "project.job_number": "OSB-TEST-002",
    }


@pytest.fixture
def custom_steel_input(valid_baseline_input) -> Dict[str, Any]:
    """
    Bridge input configured with custom steel material properties.
    Source: High-strength structural steel test parameters (Fy=350 MPa, Fu=490 MPa).
    """
    inp = valid_baseline_input.copy()
    inp[KEY_GIRDER] = "Custom"
    inp[KEY_MATERIAL_GIRDER_FY] = 350.0
    inp[KEY_MATERIAL_GIRDER_FU] = 490.0
    inp[KEY_MATERIAL_GIRDER_E] = 200.0  # GPa
    inp[KEY_MATERIAL_GIRDER_DENSITY] = 78.5  # kN/m³
    inp[KEY_MATERIAL_GIRDER_POISSON] = 0.3
    return inp


@pytest.fixture
def custom_concrete_input(valid_baseline_input) -> Dict[str, Any]:
    """
    Bridge input configured with custom concrete deck properties.
    Source: High-performance deck concrete test parameters (fck=45 MPa, M45).
    """
    inp = valid_baseline_input.copy()
    inp[KEY_DECK_CONCRETE_GRADE_BASIC] = "Custom"
    inp[KEY_MATERIAL_DECK_FCK] = 45.0  # MPa
    inp[KEY_MATERIAL_DECK_FCTM] = 3.8  # MPa
    inp[KEY_MATERIAL_DECK_ECM] = 33.5  # GPa
    inp[KEY_MATERIAL_DECK_THERMAL] = 10.0  # ×10⁻⁶/°C
    inp[KEY_MATERIAL_DECK_DENSITY] = 25.0  # kN/m³
    return inp


@pytest.fixture
def invalid_input_scenario() -> Dict[str, Any]:
    """
    Invalid bridge input scenario containing multiple out-of-bounds parameters.
    Source: Negative boundary test case for validator testing.
    """
    return {
        KEY_STRUCTURE_TYPE: "Plate Girder",
        KEY_DESIGN_MODE: "Optimized",
        KEY_SPAN: 10.0,                 # Invalid: min is 20.0m
        KEY_CARRIAGEWAY_WIDTH: -5.0,    # Invalid: negative width
        KEY_FOOTPATH: "InvalidChoice",  # Invalid choice
        KEY_MATERIAL_GIRDER_DENSITY: 20.0, # Invalid: min is 50.0 kN/m³
        KEY_SKEW_ANGLE: 65.0,           # Invalid: max is 45.0 deg
    }


@pytest.fixture
def baseline_design_result() -> Dict[str, Any]:
    """
    Representative baseline design results output dictionary.
    Source: Validated bridge design calculations output structure.
    """
    return {
        "summary": {
            "max_bm": 1560.0,
            "max_sf": 520.0,
            "max_reaction": 545.2,
            "max_deflection": 18.5,
            "governing_combination": "1.35 DL + 1.50 LL (Class 70R Eccentric)",
            "dcr_moment": 0.78,
            "dcr_shear": 0.52,
            "dcr_deflection": 0.58,
            "design_status": "PASS",
        },
        "design_results": {
            "per_girder": {
                "G1": {
                    "checks": [
                        {"check_id": 1, "name": "Moment Capacity (ULS)", "demand": 1560.0, "capacity": 2000.0, "dcr": 0.78, "status": "PASS", "demand_unit": "kN-m", "capacity_unit": "kN-m"},
                        {"check_id": 2, "name": "Shear Capacity (ULS)", "demand": 520.0, "capacity": 1000.0, "dcr": 0.52, "status": "PASS", "demand_unit": "kN", "capacity_unit": "kN"},
                        {"check_id": 5, "name": "Lateral Torsional Buckling", "demand": 1260.0, "capacity": 1500.0, "dcr": 0.84, "status": "PASS", "demand_unit": "kN-m", "capacity_unit": "kN-m"},
                        {"check_id": 13, "name": "Deflection (SLS)", "demand": 23.2, "capacity": 40.0, "dcr": 0.58, "status": "PASS", "demand_unit": "mm", "capacity_unit": "mm"},
                    ]
                }
            },
            "concrete_deck": {
                "checks": [
                    {"check_id": "D1", "name": "Sagging Moment", "demand": 120.0, "capacity": 180.0, "dcr": 0.667, "status": "PASS", "demand_unit": "kNm/m", "capacity_unit": "kNm/m"},
                    {"check_id": "D2", "name": "Punching Shear", "demand": 210.0, "capacity": 350.0, "dcr": 0.600, "status": "PASS", "demand_unit": "kN", "capacity_unit": "kN"},
                ]
            },
            "cross_bracing": {
                "checks": [
                    {"check_id": "CB1", "name": "Chord Compression", "demand": 95.0, "capacity": 250.0, "dcr": 0.38, "status": "PASS", "demand_unit": "kN", "capacity_unit": "kN"},
                ]
            },
            "end_diaphragm": {
                "checks": [
                    {"check_id": "ED1", "name": "Diaphragm Bending", "demand": 110.0, "capacity": 261.9, "dcr": 0.42, "status": "PASS", "demand_unit": "kNm", "capacity_unit": "kNm"},
                ]
            }
        }
    }


@pytest.fixture
def evidence_tracker():
    """
    Evidence tracker helper for capturing snapshots and logs during test execution.
    """
    class EvidenceTracker:
        def __init__(self, evidence_dir: str):
            self.evidence_dir = evidence_dir

        def save_json_snapshot(self, test_id: str, snapshot_name: str, data: Dict[str, Any]) -> str:
            filename = f"{test_id}_{snapshot_name}_{int(time.time())}.json"
            filepath = os.path.join(self.evidence_dir, filename)
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, default=str)
            return filepath

        def save_error_log(self, test_id: str, error_text: str) -> str:
            filename = f"{test_id}_error_{int(time.time())}.txt"
            filepath = os.path.join(self.evidence_dir, filename)
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(error_text)
            return filepath

    return EvidenceTracker(EVIDENCE_DIR)


# =============================================================================
# PYTEST HOOKS FOR AUTOMATED LOGGING
# =============================================================================

@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """
    Hook to capture test execution status, duration, and error log,
    and append record to test_execution_log.csv.
    """
    outcome = yield
    report = outcome.get_result()

    if report.when == "call" or (report.when == "setup" and report.skipped):
        # Extract Test ID from function docstring or name
        doc = item.function.__doc__ or ""
        test_id = "OSB-UNKNOWN"
        for line in doc.splitlines():
            line_s = line.strip()
            if line_s.startswith("Test Case ID:") or line_s.startswith("ID:"):
                test_id = line_s.split(":")[-1].strip()
                break
        if test_id == "OSB-UNKNOWN" and hasattr(item, "name"):
            # Fallback heuristic from test name
            test_id = item.name

        if report.passed:
            status = "PASS"
        elif report.skipped:
            status = "BLOCKED"
        else:
            status = "FAIL"

        error_details = ""
        if report.failed:
            error_details = str(report.longrepr).replace("\n", " ").replace('"', "'")[:200]
        elif report.skipped:
            if hasattr(report, "longrepr") and isinstance(report.longrepr, tuple) and len(report.longrepr) >= 3:
                error_details = str(report.longrepr[2]).replace("\n", " ").replace('"', "'")[:200]
            else:
                error_details = str(report.longrepr).replace("\n", " ").replace('"', "'")[:200]

        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        duration = f"{report.duration:.3f}s"
        exec_id = f"EXEC-{int(time.time() * 1000) % 1000000:06d}"

        # Ensure execution log CSV has header
        if not os.path.exists(EXEC_LOG_CSV) or os.path.getsize(EXEC_LOG_CSV) == 0:
            with open(EXEC_LOG_CSV, "w", encoding="utf-8") as f:
                f.write("Execution ID,Date and Time,Test Case ID,Application Version,Input Summary,Result,Duration,Error Log,Evidence Path\n")

        with open(EXEC_LOG_CSV, "a", encoding="utf-8") as f:
            evidence_path = f"test_results/evidence/{test_id}_evidence.json"
            f.write(f'"{exec_id}","{timestamp}","{test_id}","1.0.0","Automated Test Run","{status}","{duration}","{error_details}","{evidence_path}"\n')
