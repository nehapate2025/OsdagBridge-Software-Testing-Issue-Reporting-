# BUG-005: In-place division of girder dimensions in _convert_girder_dims_mm_to_m() causes non-idempotent distortion

## Description
An issue was identified in module `osdagbridge.core.bridge_types.plate_girder.plategirderbridge` during the comprehensive test campaign of OsdagBridge.

## Environment
- **Operating System:** Microsoft Windows 11 Home (x64)
- **Python Version:** Python 3.13 / Anaconda Python 3.11/3.12
- **Repository:** https://github.com/Nidhikhare12/OsdagBridge
- **Branch:** main / dev
- **Severity:** Major
- **Priority:** High

## Steps to Reproduce
1. Pass input_dict with girder depth = 1800.0 mm.
2. Call _convert_girder_dims_mm_to_m(input_dict) -> depth = 1.8 m.
3. Call _convert_girder_dims_mm_to_m(input_dict) again -> depth = 0.0018 m.
4. Downstream design crashes with unrealistic geometry.

## Input Configuration
```json
Consecutive design runs or multiple calls to _convert_girder_dims_mm_to_m() on shared input dictionary
```

## Expected Behavior
Dimension conversion should be idempotent or operate on a copy of geometric properties.

## Actual Behavior
Modifies dictionary in-place by dividing values by 1000.0 without checking if conversion was already applied. Second run divides by 1,000,000.

## Error Message & Traceback
```
ValueError: Girder depth 0.0018 m is below minimum allowable span depth
Location: src/osdagbridge/core/bridge_types/plate_girder/plategirderbridge.py:542
```

## Suspected Source Code Location
- **Source File:** `src/osdagbridge/core/bridge_types/plate_girder/plategirderbridge.py`
- **Function/Method:** `_convert_girder_dims_mm_to_m()`
- **Affected Key:** `girder.overall_depth, girder.web_thickness, girder.flange_width`

## Root Cause Analysis
In-place dictionary mutation of raw geometric inputs without dimension flag tracking.

## Suggested Fix
Create a converted copy of the geometry dictionary or tag dictionary with `_dimensions_converted_to_m = True` before dividing.

## Supporting Evidence
- **Evidence Reference:** `test_results/evidence/consecutive_runs/run2_design_summary.json`
- **Related Test Case:** `OSB-RUN-002`

---
*Status: DRAFT / NOT SUBMITTED*  
*Submission Target: https://github.com/Nidhikhare12/OsdagBridge/issues/new*
