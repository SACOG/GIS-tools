"""
Name: geopandas_to_esri_fc.py
Purpose: To output geopandas geodataframe to ESRI feature class


Author: Darren Conly
Last Updated: June 2025
Updated by: 
Copyright:   (c) SACOG
Python Version: 3.x
"""

import pandas as pd
from arcgis.features import GeoAccessor, GeoSeriesAccessor

def gdf_to_esri_fc(gdf, out_path):
    if not isinstance(out_path, str):
        out_path = str(out_path)

    sedf4gis = pd.DataFrame.spatial.from_geodataframe(gdf)
    sedf4gis.spatial.to_featureclass(out_path, sanitize_columns=False) 
    
    return out_path



if __name__ == '__main__':
    pass