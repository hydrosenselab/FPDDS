#!/usr/bin/env python
# coding: utf-8

"""
==================================================================================
 Script Name   : model_run.py
 Description   :
     This script automates the parallel execution of multiple Land Surface Model (LSM)
     runs using LIS (Land Information System), followed by post-processing and parameter
     evaluation using custom Python utilities. The workflow integrates Ostrich for 
     parameter optimization and maintains a structured logging and backup system.

 Workflow      :
     1. Parallel execution of LIS model simulations for multiple configurations (mod1–mod4)
     2. Post-processing using a custom script (`run_process_lsm.py`) to evaluate LSM performance
     3. Execution of calibration evaluation scripts (`save_best_run.py` and `multiplire.py`)
     4. Running Ostrich optimization via MPI for parameter tuning
     5. Backup of generated configuration and error metric files for each outer iteration `j`
 Notes         :
     - Modify the `range(0,35)` loop for outer iterations as required for total number of cycles
     - Ensure LIS, Python environments, and Ostrich paths are properly set
     - Assumes Slurm/cluster modules are manually loaded via `module load`
     - Requires `geo_env` conda environment with necessary Python packages

 Dependencies  :
     - process_lsm_output (imported from `process_lsm_output.py`)
     - External Python scripts: `save_best_run.py`, `multiplire.py`
     - OstrichMPI executable
==================================================================================
"""

import os, sys, glob
import subprocess
import multiprocessing
from multiprocessing import Pool
import shutil
from process_lsm_output import process_lsm_output
from config_paths import *

# ======== MAIN ITERATION LOOP ========
for j in range(0, 35):

    def run_model(model_id):
        shell_script = f"""
        cd {BASE_DIR}
        module purge
        module load lib/intel/2019/eccodes/2.18.0
        module load lib/intel/2019/esmf/8.0.0
        module load lib/intel/2019/hdfeos/2.20v1.10
        module swap suite/intel/parallelStudio/2019 suite/intel/parallelStudio/2018

        time -p mpirun -np 4 /home/civil/phd/cez218606/LISF1/LISF-7.4/LISF/lis/LIS -f {BASE_DIR}/LIS_IMD_{model_id}
        cd {NOTEBOOK_DIR}
        ~/anaconda3/envs/geo_env/bin/python {NOTEBOOK_DIR}/run_process_lsm.py LSM_IMD{model_id}
        """
        output_log = os.path.join(BASE_DIR, "logs", f"output_mp_{model_id}.txt")
        error_log = os.path.join(BASE_DIR, "logs", f"error_mp_{model_id}.txt")

        with open(output_log, "w") as out, open(error_log, "w") as err:
            process = subprocess.run(shell_script, shell=True, executable="/bin/bash", stdout=out, stderr=err)

        if process.returncode == 0:
            print(f"Model run {model_id} completed successfully.")
        else:
            print(f"Model run {model_id} failed with return code: {process.returncode}")
        return process.returncode

    model_ids = [1, 2, 3, 4]

    if __name__ == "__main__":
        with Pool(processes=4) as pool:
            results = pool.map(run_model, model_ids)

        if all(code == 0 for code in results):
            print("All model runs completed successfully.")
        else:
            print("Some model runs failed.")

    def run_job(job_id):
        shell_script = f"""
        cd {NOTEBOOK_DIR}
        ~/anaconda3/envs/geo_env/bin/python {NOTEBOOK_DIR}/save_best_run.py

        cd {BASE_DIR}/FPDDS/configs/
        cp ostIn_Parallel.txt ostIn.txt
        echo 0 > Counter.txt
        module load lib/intel
        export I_MPI_PMI_LIBRARY=/usr/lib64/libpmi.so
        mpirun -n 4 {BASE_DIR}/FPDDS/Linux/intelmpi/5.1.1/OstrichMPI

        cd {NOTEBOOK_DIR}
        ~/anaconda3/envs/geo_env/bin/python {NOTEBOOK_DIR}/multiplire.py
        """
        output_log = os.path.join(BASE_DIR, "logs", f"output_mo_{job_id}.txt")
        error_log = os.path.join(BASE_DIR, "logs", f"error_mo_{job_id}.txt")

        with open(output_log, "w") as out_log, open(error_log, "w") as err_log:
            subprocess.run(shell_script, shell=True, stdout=out_log, stderr=err_log)

    run_job(job_id=1)

    for i in range(0, 4):
        path1 = os.path.join(BASE_DIR, f'FPDDS/param_save/er{j}/mod{i}')
        path2 = os.path.join(BASE_DIR, f'FPDDS/configs/mod{i}')
        path3 = os.path.join(BASE_DIR, 'output/error_metrix/')

        os.makedirs(path1, exist_ok=True)

        for file_name in os.listdir(path2):
            full_file_name = os.path.join(path2, file_name)
            if os.path.isfile(full_file_name):
                shutil.copy(full_file_name, path1)

        for file_name in os.listdir(path3):
            full_file_name = os.path.join(path3, file_name)
            if os.path.isfile(full_file_name):
                shutil.copy(full_file_name, path1)

    print(f'✅ j iteration {j} completed')

