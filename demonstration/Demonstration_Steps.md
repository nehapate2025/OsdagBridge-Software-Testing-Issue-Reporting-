# Video Demonstration Protocol & Step-by-Step Script — OsdagBridge

### Project Developer and Ownership

- **Project Name:** OsdagBridge
- **Developer:** Ankit Shukla
- **Creator:** Ankit Shukla
- **Maintained By:** Ankit Shukla
- **Project Type:** Individual Project
- **Project Ownership:** Ankit Shukla

OsdagBridge is an individual software project developed and maintained by Ankit Shukla. The project-specific implementation, customization, testing, documentation, and integration covered by this project are attributed to Ankit Shukla.

---

This document outlines the demonstration workflow, script, and technical procedures for recording the OsdagBridge Software Testing and Issue Reporting demonstration video.

---

## Technical Recording Guidelines (Task 10, Section 12)

- **Resolution:** 1920x1080 (1080p Full HD) or 2560x1440 (1440p)
- **Framerate:** 30 fps or 60 fps
- **Audio:** Clear voiceover commentary or silent recording with clean on-screen annotations
- **Environment:** Clean desktop wallpaper, closed background messaging apps, clear font scaling
- **Tool Recommendation:** OBS Studio, Windows Game Bar (`Win + Alt + R`), or ShareX

---

## Demonstration Workflow

### Part 1: Application Launch & Environment (Estimated: 0:00 – 1:00)
1. **Terminal View:**
   - Open PowerShell or Anaconda Prompt.
   - Show active environment: `conda activate osdagbridge`.
   - Run python verification check:
     ```bash
     python -c "import osdagbridge; print('OsdagBridge Loaded Successfully')"
     ```
2. **GUI Launch:**
   - Execute:
     ```bash
     python -m osdagbridge.desktop.main
     ```
   - Show the OsdagBridge homepage and select the **Plate Girder (Composite/Non-Composite)** design module.
   - Highlight the standard UI layout: Input Dock, 3D CAD Visualization Pane, Output Results Dock, and Message Log.

---

### Part 2: Custom Material Input Workflow (Estimated: 1:00 – 2:30)
1. **Steel Material Customization:**
   - Navigate to the **Material** tab.
   - Switch Steel Grade to `Custom`.
   - Enter custom properties:
     - Yield Strength ($f_y$): `350 MPa` (E350 Grade)
     - Ultimate Tensile Strength ($f_u$): `490 MPa`
     - Elastic Modulus ($E$): `200,000 MPa`
2. **Concrete Deck Customization:**
   - Select Concrete Grade `M40`.
   - Verify characteristic compressive cube strength: $f_{ck} = 40 \text{ MPa}$.
   - Enter custom deck slab thickness: `280 mm` (noting BUG-001 persistence observation).
3. **Reinforcement Customization:**
   - Select Rebar Grade: `Fe 500`.
   - Set transverse rebar diameter: `16 mm` and spacing: `150 mm c/c`.
4. **Execute Design:**
   - Click the **Design** button and observe the solver status log in the console.

---

### Part 3: Consecutive Design Runs & State Persistence (Estimated: 2:30 – 4:00)
1. **Run 1 (Baseline 24m Span):**
   - Note the resulting maximum bending moment ($M_u$), shear demand ($V_u$), and overall girder depth.
2. **Unlock & Modify Geometry (Run 2 — 30m Span):**
   - Click **Unlock Design**.
   - Modify span length from `24.0 m` to `30.0 m`.
   - Click **Design** again.
   - Observe that results update dynamically: required girder depth increases proportionally to span, proving solver re-execution.
3. **Unlock & Modify Geometry (Run 3 — 22m Span):**
   - Change span to `22.0 m` and girder count from `4` to `3`.
   - Re-run design.
   - Point out that intermediate stiffness matrices are re-initialized and no stale results remain.

---

### Part 4: Input & Output Dictionary Verification (Estimated: 4:00 – 5:15)
1. **Input Dictionary Inspection:**
   - Open `test_results/evidence/input_dictionary/baseline/baseline_input_snapshot.json`.
   - Show how GUI fields map 1-to-1 to nested dictionary keys (`geometry.span`, `material.steel_grade`).
2. **Output Dictionary Inspection:**
   - Open `test_results/evidence/output_dictionary/baseline/baseline_output_snapshot.json`.
   - Cross-reference the UI Output Dock figures (e.g. Flange Capacity, Web Shear Ratio, Deflection Utilization) against the raw dictionary values to confirm numerical identity.

---

### Part 5: 3D CAD Model & Structural Plots (Estimated: 5:15 – 6:30)
1. **3D CAD Model Navigation:**
   - Switch to the 3D CAD visualization tab.
   - Rotate, pan, and zoom the 3D plate girder bridge superstructure (top flange, web, bottom flange, transverse stiffeners, and concrete deck).
2. **Structural Analysis Plots:**
   - Open and display the generated 3D grillage structural plots:
     - **BMD (Bending Moment Diagram):** `test_results/evidence/cad_plots/structural_plots/bmd_bending_moment_3d.png`
     - **SFD (Shear Force Diagram):** `test_results/evidence/cad_plots/structural_plots/sfd_shear_force_3d.png`
     - **Grillage Model Mesh:** `test_results/evidence/cad_plots/structural_plots/grillage_model_3d.png`
     - **3D Deflection Diagram:** `test_results/evidence/cad_plots/structural_plots/deflection_diagram_3d.png`

---

### Part 6: Automated Testing Suite & Final Report (Estimated: 6:30 – 7:30)
1. **Automated Pytest Execution:**
   - Run in terminal:
     ```bash
     pytest -v --tb=short
     ```
   - Show the live execution of all 95 tests finishing with **90 PASSED, 5 SKIPPED (BLOCKED)** and **0 FAILED**.
2. **Final Deliverables Review:**
   - Open `test_results/final_report/OsdagBridge_Comprehensive_Testing_Report.pdf`.
   - Scroll through the 7-page PDF report highlighting Chapters 1–13, the defect register (BUG-001 to BUG-006), the consolidated results table, and embedded structural plots.
   - Conclude the demonstration.