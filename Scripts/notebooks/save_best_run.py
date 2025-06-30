#!/usr/bin/env python
# coding: utf-8

"""
==================================================================================
 Script Name   : save_best_run.py
 Description   : 
     This script evaluates performance metrics (e.g., KGE) from multiple model 
     simulations, compares them to the current best configuration, and updates 
     the best parameter set if a better one is found.

 Workflow      :
     1. Iterates through error metric files generated from each simulation.
     2. Loads the latest objective function and performance metrics.
     3. Compares current simulation's KGE with the best so far.
     4. If improved:
         - Updates best PARAMS, GENPARM_NEW.TBL, SOILPARM_NEW.TBL.
         - Logs best parameter values into ostIn_Parallel.txt.
         - Appends current performance to tracking files.
     5. If not improved:
         - Appends current results to log files but does not overwrite best files.

 Inputs        :
     - LIS model output error metric files.
     - Simulation-specific configuration and parameter files.

 Outputs       :
     - Updated best parameter files (PARAMS, GENPARM_NEW.TBL, SOILPARM_NEW.TBL).
     - Updated tracking files for objective function and metrics.
     - Appended summary to ostIn_Parallel.txt.
==================================================================================
"""
import os, sys, glob
import pandas as pd
import warnings
from config_paths import *
warnings.filterwarnings('ignore')


error_files = sorted(glob.glob(os.path.join(BASE_DIR, "output", "error_metrix", "*")))

for i in range(len(error_files)):
    try:
        obj_fun = pd.read_csv(os.path.join(BASE_DIR, "FPDDS/obj_function/objective_func.csv"))
        MMMM = pd.read_csv(os.path.join(BASE_DIR, "FPDDS/obj_function/Metrics.csv"))
    except:
        continue

    obj_fun1 = obj_fun.set_index('sn')
    MMMM1 = MMMM.set_index('Latitude')
    ab1 = obj_fun1.objective_function.max()
    key = error_files[i]
    station = pd.read_csv(key)
    a_avg = station['KGE'].mean()
    a_avg1 = pd.DataFrame(a_avg, columns=['sn', 'objective_function'], index=[1])
    a_avg11 = a_avg1.set_index('sn')

    MMMM_avg = station.mean()
    MMMM_avg1 = MMMM_avg.transpose()
    MMMM_avg11 = pd.DataFrame(MMMM_avg1)
    MMMM_avg111 = MMMM_avg11.transpose()
    MMMM_avg1111 = MMMM_avg111.set_index('Latitude')

    if ab1 < a_avg:
        mod_dir = os.path.join(BASE_DIR, f"FPDDS/configs/mod{i}")
        best_dir = os.path.join(BASE_DIR, "FPDDS/best_parm")

        with open(os.path.join(mod_dir, "PARAMS"), 'r', encoding='utf-8') as file:
            best_parm = file.readlines()
        with open(os.path.join(best_dir, "PARAMS"), 'w', encoding='utf-8') as file:
            file.writelines(best_parm)

        colnames = ['a']
        param = pd.read_csv(os.path.join(mod_dir, "PARAMS"), names=colnames, sep=", ")
        HYMAP_runoff_time_delay_multple = param['a'][1]
        HYMAP_river_roughness_multiple = param['a'][2]

        with open(os.path.join(mod_dir, "GENPARM_NEW.TBL"), 'r', encoding='utf-8') as file:
            best_genparm = file.readlines()
        with open(os.path.join(BASE_DIR, "FPDDS/configs/best_parm/GENPARM_NEW.TBL"), 'w', encoding='utf-8') as file:
            file.writelines(best_genparm)

        with open(os.path.join(mod_dir, "SOILPARM_NEW.TBL"), 'r', encoding='utf-8') as file:
            best_soilparm = file.readlines()
        with open(os.path.join(best_dir, "SOILPARM_NEW.TBL"), 'w', encoding='utf-8') as file:
            file.writelines(best_soilparm)

        colnames2 = ['a','b','c','d','e','f','g','h','i','j','k','l']
        colnames1 = ['a']
        soil_param = pd.read_csv(os.path.join(mod_dir, "SOILPARM.TBL"), names=colnames2, sep=", ")
        gen_param = pd.read_csv(os.path.join(mod_dir, "GENPARM.TBL"), names=colnames1, sep=",")

        REFDK_DATA1 = gen_param['a'][21]
        REFKDT_DATA1 = gen_param['a'][23]
        slop_DATA1 = gen_param['a'][3]
        MAXSMC = soil_param['e'][3:16].values
        SATDK = soil_param['h'][3:16].values
        BB = soil_param['b'][3:16].values
        REFSMC = soil_param['f'][3:16].values

        oString = f'{HYMAP_runoff_time_delay_multple} {HYMAP_river_roughness_multiple} {REFDK_DATA1} {REFKDT_DATA1} {slop_DATA1} {MAXSMC[0]} {SATDK[0]} {BB[0]} {REFSMC[0]}\n'

        with open(os.path.join(BASE_DIR, "output/pyLISF/notebooks/ostIn_Parallel.txt"), 'r', encoding='utf-8') as file:
            data = file.readlines()
        data[-2:-2] = [oString]

        with open(os.path.join(BASE_DIR, "FPDDS/configs/ostIn_Parallel.txt"), 'w', encoding='utf-8') as file:
            file.writelines(data)

        obj_fun2 = pd.concat([obj_fun1, a_avg11])
        obj_fun2.to_csv(os.path.join(BASE_DIR, "FPDDS/obj_function/objective_func.csv"))
        MMMM2 = pd.concat([MMMM1, MMMM_avg1111])
        MMMM2.to_csv(os.path.join(BASE_DIR, "FPDDS/obj_function/Metrics.csv"))
        ab2 = obj_fun2.objective_function.max()
        ab21 = pd.DataFrame(ab2, columns=['sn', 'objective_function'], index=[1])
        ab211 = ab21.set_index('sn')
        ab211.to_csv(os.path.join(BASE_DIR, "FPDDS/obj_function/best.csv"))

    else:
        obj_fun2 = pd.concat([obj_fun1, a_avg11])
        obj_fun2.to_csv(os.path.join(BASE_DIR, "FPDDS/obj_function/objective_func.csv"))
        MMMM2 = pd.concat([MMMM1, MMMM_avg1111])
        MMMM2.to_csv(os.path.join(BASE_DIR, "FPDDS/obj_function/Metrics.csv"))
        ab2 = obj_fun2.objective_function.max()
        ab21 = pd.DataFrame(ab2, columns=['sn', 'objective_function'], index=[1])
        ab211 = ab21.set_index('sn')
        ab211.to_csv(os.path.join(BASE_DIR, "FPDDS/obj_function/best.csv"))

