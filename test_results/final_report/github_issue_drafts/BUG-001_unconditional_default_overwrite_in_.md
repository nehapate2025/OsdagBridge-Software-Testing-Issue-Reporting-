# BUG-001: Unconditional Default Overwrite in defaults.py erases customized section and loading parameters

## Description
An issue was identified in module `osdagbridge.core.bridge_types.plate_girder.defaults` during the comprehensive test campaign of OsdagBridge.

## Environment
- **Operating System:** Microsoft Windows 11 Home (x64)
- **Python Version:** Python 3.13 / Anaconda Python 3.11/3.12
- **Repository:** https://github.com/Nidhikhare12/OsdagBridge
- **Branch:** main / dev
- **Severity:** Major
- **Priority:** High

## Steps to Reproduce
1. Build an input dictionary with custom typical_section.deck_thickness = 280.0.
2. Call populate_default_values(input_dict).
3. Inspect input_dict['typical_section']['deck_thickness']. It is reverted to 250.0.

## Input Configuration
```json
typical_section.deck_thickness=280.0 mm, typical_section.wearing_coat_thickness=75.0 mm
```

## Expected Behavior
Custom parameters provided in input_dict should be preserved and not overwritten by defaults.

## Actual Behavior
Helper functions (_update_typical_section_defaults, etc.) unconditionally call input_dict.update({key: val}), resetting user values back to 250.0 and 65.0.

## Error Message & Traceback
```
AssertionError: Expected custom deck thickness 280.0, but got default 250.0
Location: tests/unit/test_input_dictionary.py:test_custom_deck_thickness_persistence
```

## Suspected Source Code Location
- **Source File:** `src/osdagbridge/core/bridge_types/plate_girder/defaults.py`
- **Function/Method:** `_update_typical_section_defaults, _update_loading_tab_defaults`
- **Affected Key:** `typical_section.deck_thickness, typical_section.wearing_coat_thickness`

## Root Cause Analysis
The inner closure `def _update(key, value): input_dict.update({key: value})` performs unconditional overwrite instead of checking `if input_dict.get(key) is None:`.

## Suggested Fix
Change helper to `def _update(key, value): if key not in input_dict or input_dict[key] is None: input_dict[key] = value`.

## Supporting Evidence
- **Evidence Reference:** `test_results/evidence/input_dictionary/geometry/geometry_input_snapshot.json`
- **Related Test Case:** `OSB-INP-007`

---
*Status: DRAFT / NOT SUBMITTED*  
*Submission Target: https://github.com/Nidhikhare12/OsdagBridge/issues/new*
