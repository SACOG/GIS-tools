"""
Name: publish_se_dataframe.py
Purpose: Code to publish ESRI spatially-enabled dataframe directly to Portal

# https://developers.arcgis.com/python/latest/api-reference/arcgis.features.toc.html#arcgis.features.GeoAccessor.to_featurelayer


Author: Darren Conly
Last Updated: Oct 2024
Updated by: 
Copyright:   (c) SACOG
Python Version: 3.x
"""
from pathlib import Path

import pandas as pd
import arcpy
from arcgis.features import GeoAccessor, GeoSeriesAccessor
from arcgis.gis import GIS

def make_shp_compatible(in_df):
    # update field data types to make compatible with exporting to shapefile

    translator = { # make sure that keys are all lower-case
        'int64': 'int32',
        'float64': 'float32' # 'float32'
    }

    for fname, dt in in_df.dtypes.to_dict().items():
        dtname = dt.name.lower()
        if dtname in translator.keys():
            in_df[fname] = in_df[fname].astype(translator[dtname])

if __name__ == '__main__':

    test_fc = r'Q:\SACSIM23\Network\MTPProjectQA_GIS\MTPProjectQA_GIS.gdb\PNR_2020_20230221'
    sedf = pd.DataFrame.spatial.from_featureclass(test_fc)

    output_name = 'PNR_TEST'
    destination_folder = 'Blueprint 2024'
    overwrite_existing = False
    feature_svc_id = '8a1f15d5715746b99e87b9a218fb2e02'
    layer_n = 0
    auth_file = Path(__file__).parent.joinpath('gis_admin.auth') # auth text file that has user_name and portal_url. If in a repository should add .auth to .gitignore file

    
    #=========RUN SCRIPT================================
    authdict = {}
    try:
        with open(auth_file, 'r') as f:
            rows = f.readlines()
            for row in rows:
                rs = row.strip('\n').split('=')
                authdict[rs[0].strip("\'")] = rs[1].strip("\'")
    except FileNotFoundError:
        raise Exception(f"PERMISSION ERROR: {auth_file} not found.")

    gis_conn = GIS(authdict['portal_url'], authdict['user_name'], verify_cert=False)
    print("connection made to gis object. Publishing SEDF to feature layer...")


    # convert away from big-int datatype
    make_shp_compatible(sedf)

    overwrite_svc = None # by default, assume not overwriting
    if overwrite_existing:
        overwrite_svc = {'featureServiceId' : feature_svc_id, 'layer': layer_n}
    sedf.spatial.to_featurelayer(title=output_name, gis=gis_conn, folder=destination_folder, overwrite=overwrite_existing, service=overwrite_svc)
    print("success!")