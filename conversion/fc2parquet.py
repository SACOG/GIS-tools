"""
Name: fc2parquet.py
Purpose: converts ESRI feature classes to parquet


Author: Darren Conly
Last Updated: 
Updated by: 
Copyright:   (c) SACOG
Python Version: 3.x
"""

from pathlib import Path

import geopandas as gpd
import pandas as pd
import arcpy
from shapely import wkt

def esri_to_df(esri_obj_path, include_geom, field_list=None, index_field=None, 
               crs_val=None, dissolve=False, use_centroid=False):
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
    use_centroid = True/False indicating if you want to use centroid points rather than, for example, line for polygon geometry.
                    Setting to True can save a lot of space if working with a large number of records.
    """

    fields = field_list # should not be necessary, but was having issues where class properties were getting changed with this formula
    if not field_list:
        fields = [f.name for f in arcpy.ListFields(esri_obj_path)]

    if include_geom:
        # by convention, geopandas uses 'geometry' instead of 'SHAPE@' for geom field
        f_esrishp = 'SHAPE@'
        f_gpdshape = 'geometry'
        fields = fields + [f_esrishp]

    data_rows = []
    with arcpy.da.SearchCursor(esri_obj_path, fields) as cur:
        for row in cur:
            rowlist = [i for i in row]
            if include_geom:
                geom_wkt = wkt.loads(rowlist[fields.index(f_esrishp)].WKT)
                if use_centroid:
                    geom_wkt = geom_wkt.centroid
                rowlist[fields.index(f_esrishp)] = geom_wkt
            out_row = rowlist
            data_rows.append(out_row)  

    if include_geom:
        fields_gpd = [f for f in fields]
        fields_gpd[fields_gpd.index(f_esrishp)] = f_gpdshape
        
        out_df = gpd.GeoDataFrame(data_rows, columns=fields_gpd, geometry=f_gpdshape)

        # only set if the input file has no CRS--this is not same thing as .to_crs(), which merely projects to a CRS
        if crs_val: out_df.crs = crs_val

        # dissolve to single zone so that, during spatial join, points don't erroneously tag to 2 overlapping zones.
        if dissolve and out_df.shape[0] > 1: 
            out_df = out_df.dissolve() 
    else:
        out_df = pd.DataFrame(data_rows, index=index_field, columns=field_list)

    return out_df


def fc2parquet(in_fc, out_pqt, field_list, crs, convert_to_centroid=False):
    gdf = esri_to_df(esri_obj_path=in_fc, field_list=field_list, include_geom=True, crs_val=crs,
                     use_centroid=convert_to_centroid)
    gdf.to_parquet(out_pqt)



if __name__ == '__main__':
    input_fcs = [
        r'I:\Projects\Indrani\Pathways_landuse_Summaries.gdb\PathwayParcels_2020_DC',
        r'I:\Projects\Indrani\Pathways_landuse_Summaries.gdb\Region_P1_2035',
        r'I:\Projects\Indrani\Pathways_landuse_Summaries.gdb\Region_P1_2050',
        r'I:\Projects\Indrani\Pathways_landuse_Summaries.gdb\Region_P2_2035',
        r'I:\Projects\Indrani\Pathways_landuse_Summaries.gdb\Region_P2_2050',
        r'I:\Projects\Indrani\Pathways_landuse_Summaries.gdb\Region_P3_2035',
        r'I:\Projects\Indrani\Pathways_landuse_Summaries.gdb\Region_P3_2050'
    ]

    output_folder = r'I:\Projects\Indrani\Pathways_Landuse_summaries_parquet'

    fields_to_load = None # ['ES_Landuse', 'HU', 'EMP', 'GROSS_NET', 'GISac']
    load_as_centroid = True

    for fc in input_fcs:
        fcname = Path(fc).name
        out_pqt = Path(output_folder).joinpath(f"{fcname}.parquet")
        fc2parquet(fc, out_pqt, field_list=fields_to_load, crs="EPSG:2226",
                   convert_to_centroid=load_as_centroid)
        print(f"Created parquet file {out_pqt}")

