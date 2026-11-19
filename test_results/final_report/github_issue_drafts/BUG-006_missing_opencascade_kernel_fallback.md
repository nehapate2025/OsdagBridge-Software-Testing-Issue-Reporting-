# BUG-006: Missing OpenCASCADE kernel fallback in cad_generator.py aborts headless CAD pipeline

## Description
An issue was identified in module `osdagbridge.core.bridge_types.plate_girder.cad_generator` during the comprehensive test campaign of OsdagBridge.

## Environment
- **Operating System:** Microsoft Windows 11 Home (x64)
- **Python Version:** Python 3.13 / Anaconda Python 3.11/3.12
- **Repository:** https://github.com/Nidhikhare12/OsdagBridge
- **Branch:** main / dev
- **Severity:** Medium
- **Priority:** Low

## Steps to Reproduce
1. In environment without pythonocc-core, execute `from osdagbridge.core.bridge_types.plate_girder.cad_generator import CADGenerator`.
2. Module fails with ModuleNotFoundError.

## Input Configuration
```json
Running CAD generation in Python environment without pythonocc-core installed
```

## Expected Behavior
Module should catch ImportError and provide fallback wireframe/parametric bounding box representation or mock shape.

## Actual Behavior
Unconditional import `from OCC.Core.TopoDS import TopoDS_Shape` raises ModuleNotFoundError, preventing CAD parameter generation.

## Error Message & Traceback
```
ModuleNotFoundError: No module named 'OCC'
Location: src/osdagbridge/core/bridge_types/plate_girder/cad_generator.py:27
```

## Suspected Source Code Location
- **Source File:** `src/osdagbridge/core/bridge_types/plate_girder/cad_generator.py`
- **Function/Method:** `Top-level module import`
- **Affected Key:** `cad_model_shape`

## Root Cause Analysis
Missing conditional import and stub fallback for optional OpenCASCADE rendering engine.

## Suggested Fix
Wrap OCC imports in try/except and provide fallback CADDataTransferObject containing vertices and faces.

## Supporting Evidence
- **Evidence Reference:** `test_results/evidence/cad_plots/cad_verification_summary.csv`
- **Related Test Case:** `OSB-CAD-001`

---
*Status: DRAFT / NOT SUBMITTED*  
*Submission Target: https://github.com/Nidhikhare12/OsdagBridge/issues/new*
