import geopandas as gpd
import matplotlib.pyplot as plt
from shapely.geometry import Point, shape
import fiona 
import shapely
import numpy as np
import pandas as pd
import os,glob


points_df = pd.read_csv('')   # point data for basin-wise analysis

# The analysis is done by opening each basin polygon individually and then extracting the data from points_df which fall in the basin.

# Build a list of all basin files. Any implementation will work. I have used list structre.
basin_files = ['Basin_Krishna','Basin_Narmada','Basin_North_western','Basin_Cauvery_Eastern','Basin_Mahanadi_Subarnarekha','Basin_Godavari']
i = 0 # counter need to build list of basin-wise dataframes
# Open the basin files iterative and build the list of basin-wise dataframes.
for item in basin_files():
    fc = fiona.open('location of basin files/'+item+'.shp')
    basin_points = pd.DataFrame() # dataframe to capture basin-specific points data
    basin_dfs = [None]*len(basin_files) # empty list to contain basin wise dataframes
    shapefile_record = fc.next()
    shape = shapely.geometry.asShape( shapefile_record['geometry'] )
    # Check for each lat/lon whether it falls within the Basin boundary
    for k in range(0,len(points_df)) :
        x = points_df.loc[k]['Longitude']
        y = points_df.loc[k]['Latitude']
        point = shapely.geometry.Point(x,y) # longitude, latitude
        if shape.contains(point):
            basin_points = basin_points.append(points_df.loc[k])
    basin_dfs[i] = basin_points
    i = i+1


print(basin_dfs[0].describe())