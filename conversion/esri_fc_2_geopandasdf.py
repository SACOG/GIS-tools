"""
Name: esri_fc_2_geopandasdf.py
Purpose: Code snippets to demonstrate how to load ESRI feature classes into
    a Geopandas geodataframe.
    
    NOTE that unlike using arcpy, you can also access and load CUBE geodatabase feature classes
    into geodataframes.

    HOWEVER, you cannot export geopandas geodataframes directly back into an ESRI file geodatabase. Instead,
    you must export to a more open format (e.g., SHP, geojson, gpkg, etc.) and load that resulting file into the geodatabase.
        
          
Author: Darren Conly
Last Updated: Oct 2021
Updated by: <name>
Copyright:   (c) SACOG
Python Version: 3.x
"""

import geopandas as gpd


### FROM ESRI GEODATABASE TO GEOPANDAS GEODATAFRAME

file_gdb = r'I:\Projects\Darren\PPA_V2_GIS\PPA_V2.gdb'

feature_class = 'EJ_Areas_2018'

# NOTE - must always include 'geometry' if specifying columns, otherwise won't have any geometry attribute
# and you won't be able to do spatial stuff with the geodataframe
fc_cols_to_use = ['COUNTY', 'Tot_Pop', 'pct_minori', 'EJ_TYPE', 'geometry']

gdf = gpd.GeoDataFrame.from_file(file_gdb, layer=feature_class, driver="OpenFileGDB")[fc_cols_to_use]

print(gdf.head())


""" 
### FROM CUBE TRANSIT NETWORK DATA SET TO GEOPANDAS GEODATAFRAME
cube_gdb = r'\\data-svr\Modeling\SACSIM23\Network\Cube\SACSIM23GISNets.gdb'
gdb_fd = r'\\data-svr\Modeling\SACSIM23\Network\Cube\SACSIM23GISNets.gdb'

# feature classes within a transit feature dataset -- note that the feature data set name is NOT in the path to the feature class
# e.g., 'PT_PA35_PTNode' is inside a feature dataset called 'PT_PA35', but you don't specify that in the path.
fc_trn_nodes = r'PT_PA35_PTNode' 
fc_trn_lines = r'PT_PA35_PTLine'

# load the feature class--even in a Cube GDB!--into a geodataframe
gdf_tnodes = gpd.GeoDataFrame.from_file(gdb_fd, layer=fc_trn_nodes, driver="OpenFileGDB")
gdf_tlines = gpd.GeoDataFrame.from_file(gdb_fd, layer=fc_trn_lines, driver="OpenFileGDB")
# print(gdf_tnodes['LINEID'].unique())
print(gdf_tnodes.columns)
print(gdf_tlines.head())

 """