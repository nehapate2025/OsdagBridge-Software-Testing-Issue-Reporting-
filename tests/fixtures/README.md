# OsdagBridge Test Fixtures Documentation

**Directory:** `tests/fixtures/`  
**Parent Configuration:** `tests/conftest.py`  
**Purpose:** Centralized, reusable, immutable test data structures for unit, integration, and scenario testing.

---

## 1. Available Test Fixtures

| Fixture Name | Category | Scope / Representation | Source Data Origin |
| :--- | :---: | :--- | :--- |
| `valid_baseline_input` | Baseline | $30.00\text{ m}$ span, $7.50\text{ m}$ carriageway, 4 steel plate girders at $3.00\text{ m}\text{ c/c}$, E250 steel, M35 concrete, zero footpath, zero median. | Standard OsdagBridge project defaults (`src/osdagbridge/core/bridge_types/plate_girder/defaults.py`). |
| `modified_geometry_input` | Scaling | $36.00\text{ m}$ span, $8.50\text{ m}$ carriageway, 2 footpaths ($1.50\text{ m}$ each), $0.50\text{ m}$ median, $15^\circ$ skew angle, E350 steel, M40 concrete. | Modified geometry test values designed to exercise cross-section width formulas and transverse grillage meshing. |
| `custom_steel_input` | Materials | Baseline bridge geometry with custom high-strength steel properties ($F_y = 350.0\text{ MPa}$, $F_u = 490.0\text{ MPa}$, $E = 200,000\text{ MPa}$, $\rho = 78.5\text{ kN/m}^3$). | Synthetic custom material configuration matching Indian Standard IS 2062 Grade E350 steel. |
| `custom_concrete_input` | Materials | Baseline bridge geometry with custom high-performance concrete deck properties ($f_{ck} = 45.0\text{ MPa}$, $E = 33,541\text{ MPa}$, $\nu = 0.20$, $\rho = 25.0\text{ kN/m}^3$). | Synthetic custom material configuration matching IRC:112 Grade M45 concrete. |
| `invalid_input_scenario` | Negative | Out-of-bounds inputs: Span = $10.00\text{ m}$ ($< 20.0\text{ m}$ minimum), Carriageway = $-5.00\text{ m}$, Steel Density = $20.0\text{ kN/m}^3$ ($< 50.0\text{ kN/m}^3$ minimum), Skew = $65^\circ$ ($> 45^\circ$ maximum). | Negative boundary test case constructed to verify input validation and boundary clamping mechanisms. |
| `baseline_design_result` | Results | Representative structural analysis and design output dictionary containing per-girder checks (moment, shear, LTB, deflection), deck checks, and transverse cross-bracing checks. | Derived from verified grillage analysis and limit state design checks for a 30m highway bridge. |
| `evidence_tracker` | Tooling | Utility helper for exporting input/output dictionary JSON snapshots and runtime error tracebacks into `test_results/evidence/`. | Automated testing infrastructure helper. |

---

## 2. Data Isolation & Immutability Rules

1. **Independent Test State**: Each fixture generates a fresh dictionary or object instance per test invocation. No mutable global states are shared across tests.
2. **Copy Isolation**: Tests modifying inputs must explicitly work on a copy (`inp = valid_baseline_input.copy()`) to prevent accidental contamination.
3. **No Database Dependencies**: Fixtures operate in-memory without requiring external database connections or active network interfaces.
