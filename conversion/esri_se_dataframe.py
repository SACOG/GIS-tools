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
import json
import pandas as pd
import geopandas as gpd
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
sedf[cols_to_use].spatial.to_featureclass(output_fc, sanitize_columns=False) # if sanitize_columns is True, then all field names will be set to lower case with underscores

#============JSON STRING <--> SEDF===============================#
def json_to_sedf(in_json_str, k_features='features'):
    """Takes in a json string, loads it to dict, then converts to
    ESRI spatially-enabled dataframe (SEDF"""

    json_loaded = json.loads(in_json_str)

    if k_features in json_loaded.keys():
        gdf = gpd.GeoDataFrame.from_features(json_loaded[k_features])
        sedf = pd.DataFrame.spatial.from_geodataframe(gdf)
    else:
        jl_keys = list(json_loaded.keys())
        exc_msg = f"""
        Error! Key value '{k_features}' is not in the list of keys
        in the loaded JSON string, whose keys include {jl_keys}. \nYou may need
        to specify the feature collection by indicating k_features=<feature coll key>.
        """
        raise Exception(exc_msg)

    return sedf


#============GEOPANDAS GEODATAFRAME <--> SPATIALLY-ENABLED DATAFRAME (ALSO WORKS WITH SHAPEFILES)=======================
import geopandas as gpd

world_gdf = gpd.read_file(gpd.datasets.get_path('naturalearth_lowres'))
world_sedf = pd.DataFrame.spatial.from_geodataframe(world_gdf)
world_sedf.head()

def sedf2gpd(in_sedf, sedf_crs='EPSG:2226', gdf_crs='EPSG:3857'):
    import geopandas as gpd
    # converts ESRI spatially-enabled dataframe to geopandas geodataframe
    print("converting to shapely geometry...")
    in_sedf['geometry'] = in_sedf['SHAPE'].apply(lambda x: x.as_shapely)
    # sedf_test
    del in_sedf['SHAPE']

    print("converting to geodataframe...")
    gdf = gpd.GeoDataFrame(in_sedf, geometry='geometry')
    gdf.crs = sedf_crs # originally import as SACOG state plan CRS

    if sedf_crs != gdf_crs:
        gdf = gdf.to_crs(gdf_crs) # need to convert to web mercator

    return gdf

#==============PANDAS DATAFRAME WITH X/Y FIELDS <--> SPATIALLY-ENABLED DATAFRAME==================
# convert a normal non-spatial pandas df with x/y fields into a spatially-enabled dataframe
df = None
df_x_col = None
df_y_col = None
GeoAccessor.from_xy(df, x_column=df_x_col, y_column=df_y_col)

# convert SEDF into normal, non-spatial pandas df