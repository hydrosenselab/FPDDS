import xarray as xr

def nc_varlist(ncdat):
    """Gives a list of netCDF variables contained 
    in an xarray dataset
    
    Parametes: 
        ncfile: A netCDF file
    Returns: 
        A list of netCDF variables contained in the file
    """    
    varlist=[]
    for var in ncdat.variables:
        varlist.append(var)
    return(varlist)