#!/usr/bin/env python
# coding: utf-8

"""
==================================================================================
 Script Name   : multiplire.py
 Description   : 
     This script updates parameter tables for hydrological modeling based on 
     new calibration results. It modifies SOILPARM and GENPARM tables, applies 
     multiplicative adjustments to relevant parameters, and regenerates updated 
     LIS input NetCDF files for each model realization.

 Workflow      :
     1. Iterates over model output folders (based on error files present).
     2. Loads both the new and previously best parameter files:
         - SOILPARM.TBL
         - GENPARM.TBL
     3. Computes scaling multipliers for selected soil and general parameters.
     4. Updates SOILPARM_NEW.TBL and GENPARM_NEW.TBL with scaled parameters.
     5. Reads LIS NetCDF input file and clips selected variables using a 
        watershed shapefile.
     6. Updates HYMAP-specific variables (e.g., runoff delay, roughness) by 
        applying the corresponding multiplicative factors.
     7. Writes updated NetCDF files with modified variables for each ensemble.

 Inputs        :
     - Calibrated parameter files: SOILPARM.TBL, GENPARM.TBL
     - Best parameter files: SOILPARM_NEW.TBL, GENPARM_NEW.TBL
     - LIS NetCDF input file
     - River basin shapefile

 Outputs       :
     - Updated parameter tables: SOILPARM_NEW.TBL, GENPARM_NEW.TBL
     - Modified LIS input NetCDFs named: lis_input_ildas_noahmp401_010_Narmada_*.nc
==================================================================================
"""



import os, sys, glob
import pandas as pd
import xarray as xr
import numpy as np
import geopandas
from shapely.geometry import mapping
import rioxarray
from config_paths import *
from lis import *
import warnings
warnings.filterwarnings('ignore')


# Read error files
error_files = sorted(glob.glob(os.path.join(BASE_DIR, 'output/error_metrix/*')))

for i in range(len(error_files)):
    colnames = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l']
    colnames1 = ['a']

    soil_param_new = pd.read_csv(os.path.join(BASE_DIR, f'FPDDS/configs/mod{i}/SOILPARM.TBL'), names=colnames, sep=", ")
    soil_param_old = pd.read_csv(os.path.join(BASE_DIR, 'FPDDS/best_parm/SOILPARM_NEW.TBL'), names=colnames, sep=", ")
    gen_param_new = pd.read_csv(os.path.join(BASE_DIR, f'FPDDS/configs/mod{i}/GENPARM.TBL'), names=colnames1, sep=",")
    gen_param_old = pd.read_csv(os.path.join(BASE_DIR, 'FPDDS/best_parm/GENPARM_NEW.TBL'), names=colnames1, sep=", ")

    BB_new = soil_param_new['b'][3]
    MAXSMC_new = soil_param_new['e'][3]
    REFSMC_new = soil_param_new['f'][3]
    SATDK_new = soil_param_new['h'][3]
    slop_new = float(gen_param_new['a'][3])

    BB_old = soil_param_old['b'][3]
    MAXSMC_old = soil_param_old['e'][3]
    REFSMC_old = soil_param_old['f'][3]
    SATDK_old = soil_param_old['h'][3]
    slop_old = float(gen_param_old['a'][3])

    BB_mult = BB_new / BB_old
    MAXSMC_mult = MAXSMC_new / MAXSMC_old
    REFSMC_mult = REFSMC_new / REFSMC_old
    SATDK_mult = SATDK_new / SATDK_old
    slop_mult = slop_new / slop_old

    BB = soil_param_old['b'][3:14].values
    MAXSMC = soil_param_old['e'][3:14].values
    REFSMC = soil_param_old['f'][3:14].values
    SATDK = soil_param_old['h'][3:14].values

    BB_best = BB * BB_mult
    MAXSMC_best = MAXSMC * MAXSMC_mult
    REFSMC_best = REFSMC * REFSMC_mult
    SATDK_best = SATDK * SATDK_mult

    slop1 = float(gen_param_old['a'][4]) * slop_mult
    slop2 = float(gen_param_old['a'][6]) * slop_mult
    slop3 = float(gen_param_old['a'][7]) * slop_mult
    slop4 = float(gen_param_old['a'][8]) * slop_mult
    slop5 = float(gen_param_old['a'][9]) * slop_mult

    with open(os.path.join(BASE_DIR, 'FPDDS/best_parm/SOILPARM_NEW.TBL'), 'r', encoding='utf-8') as file:
        data = file.readlines()

    mm = [line.split() for line in data[3:14]]

    oStrings = [
        f"{mm[i][0]}    {BB_new if i == 0 else BB_best[i]},    {mm[i][2]}    {mm[i][3]}    {MAXSMC_new if i == 0 else MAXSMC_best[i]},    {REFSMC_new if i == 0 else REFSMC_best[i]},    {mm[i][6]}    {SATDK_new if i == 0 else SATDK_best[i]},    {'    '.join(mm[i][8:])}\n"
        for i in range(11)
    ]

    data[3:14] = oStrings

    with open(os.path.join(BASE_DIR, f'FPDDS/configs/mod{i}/SOILPARM_NEW.TBL'), 'w') as file:
        file.writelines(data)

    with open(os.path.join(BASE_DIR, f'FPDDS/configs/mod{i}/GENPARM.TBL'), 'r', encoding='utf-8') as file:
        data1 = file.readlines()
    with open(os.path.join(BASE_DIR, f'FPDDS/configs/mod{i}/GENPARM.TBL'), 'r', encoding='utf-8') as file:
        data2 = file.readlines()

    data2[4] = f'{slop1}\n'
    data2[6] = f'{slop2}\n'
    data2[7] = f'{slop3}\n'
    data2[8] = f'{slop4}\n'
    data2[9] = f'{slop5}\n'
    data2[21] = data1[21]
    data2[23] = data1[23]

    with open(os.path.join(BASE_DIR, f'FPDDS/configs/mod{i}/GENPARM_NEW.TBL'), 'w') as file:
        file.writelines(data2)

for i in range(len(error_files)):
    PARM = pd.read_csv(os.path.join(BASE_DIR, f'FPDDS/configs/mod{i}/PARAMS'))
    ds = xr.open_dataset(os.path.join(BASE_DIR, 'lis_input_files/lis_input_ildas_noahmp401_010.nc'))
    ds1 = xr.open_dataset(os.path.join(BASE_DIR, 'lis_input_files/lis_input_ildas_noahmp401_010.nc'))
    mask = geopandas.read_file(os.path.join(BASE_DIR, 'FPDDS/Scripts/shapefiles/narmada.shp'))

    a = reformat_LIS_output(ds)
    aa = a.LANDMASK
    bb = a.DOMAINMASK
    cc = a.HYMAP_runoff_time_delay
    dd = a.HYMAP_river_roughness

    for var in [aa, bb, cc, dd]:
        var.rio.set_spatial_dims(x_dim="lon", y_dim="lat", inplace=True)
        var.rio.write_crs("epsg:4326", inplace=True)

    lsm_clip = aa.rio.clip(mask.geometry.apply(mapping), mask.crs, drop=True)
    lsm_clip1 = bb.rio.clip(mask.geometry.apply(mapping), mask.crs, drop=True)
    lsm_clip2 = cc.rio.clip(mask.geometry.apply(mapping), mask.crs, drop=True)
    lsm_clip3 = dd.rio.clip(mask.geometry.apply(mapping), mask.crs, drop=True)

    a = a.assign(LANDMASK=lsm_clip, DOMAINMASK=lsm_clip1, HYMAP_runoff_time_delay=cc, HYMAP_river_roughness=dd)

    aaa = a.LANDMASK.fillna(0)
    aaa1 = a.DOMAINMASK.fillna(0)
    aaa2 = a.HYMAP_runoff_time_delay * PARM.Parameters[0]
    aaa3 = a.HYMAP_river_roughness * PARM.Parameters[1]

    lat = np.arange(5.0499, 37.95, 0.1).reshape(330, 1).repeat(355, axis=1)
    lon = np.arange(64.5499, 99.95, 0.1).reshape(1, 355).repeat(330, axis=0)

    def make_ds(name, data):
        return xr.Dataset({
            name: xr.DataArray(data=data, dims=["north_south", "east_west"],
                               coords={"lon": (["north_south", "east_west"], lon),
                                       "lat": (["north_south", "east_west"], lat)})
        })

    ds1['LANDMASK'] = make_ds('LANDMASK', aaa).LANDMASK.drop(['lon', 'lat'])
    ds1['DOMAINMASK'] = make_ds('DOMAINMASK', aaa1).DOMAINMASK.drop(['lon', 'lat'])
    ds1['HYMAP_runoff_time_delay'] = make_ds('HYMAP_runoff_time_delay', aaa2).HYMAP_runoff_time_delay.drop(['lon', 'lat'])
    ds1['HYMAP_river_roughness'] = make_ds('HYMAP_river_roughness', aaa3).HYMAP_river_roughness.drop(['lon', 'lat'])

    ds1.to_netcdf(os.path.join(BASE_DIR, f'lis_input_files/lis_input_ildas_noahmp401_010_Narmada_{i}.nc'))

# In[ ]:

