# BUG-002: Direct PySide6 GUI Widget Import in Core Schema Module breaks headless execution

## Description
An issue was identified in module `osdagbridge.core.bridge_types.plate_girder.ui_fields_additional_input` during the comprehensive test campaign of OsdagBridge.

## Project Developer & Author
- **Project Name:** OsdagBridge
- **Developer & Author:** Ankit Shukla (Sole Individual Developer — Individual Project)

## Environment
- **Operating System:** Microsoft Windows 11 Home (x64)
- **Python Version:** Python 3.13 / Anaconda Python 3.11/3.12
- **Repository:** https://github.com/osdag-admin/OsdagBridge
- **Branch:** main / dev
- **Severity:** Medium
- **Priority:** Medium

## Steps to Reproduce
1. Set QT_QPA_PLATFORM=offscreen or run in environment without PySide6 GUI plugins.
2. Import ui_fields_additional_input.
3. Python crashes with QApplication initialization failure.

## Input Configuration
```json
Headless CLI execution: python -c 'import osdagbridge.core.bridge_types.plate_girder.ui_fields_additional_input'
```

## Expected Behavior
Core data schema modules should be pure Python and importable without Qt GUI platform plugin initialized.

## Actual Behavior
Module executes `from osdagbridge.desktop.ui.docks.cad_cross_section import CrossSectionCADWidget` at top level, crashing if DISPLAY/QApplication is absent.

## Error Message & Traceback
```
qt.qpa.plugin: Could not load the Qt platform plugin 'xcb' / 'windows' in headless environment
Location: src/osdagbridge/core/bridge_types/plate_girder/ui_fields_additional_input.py:331
```

## Suspected Source Code Location
- **Source File:** `src/osdagbridge/core/bridge_types/plate_girder/ui_fields_additional_input.py`
- **Function/Method:** `Top-level module import`
- **Affected Key:** `N/A (Schema Architecture)`

## Root Cause Analysis
Hard architectural coupling between core business logic and desktop Qt UI layer.

## Suggested Fix
Move Qt widget instantiation into desktop/ui adapter layer or wrap inside `try...except ImportError` / deferred import inside UI factory methods.

## Supporting Evidence
- **Evidence Reference:** `tests/unit/test_input_validation.py (headless run skips)`
- **Related Test Case:** `OSB-INP-011`

---
*Status: DRAFT / NOT SUBMITTED*  
*Submission Target: https://github.com/osdag-admin/OsdagBridge/issues/new*
