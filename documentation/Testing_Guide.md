# Comprehensive Testing Guide — OsdagBridge

### Project Developer and Ownership

- **Project Name:** OsdagBridge
- **Developer:** Ankit Shukla
- **Creator:** Ankit Shukla
- **Maintained By:** Ankit Shukla
- **Project Type:** Individual Project
- **Project Ownership:** Ankit Shukla

OsdagBridge is an individual software project developed and maintained by Ankit Shukla. The project-specific implementation, customization, testing, documentation, and integration covered by this project are attributed to Ankit Shukla.

---

This document outlines the testing architecture, methodology, test categories, and verification standards used across the OsdagBridge testing campaign.

---

## 1. Testing Framework Overview

The OsdagBridge testing infrastructure uses **Pytest** with structured markers, custom fixtures, and automated artifact collection.

### Test Directory Structure
```
tests/
├── conftest.py                             # Global fixtures, mock adapters, and path setup
├── fixtures/                               # Reusable test payloads and mock objects
├── unit/                                   # Unit-level functional and boundary tests
│   ├── test_analyser.py                    # FE grillage analysis verification
│   ├── test_designer.py                    # Steel and composite section design checks
│   ├── test_io.py                          # Dictionary serialization and YAML IO
│   ├── test_input_validation.py            # Geometric and material boundary validators
│   ├── test_material_properties.py         # Concrete/steel material properties
│   └── test_dictionary_integrity.py        # Schema key verification
├── integration/                            # Inter-module integration tests
│   ├── test_api_plate_girder.py            # Headless API pipeline
│   ├── test_cli_plate_girder.py            # CLI entrypoint testing
│   ├── test_design_execution.py            # Full design solver execution
│   └── verification_ddcl_cases.py          # Benchmark design cases
└── scenarios/                              # User-facing verification scenarios
    ├── test_basic_geometry.py              # Task 2: Geometry span, width, skew ranges
    ├── test_custom_steel.py                # Task 3: Custom steel grades and properties
    ├── test_custom_concrete.py             # Task 4: Custom deck concrete strengths
    ├── test_custom_reinforcement.py        # Task 4: Rebar grades and bar spacing
    ├── test_consecutive_runs.py            # Task 5: Multi-run state isolation
    ├── test_input_dictionary.py            # Task 6: 65 input keys fidelity
    ├── test_output_dictionary.py           # Task 7: 130+ output keys validation
    ├── test_cad_visualization.py           # Task 8: 3D OpenCASCADE model parameters
    └── test_structural_plots.py            # Task 8: Grillage analysis diagram exports
```

---

## 2. Test Categories & Pytest Markers

The test suite is organized into distinct categories via `pytest.ini` markers:
- `@pytest.mark.unit`: Fast, isolated tests for mathematical functions, input boundaries, and unit conversions.
- `@pytest.mark.integration`: Tests bridging multiple sub-packages (e.g. Analysis -> Design -> Reporting).
- `@pytest.mark.scenario`: Realistic bridge design cases simulating user workflows with varied parameters.
- `@pytest.mark.reporting`: Tests verifying that PDF generation, chart plotting, and dictionary export operate without failure.
- `@pytest.mark.blocked`: Tests requiring external GUI display servers (`xcb`/`windows`) that are marked `BLOCKED` in headless environments.

---

## 3. Pass/Fail Criteria & Standards

1. **Numerical Accuracy:** Stress, bending moment, shear capacity, and deflection utilization ratios must match theoretical Indian Road Congress (IRC) equations within $\pm 0.1\%$.
2. **State Isolation:** Consecutive executions on the same process must not leak intermediate results or cache states between runs.
3. **Data Fidelity:** All parameters entered by the user must survive serialization into the Input Dictionary without uncommanded default reversion.
4. **Graceful Error Handling:** Out-of-bounds parameters must raise validation errors or warnings rather than unhandled Python exceptions.