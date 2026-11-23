# Environment Setup Guide — OsdagBridge

### Project Developer and Ownership

**Developed By: Neha Patel**

- **Project Name:** OsdagBridge
- **Developer:** Neha Patel
- **Creator:** Neha Patel
- **Maintained By:** Neha Patel
- **Project Type:** Individual Project
- **Project Ownership:** Neha Patel

OsdagBridge is an individual software project developed and created exclusively by Neha Patel. The project-specific implementation, customization, testing, documentation, and integration covered by this project are attributed to Neha Patel.

---

This guide provides instructions for setting up the development, analysis, and verification environment for **OsdagBridge** (Short-Span Steel Plate Girder Highway Bridge Design Module).

---

## 1. System Requirements

- **Operating System:** Windows 10/11 (64-bit), Ubuntu Linux 20.04/22.04 LTS, or macOS 12+
- **Processor:** Dual-core 2.0 GHz or higher (x86_64 architecture)
- **RAM:** 8 GB minimum (16 GB recommended for large finite element grillage models)
- **Disk Space:** 5 GB free disk space
- **Graphics:** OpenGL 2.1+ compatible GPU for 3D OpenCASCADE rendering

---

## 2. Python Environment Setup

We recommend using **Anaconda** or **Miniconda** to manage dependencies.

### Step 2.1: Clone or Open the Repository
```bash
git clone https://github.com/osdag-admin/OsdagBridge.git
cd OsdagBridge
```

### Step 2.2: Create Conda Environment
Use the provided `environment.yml`:
```bash
conda env create -f environment.yml
conda activate osdagbridge
```

Alternatively, create an environment manually with Python 3.11:
```bash
conda create -n osdagbridge python=3.11 -y
conda activate osdagbridge
```

### Step 2.3: Install Required Dependencies
Install the required scientific, GUI, FE analysis, and reporting libraries:
```bash
pip install -r requirements.txt
```
Key packages include:
- `PySide6`: Desktop GUI application framework
- `numpy`, `scipy`, `pandas`: Numerical computations and tabular data handling
- `matplotlib`: 2D/3D plotting and structural response diagrams
- `reportlab`: Automated PDF design report generation
- `pyyaml`: YAML parsing for `.osi` input files and project configurations
- `pytest`: Automated testing framework
- `OpenSeesPy`: Finite element grillage analysis engine (optional native binary)
- `pythonocc-core`: OpenCASCADE 3D solid modeling kernel (conda-forge)

---

## 3. Verifying Installation

To verify that the core libraries and design solver are accessible:
```bash
python -c "import osdagbridge; print('OsdagBridge successfully loaded!')"
```

To run the automated verification suite:
```bash
pytest -v
```

---

## 4. Headless Runner Notes

For CI/CD or server environments without a physical display:
- Set `QT_QPA_PLATFORM=offscreen` to allow PySide6 components to initialize in headless mode.
- In Linux runners, install `xvfb` (`xvfb-run pytest -v`) to execute GUI integration tests.
