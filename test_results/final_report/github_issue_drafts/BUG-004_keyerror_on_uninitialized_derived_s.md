# BUG-004: KeyError on uninitialized derived shear stud parameters in 3D CAD parameter generation

## Description
An issue was identified in module `osdagbridge.core.bridge_types.plate_girder.plategirderbridge` during the comprehensive test campaign of OsdagBridge.

## Environment
- **Operating System:** Microsoft Windows 11 Home (x64)
- **Python Version:** Python 3.13 / Anaconda Python 3.11/3.12
- **Repository:** https://github.com/Nidhikhare12/OsdagBridge
- **Branch:** main / dev
- **Severity:** Medium
- **Priority:** Medium

## Steps to Reproduce
1. Instantiate PlateGirderBridge.
2. Call bridge.get_3d_cad_parameters() without calling bridge.design().
3. KeyError crashes process.

## Input Configuration
```json
PlateGirderBridge instance before design execution or after partial design failure calling get_3d_cad_parameters()
```

## Expected Behavior
CAD parameter extractor should gracefully check for component keys and return None/default if shear stud solver has not completed.

## Actual Behavior
Direct indexing `output_dict[KEY_DS_STUD_HEAD_DIAMETER]` raises unhandled KeyError, aborting 3D geometry generation.

## Error Message & Traceback
```
KeyError: 'stud_head_diameter'
Location: src/osdagbridge/core/bridge_types/plate_girder/plategirderbridge.py:3635
```

## Suspected Source Code Location
- **Source File:** `src/osdagbridge/core/bridge_types/plate_girder/plategirderbridge.py`
- **Function/Method:** `PlateGirderBridge.get_3d_cad_parameters()`
- **Affected Key:** `stud_head_diameter, stud_shank_length`

## Root Cause Analysis
Direct dictionary lookup without `.get()` fallback for derived shear connector parameters.

## Suggested Fix
Use `output_dict.get(KEY_DS_STUD_HEAD_DIAMETER, default_stud_dia)` with validation.

## Supporting Evidence
- **Evidence Reference:** `test_results/evidence/cad_plots/cad_verification_summary.csv`
- **Related Test Case:** `OSB-CAD-004`

---
*Status: DRAFT / NOT SUBMITTED*  
*Submission Target: https://github.com/Nidhikhare12/OsdagBridge/issues/new*
