# Known Issues & Defect Tracking — OsdagBridge

### Project Developer and Ownership

**Developed By: Yoshita Namdev**

- **Project Name:** OsdagBridge
- **Developer:** Yoshita Namdev
- **Creator:** Yoshita Namdev
- **Maintained By:** Yoshita Namdev
- **Project Type:** Individual Project
- **Project Ownership:** Yoshita Namdev

OsdagBridge is an individual software project developed and created exclusively by Yoshita Namdev. The project-specific implementation, customization, testing, documentation, and integration covered by this project are attributed to Yoshita Namdev.

---

This document tracks all confirmed software defects, limitations, and architectural issues discovered during the testing campaign of the **OsdagBridge** short-span steel plate girder module.

---

## 1. Confirmed Software Defects

Detailed root cause analyses and code patches are cataloged in [`test_results/final_report/bug_register.csv`](file:///c:/Users/acer/Downloads/OsdagBridge-dev/test_results/final_report/bug_register.csv) and markdown drafts under [`test_results/final_report/github_issue_drafts/`](file:///c:/Users/acer/Downloads/OsdagBridge-dev/test_results/final_report/github_issue_drafts/).

### BUG-001: Unconditional Default Overwrite in `defaults.py`
- **Severity:** Major | **Priority:** High
- **Affected File:** `src/osdagbridge/core/bridge_types/plate_girder/defaults.py`
- **Symptom:** User-customized deck thickness or wearing coat depths are reset to default values (`250.0 mm` and `65.0 mm`) upon calling default population helpers.
- **Root Cause:** Helper closure `def _update(key, value): input_dict.update({key: value})` mutates dictionary unconditionally without verifying if key already has user-supplied values.
- **Suggested Fix:** Guard updates with `if key not in input_dict or input_dict[key] is None: input_dict[key] = value`.

### BUG-002: Direct GUI Widget Import in Core Schema Module
- **Severity:** Medium | **Priority:** Medium
- **Affected File:** `src/osdagbridge/core/bridge_types/plate_girder/ui_fields_additional_input.py`
- **Symptom:** Headless scripts and server pipelines crash with Qt platform plugin errors on import.
- **Root Cause:** Direct top-level import `from osdagbridge.desktop.ui.docks.cad_cross_section import CrossSectionCADWidget` couples the core schema directly to PySide6 UI widgets.
- **Suggested Fix:** Decouple widget instantiation or use lazy import inside UI factory functions.

### BUG-003: Premature `MappingProxyType` Freeze on `output_dict`
- **Severity:** Minor | **Priority:** Low
- **Affected File:** `src/osdagbridge/core/bridge_types/plate_girder/plategirderbridge.py`
- **Symptom:** Downstream report engines cannot augment output dictionary with execution timestamps or job metadata.
- **Root Cause:** Setting `self.output_dict = types.MappingProxyType(self.output_dict)` prevents item assignment.
- **Suggested Fix:** Keep dictionary mutable or provide explicit `.copy()` method for downstream consumers.

### BUG-004: `KeyError` on Uninitialized Shear Stud Parameters in CAD Generator
- **Severity:** Medium | **Priority:** Medium
- **Affected File:** `src/osdagbridge/core/bridge_types/plate_girder/plategirderbridge.py`
- **Symptom:** Invoking CAD parameter extraction before full solver completion raises unhandled `KeyError`.
- **Root Cause:** Direct dictionary lookup `output_dict[KEY_DS_STUD_HEAD_DIAMETER]` assumes prior solver execution.
- **Suggested Fix:** Use safe dictionary access: `output_dict.get(KEY_DS_STUD_HEAD_DIAMETER, default_value)`.

### BUG-005: Non-Idempotent Dimension Division in `_convert_girder_dims_mm_to_m()`
- **Severity:** Major | **Priority:** High
- **Affected File:** `src/osdagbridge/core/bridge_types/plate_girder/plategirderbridge.py`
- **Symptom:** Consecutive design runs on the same input dictionary divide girder dimensions by 1,000 repeatedly.
- **Root Cause:** In-place division without tracking dimension unit status flag.
- **Suggested Fix:** Tag dictionary with `_dimensions_converted_to_m = True` or operate on deep-copied dictionary.

### BUG-006: Missing OpenCASCADE Kernel Fallback in `cad_generator.py`
- **Severity:** Medium | **Priority:** Low
- **Affected File:** `src/osdagbridge/core/bridge_types/plate_girder/cad_generator.py`
- **Symptom:** Crash on systems without `pythonocc-core` installed.
- **Root Cause:** Top-level import `from OCC.Core.TopoDS import TopoDS_Shape` lacks exception handling.
- **Suggested Fix:** Wrap OCC imports in `try...except ImportError` and provide fallback bounding box representation.

---

## 2. Environmental Limitations

1. **Headless Execution:** 5 interactive GUI modal tests in PySide6 require a virtual framebuffer (`xvfb`) on headless Linux runners.
2. **OpenCASCADE Kernel:** Full 3D solid geometry viewing requires native `pythonocc-core` packages typically installed via `conda-forge`.