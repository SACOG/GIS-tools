"""
Name: esri_file_to_dataframe.py
Purpose: Converts ESRI file (File GDB table, SHP, or feature class) to either pandas dataframe
    or geopandas geodataframe (if it is spatial data)

    NOTE - in the past geopandas has had a read_file method that enabled users to specify
        ESRI file gdb feature class, but it's been unreliable and subject to issues with version
        updates. This formula aims to use common ESRI and GeoPandas functions to maximize long-term reliability.


Author: Darren Conly
Last Updated: Dec 2023
Updated by: 
Copyright:   (c) SACOG
Python Version: 3.x
"""

import pandas as pd
import arcpy
from shapely import wkt

def esri_to_df(esri_obj_path, include_geom, field_list=None, index_field=None, 
               crs_val=None, dissolve=False, explode=False, sql_clause=None):
    """
    Converts ESRI file (File GDB table, SHP, or feature class) to either pandas dataframe
    or geopandas geodataframe (if it is spatial data)
    esri_obj_path = path to ESRI file
    include_geom = True/False on whether you want resulting table to have spatial data (only possible if
        input file is spatial)
    field_list = list of fields you want to load. No need to specify geometry field name as will be added automatically
        if you select include_geom. Optional. By default all fields load.
    index_field = if you want to choose a pre-existing field for the dataframe index. Optional.
    crs_val = crs, in geopandas CRS string format, that you want to apply to the resulting geodataframe. Optional.
    dissolve = True/False indicating if you want the resulting GDF to be dissolved to single feature.
    """

    fields = field_list # should not be necessary, but was having issues where class properties were getting changed with this formula
    if not field_list:
        fields = [f.name for f in arcpy.ListFields(esri_obj_path)]

    if include_geom:
        import geopandas as gpd
        # by convention, geopandas uses 'geometry' instead of 'SHAPE@' for geom field
        f_esrishp = 'SHAPE@'
        f_gpdshape = 'geometry'
        fields = fields + [f_esrishp]

    data_rows = []
    with arcpy.da.SearchCursor(esri_obj_path, fields, where_clause=sql_clause) as cur:
        for row in cur:
            rowlist = [i for i in row]
            if include_geom:
                try:
                    geom_wkt = wkt.loads(rowlist[fields.index(f_esrishp)].WKT)
                except:
                    print(f"\tWARNING: not loading link {rowlist} because it has no geometry")
                    continue
                rowlist[fields.index(f_esrishp)] = geom_wkt
            out_row = rowlist
            data_rows.append(out_row)  

    if include_geom:
        fields_gpd = [f for f in fields]

        # if feature class already had field(s) named 'geometry', rename so they don't duplicate teh geopandas geom field name
        dupe_geo_fields = [f for f in fields if f == 'geometry']
        for i, gf in enumerate(dupe_geo_fields):
            fields_gpd[fields_gpd.index(gf)] = f'{gf}{i}'

        # change name of geometry field from esri geom name to gpd geom name
        fields_gpd[fields_gpd.index(f_esrishp)] = f_gpdshape
        
        out_df = gpd.GeoDataFrame(data_rows, columns=fields_gpd, geometry=f_gpdshape)

        # only set if the input file has no CRS--this is not same thing as .to_crs(), which merely projects to a CRS
        if crs_val: out_df.crs = crs_val

        # dissolve to single zone so that, during spatial join, points don't erroneously tag to 2 overlapping zones.
        if dissolve and out_df.shape[0] > 1: 
            out_df = out_df.dissolve() 

        # use to get rid of multipart geometries (optional)
        if explode:
            out_df = out_df.explode()

        # check and warn about multipart features
        gtypes = out_df.geometry.type.drop_duplicates().values
        has_multi = any(['multi' in gt.lower() for gt in gtypes])
        if has_multi:
            print(f"WARNING: Resulting GeoDataFrame from {esri_obj_path} has multipart feature types ({gtypes}). "
                  "Use geopandas .explode() method to convert to single parts if desired.")
    else:
        out_df = pd.DataFrame(data_rows, index=index_field, columns=fields)



    return out_df

if __name__ == '__main__':
    test_fc = r'I:\Projects\Darren\PPA3_GIS\PPA3_GIS.gdb\EJ_2025_final'

    gdf = esri_to_df(test_fc, include_geom=True, crs_val=2226)
    import pdb; pdb.set_trace()