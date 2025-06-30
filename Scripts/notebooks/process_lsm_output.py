
"""
==================================================================================
 Script Name   : process_lsm_output.py
 Description   : 
     This script evaluates hydrologic model outputs (from HyMAP routing) over the Narmada basin. It processes simulated 
     streamflow, validates against observed station data, and computes statistical 
     performance metrics such as KGE, NSE, and RMSE.

 Workflow      :
     1. Identify and load routing output files for the specified LSM.
     2. Identify valid observed stations with sufficient data (≥ 5 years).
     3. Save valid observations and routing simulations for each station.
     4. Merge simulated and observed time series data.
     5. Compute error metrics (e.g., PBIAS, NSE, KGE, RMSE, R²) for each station.
     6. Save a summary error matrix as a CSV file.

 Modules Used  :
     - `lis`: Custom module to reformat LIS routing NetCDF outputs.
     - `objectives`: Custom metrics functions (e.g., KGE, NSE).

 Inputs        :
     - LSM name (e.g., "LSM_IMD1")
     - LIS routing output NetCDF files per realization
     - Observed streamflow CSV files
     - Meta file with gauge information (lat, lon, IDs)

 Outputs       :
     - Processed simulated and observed CSVs for each station
     - Merged data for comparison
     - Final error matrix saved to: output/error_metrix/error_matrix{lsm_number}.csv

 Notes         :
     - Assumes observations are stored as 'IWM-gauge-XXX.csv'
     - Observed files must include 'Streamflow (cumecs)' and 'Date'
     - Computation period is fixed to '2001-01-01' to '2003-12-31'
==================================================================================
"""




import os, sys, glob, gc, warnings
import numpy as np
import pandas as pd
import xarray as xr
import dask
from lis import *
from objectives import *
from config_paths import *
from dask import delayed, compute
from tqdm import tqdm

warnings.filterwarnings("ignore")



def process_lsm_output(lsm_name):
    print(f"🔄 Processing for LSM: {lsm_name}")

    # Extract LSM number (e.g., "LSM_IMD1" → "1")
    lsm_number = ''.join(filter(str.isdigit, lsm_name))

    routing_path = os.path.join(BASE_DIR, "output", lsm_name, "ROUTING")
    obs_dir = os.path.join(BASE_DIR, "output", "Narmada")
    processed_dir = os.path.join(BASE_DIR, "output", f"processed_data{lsm_number}")
    error_output_path = os.path.join(BASE_DIR, "output", "error_metrix", f"error_matrix{lsm_number}.csv")

    os.makedirs(processed_dir, exist_ok=True)
    os.makedirs(os.path.dirname(error_output_path), exist_ok=True)

    # Step 1: Collect routing files
    route_files = sorted(glob.glob(os.path.join(routing_path, "*", "*HIST*")))

    # Step 2: Validate stations
    def valid_stations(read_dir, min_values, key):
        try:
            key_4 = format(key, "03")
            gauge_id = f'IWM-gauge-{key_4}'
            station = pd.read_csv(os.path.join(read_dir, gauge_id + '.csv')).dropna(subset=['Streamflow (cumecs)'])
            if station['Streamflow (cumecs)'].count() >= min_values:
                return gauge_id
        except Exception:
            return

    min_values = 5 * 365
    n_stations = 3900
    dask_results = [delayed(valid_stations)(obs_dir, min_values, k) for k in range(n_stations)]
    valid_station_list = [res for res in compute(*dask_results) if res is not None]

    for key in valid_station_list:
        df = pd.read_csv(os.path.join(obs_dir, key + '.csv')).set_index('Date')
        df.to_csv(os.path.join(processed_dir, key + '-obs.csv'))

    pd.DataFrame({'stations': valid_station_list}).to_csv(
        os.path.join(processed_dir, 'valid_stations_list.csv'), index=False
    )

    # Step 3: Extract routed data
    meta_file = pd.read_csv(os.path.join(obs_dir + '.csv')).set_index('GaugeID')
    route_vars = ['Streamflow_tavg']
    routedat = xr.open_mfdataset(route_files, combine='by_coords', parallel=True)
    routedat = reformat_LIS_output(routedat).compute()

    batch_vars = [None] * len(valid_station_list)
    merged_vars = [None] * len(valid_station_list)

    for i, gauge_id in enumerate(valid_station_list):
        lat = meta_file.loc[gauge_id, 'Latitude']
        lon = meta_file.loc[gauge_id, 'Longitude']
        sel = routedat.sel(lat=lat, lon=lon, method='nearest')
        ext = sel[route_vars].to_dataframe().drop(['lat', 'lon'], axis=1, errors='ignore')
        batch_vars[i] = ext
        merged_vars[i] = ext

    del routedat
    gc.collect()

    for i, key in enumerate(valid_station_list):
        merged_vars[i].to_csv(os.path.join(processed_dir, key + '-sim.csv'))

    # Step 4: Merge with observations
    for key in valid_station_list:
        obs = pd.read_csv(os.path.join(processed_dir, key + '-obs.csv'), index_col='Date', parse_dates=True)
        sim = pd.read_csv(os.path.join(processed_dir, key + '-sim.csv'), index_col='time', parse_dates=True)
        merged = pd.concat([obs, sim], axis=1).reindex(obs.index)
        merged.to_csv(os.path.join(processed_dir, key + '-merged.csv'))

    stations_df = pd.read_csv(os.path.join(processed_dir, 'valid_stations_list.csv'))
    error_columns = ['GaugeID','Latitude','Longitude','PBIAS','NSE','KGE',
                     'RMSE','MAE','RRMSE','obs_avg','sim_avg','NMAE','R2']
    error_df = pd.DataFrame(columns=error_columns).set_index('GaugeID')

    for i in range(len(stations_df)):
        key = stations_df.loc[i, 'stations']
        try:
            station = pd.read_csv(os.path.join(processed_dir, key + '-merged.csv'), index_col='Date', parse_dates=True)
            station = station.loc['2001-01-01':'2003-12-31'].dropna()
            obs_flow = station['Streamflow (cumecs)']
            sim_flow = station['Streamflow_tavg']
            meta = meta_file.loc[key]
            kge_metrics = kge(obs_flow, sim_flow, return_all=True)
            row = pd.DataFrame([[
                key, meta['Latitude'], meta['Longitude'],
                round(pbias(obs_flow, sim_flow), 3),
                round(nashsutcliffe(obs_flow, sim_flow), 3),
                round(kge_metrics[0], 3),
                round(rmse(obs_flow, sim_flow), 3),
                round(mae(obs_flow, sim_flow), 3),
                round(rrmse(obs_flow, sim_flow), 3),
                round(obs_flow.mean(), 3), 
                round(sim_flow.mean(), 3),
                round(nmae(obs_flow, sim_flow), 3),
                round(R2(obs_flow, sim_flow), 3)
            ]], columns=error_columns).set_index('GaugeID')
            error_df = error_df.append(row)
        except Exception as e:
            print(f"❌ Error in {key}: {e}")
    error_df.to_csv(error_output_path)

    print(f"✅ Processing complete for {lsm_name}")
