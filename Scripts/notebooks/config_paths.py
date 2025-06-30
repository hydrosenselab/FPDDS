"""
config_paths.py

📁 Purpose:
This module defines all the file and directory paths used in the Narmada_FPDDS11
auto-calibration and simulation workflow. It centralizes configuration paths to ensure
that the main scripts remain clean, modular, and easily maintainable.

📌 Key Contents:
- BASE_DIR: Root directory for the entire calibration-experiment setup.
- Executable paths for LIS and Ostrich hydrologic/hydrodynamic models.
- Python environment used for post-processing tasks.

✅ Usage:
Import this module in your main scripts using:
    from config_paths import *
"""



import os

# === Base Directory for the Narmada FPDDS11 project ===
BASE_DIR = "/home/civil/phd/cez218606/Auto_calibration/Final/Narmada_FPDDS11"

# === LIS Routing and Executables ===
LIS_EXECUTABLE = "/home/civil/phd/cez218606/LISF1/LISF-7.4/LISF/lis/LIS"
OSTRICH_EXECUTABLE = os.path.join(BASE_DIR, "FPDDS/Linux/intelmpi/5.1.1/OstrichMPI")

# === Python Environment Executable ===
PYTHON_EXECUTABLE = "~/anaconda3/envs/geo_env/bin/python"

# === LSM Input Script Path ===
LSM_PROCESS_SCRIPT = os.path.join(BASE_DIR, "run_process_lsm.py")

# === Notebook Scripts ===
NOTEBOOK_DIR = os.path.join(BASE_DIR, "FPDDS/Scripts/notebooks")
