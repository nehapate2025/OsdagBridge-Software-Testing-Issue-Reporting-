"""
Integration Tests: CLI Interface for Plate Girder Bridge
========================================================
Validates CLI entrypoint, argument execution, and invalid input path handling.
"""

import sys
import pytest
from osdagbridge.cli.__main__ import main as cli_main
from osdagbridge.cli.commands import analyze_cmd


@pytest.mark.integration
def test_cli_entrypoint_main(capsys):
    """
    Test Case ID: OSB-INT-004
    Title: CLI Entrypoint Invocation
    Category: Integration / CLI
    Objective: Verify that invoking cli.__main__.main() runs without exception and outputs CLI status.
    """
    cli_main()
    captured = capsys.readouterr()
    assert "osdagbridge CLI" in captured.out, f"Unexpected CLI main output: {captured.out}"


@pytest.mark.integration
def test_cli_analyze_cmd_execution(capsys):
    """
    Test Case ID: OSB-INT-005
    Title: CLI Analyze Command Execution
    Category: Integration / CLI
    Objective: Verify that analyze_cmd accepts an input configuration path and executes without crashing.
    """
    test_path = "examples/plate_girder/verification_case_01.yaml"
    analyze_cmd(test_path)
    captured = capsys.readouterr()
    assert "analyze" in captured.out, f"Expected 'analyze' in output, got: {captured.out}"
    assert test_path in captured.out, f"Expected path in output, got: {captured.out}"


@pytest.mark.integration
def test_cli_invalid_path_handling(capsys):
    """
    Test Case ID: OSB-INT-006
    Title: CLI Analyze Command Non-Existent Path Handling
    Category: Integration / CLI
    Objective: Verify that analyze_cmd handles non-existent or dummy file paths gracefully without uncaught exceptions.
    """
    non_existent_path = "non_existent/path/to/invalid_bridge.yaml"
    try:
        analyze_cmd(non_existent_path)
        captured = capsys.readouterr()
        assert non_existent_path in captured.out or "analyze" in captured.out
    except Exception as e:
        pytest.fail(f"analyze_cmd crashed unexpectedly on invalid path: {e}")
