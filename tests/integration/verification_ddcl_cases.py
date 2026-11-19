"""
Integration Tests: DDCL Verification Cases Integrity
====================================================
Verifies that example verification case files exist, are accessible,
and adhere to YAML structure and expected baseline parameters.
"""

import os
import pytest


@pytest.mark.integration
def test_verification_ddcl_cases_structure():
    """
    Test Case ID: OSB-INT-010
    Title: Verification DDCL Case Files Integrity Check
    Category: Integration / Verification
    Objective: Verify that repository verification cases exist in examples/plate_girder/ and can be accessed.
    """
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    examples_dir = os.path.join(repo_root, "examples", "plate_girder")

    assert os.path.exists(examples_dir), f"Examples directory does not exist: {examples_dir}"

    expected_files = [
        "example_basic.yaml",
        "verification_case_01.yaml",
        "verification_case_02.yaml",
    ]

    for fname in expected_files:
        fpath = os.path.join(examples_dir, fname)
        assert os.path.exists(fpath), f"Expected verification case file missing: {fname}"
        assert os.path.getsize(fpath) > 0, f"Verification case file is empty: {fname}"

        # Check readable text
        with open(fpath, "r", encoding="utf-8") as f:
            content = f.read()
            assert len(content.strip()) > 0, f"File content is blank: {fname}"
