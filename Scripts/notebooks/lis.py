import numpy as np
import pandas as pd
import xarray as xr
import glob, os
import numpy as np

def reformat_LIS_param(ncdat):
    """Reformats dimensions of a LIS output file xarray dataset 
    for easier handling of geographic dimensions
    
    Parameters: 
        ncdir: LIS input xarray dataset with NS/EW dimensions
    Returns: 
        LIS input xarray dataset with lat/lon dimensions
    """
    
    reformatted_ncdat=ncdat.rename({'north_south':'lat', 'east_west':'lon'}) 
    
    lat_vals = reformatted_ncdat['lat'][:,-1] #Extract latitudes
    lon_vals = reformatted_ncdat['lon'][-1,:] #Extract longitudes
    
    reformatted_ncdat=reformatted_ncdat.assign_coords(lat=lat_vals,lon=lon_vals, time=reformatted_ncdat.coords['time']) #Assign lat/long as coordinate dims
    
    return(reformatted_ncdat)

def reformat_LIS_output(ncdat):
    """Reformats dimensions of LIS outputs for easier handling
    
    Parameters: 
        ncdat: LIS output xarray dataset with NS/EW dimensions
    Returns: 
        LIS output netCDF file with lat/lon dimensions
    """
    xmin=ncdat.attrs['SOUTH_WEST_CORNER_LON']
    ymin=ncdat.attrs['SOUTH_WEST_CORNER_LAT']
    dx=ncdat.attrs['DX']
    dy=ncdat.attrs['DY']
    nx=ncdat.dims['east_west']
    ny=ncdat.dims['north_south']

    lonarr=np.arange(xmin, xmin + dx * nx, dx) #Creates latitude array
    latarr=np.arange(ymin, ymin + dy * ny, dy) #Creates longitude array

    reformatted_ncdat=ncdat.rename({'north_south':'lat', 'east_west':'lon'}) 
    reformatted_ncdat=reformatted_ncdat.assign_coords({"lon": lonarr, 
                                                       "lat": latarr})
    
    return(reformatted_ncdat)
