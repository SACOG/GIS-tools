"""
Name: make_esri_se_dataframe.py
Purpose: Collection of copy/pastable functions to make an ESRI spatially-enabled dataframe
    
    NOTES:
        -often, it is nicer to use a geopandas geodataframe. There is a richer support community out there, it is open-source,
        and often it is faster.

    Resources:
        -https://developers.arcgis.com/python/guide/introduction-to-the-spatially-enabled-dataframe/
        -https://developers.arcgis.com/python/api-reference/arcgis.features.toc.html#geoaccessor
            These methods apply to a spatially-enabled dataframe
            Template: sedf.spatial.<GeoAccessor API method>
        -https://developers.arcgis.com/python/api-reference/arcgis.features.toc.html#geoseriesaccessor
            These methods apply to a geometry object within a spatially-enabled dataframe
            E.g., if an SEDF has geometry column 'geom', you apply GeoSeriesAccessor methods to single items in the geom column.
            E.g., sedf['geom'][0].<GeoSeriesAccessor API method>
        
          
Author: Darren Conly
Last Updated: Nov 2021
Updated by: <name>
Copyright:   (c) SACOG
Python Version: 3.x
"""

import pandas as pd
import arcpy
from arcgis.features import GeoAccessor, GeoSeriesAccessor
arcpy.env.overwriteOutput = True


#============FEATURE CLASS <--> SPATIALLY-ENABLED DATAFRAME (ALSO WORKS WITH SHAPEFILES)=======================
test_fc = r'I:\Projects\Darren\PEP\PEP_GIS\AccessibilityPolicyTesting\AccessibilityPolicyTesting.gdb\accessDiff2020v2019'
cols_to_use = ['bgid', 'AUTODESTS', 'AUTODESTS_1', 'SHAPE']

# load esri feature class into SEDF
sedf = pd.DataFrame.spatial.from_featureclass(test_fc, usecols=cols_to_use)

# export SEDF to feature class
output_fc = r'I:\Projects\Darren\PEP\PEP_GIS\AccessibilityPolicyTesting\AccessibilityPolicyTesting.gdb\TEST_fromSEDF'
sedf[cols_to_use].spatial.to_featureclass(output_fc)


#============GEOPANDAS GEODATAFRAME <--> SPATIALLY-ENABLED DATAFRAME (ALSO WORKS WITH SHAPEFILES)=======================
import geopandas as gpd

world_gdf = gpd.read_file(gpd.datasets.get_path('naturalearth_lowres'))
world_sedf = pd.DataFrame.spatial.from_featureclass(world_gdf)
world_sedf.head()
