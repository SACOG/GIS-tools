"""
Name: update_dtypes.py
Purpose: converts GIS types as desired to ensure file compatibility.
    E.g., Cube doesn't use int64 or float64 'big integer' types, so this script
    offers a way to convert to dtypes that Cube can use.


Author: Darren Conly
Last Updated: Sep 2024
Updated by: 
Copyright:   (c) SACOG
Python Version: 3.x
"""

from pathlib import Path

import pandas as pd

import arcpy
from arcgis.features import GeoAccessor, GeoSeriesAccessor

def convert_dtypes(in_fc, out_fc, conversion_dict):

    sedf = pd.DataFrame.spatial.from_featureclass(in_fc)

    for f in sedf.columns:
        dt1 = sedf[f].dtype.name.lower()
        if dt1 in conversion_dict:
            sedf[f] = sedf[f].astype(conversion_dict[dt1])
            
    # export to GIS      
    print(sedf.spatial.to_featureclass(out_fc, sanitize_columns=False))

    fdata = {f.name: f.type for f in arcpy.ListFields(out_fc) if f.type == 'BigInteger'}
    if len(fdata.keys()) > 0:
        print("WARNING: your table has big integer data types:")
        print(fdata)
    
    
if __name__ == '__main__':
    conversion = {
                'int64': 'int32',
                'float64': 'float32'
                 }
    
    fc_in = r'Q:\SACSIM23\Network\MTPProjectQA_GIS\MTPProjectQA_GIS.gdb\SS23master_DPS20241008_1318'
    fc_out = Path(fc_in).parent.joinpath(f"{Path(fc_in).name}_fixdtyp")


    convert_dtypes(in_fc=fc_in, out_fc=fc_out, conversion_dict=conversion)