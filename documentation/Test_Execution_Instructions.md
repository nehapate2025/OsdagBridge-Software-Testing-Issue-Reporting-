# Test Execution Instructions — OsdagBridge

This document provides exact command-line instructions to execute the automated verification suite, run individual test scenarios, generate JUnit reports, and inspect test evidence.

---

## 1. Running the Complete Verification Suite

To run all 95 automated test cases in verbose mode:
```bash
pytest -v --tb=short
```

To run with JUnit XML report generation:
```bash
pytest -v --junitxml=test_results/pytest_report.xml
```

---

## 2. Running Specific Test Categories

### Run Unit Tests Only
```bash
pytest -m unit -v
```

### Run Integration Tests Only
```bash
pytest -m integration -v
```

### Run Verification Scenarios (Tasks 2–8)
```bash
pytest tests/scenarios/ -v
```

---

## 3. Running Individual Task Scenarios

- **Task 2 (Basic Geometry Verification):**
  ```bash
  pytest tests/scenarios/test_basic_geometry.py -v
  ```

- **Task 3 (Custom Steel Material Verification):**
  ```bash
  pytest tests/scenarios/test_custom_steel.py -v
  ```

- **Task 4 (Concrete Deck & Reinforcement Verification):**
  ```bash
  pytest tests/scenarios/test_custom_concrete.py tests/scenarios/test_custom_reinforcement.py -v
  ```

- **Task 5 (Consecutive Design Runs Verification):**
  ```bash
  pytest tests/scenarios/test_consecutive_runs.py -v
  ```

- **Task 6 (Input Dictionary Verification):**
  ```bash
  pytest tests/scenarios/test_input_dictionary.py -v
  ```

- **Task 7 (Output Dictionary Verification):**
  ```bash
  pytest tests/scenarios/test_output_dictionary.py -v
  ```

- **Task 8 (CAD & Structural Plot Verification):**
  ```bash
  pytest tests/scenarios/test_cad_visualization.py tests/scenarios/test_structural_plots.py -v
  ```

---

## 4. Inspecting Execution Artifacts & Evidence

- **Master Test Case Register:** [`test_results/final_report/master_test_case_register.csv`](file:///c:/Users/acer/Downloads/OsdagBridge-dev/test_results/final_report/master_test_case_register.csv)
- **Execution Summary:** [`test_results/final_report/test_execution_summary.csv`](file:///c:/Users/acer/Downloads/OsdagBridge-dev/test_results/final_report/test_execution_summary.csv)
- **Defect Register:** [`test_results/final_report/bug_register.csv`](file:///c:/Users/acer/Downloads/OsdagBridge-dev/test_results/final_report/bug_register.csv)
- **Evidence Index:** [`test_results/final_report/evidence_index.csv`](file:///c:/Users/acer/Downloads/OsdagBridge-dev/test_results/final_report/evidence_index.csv)
- **Comprehensive PDF Report:** [`test_results/final_report/OsdagBridge_Comprehensive_Testing_Report.pdf`](file:///c:/Users/acer/Downloads/OsdagBridge-dev/test_results/final_report/OsdagBridge_Comprehensive_Testing_Report.pdf)
