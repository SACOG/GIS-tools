"""
export_fc_with_select_fields.py

Purpose: 
    Allows user to copy a feature class but specify which fields end
    up in the resulting feature class (esp useful if you want to trim off
    unneeded fields).
"""

import arcpy

def shp2fc_sel_fields(in_shp, field_list, out_dir, out_temp_fc):
    field_maps = arcpy.arcpy.FieldMappings()
    
    for field in field_list:
        vars()[field] = arcpy.FieldMap() #vars() 
        vars()[field].addInputField(in_shp, field)
        field_maps.addFieldMap(vars()[field])
        
    arcpy.FeatureClassToFeatureClass_conversion(in_shp, out_dir, out_temp_fc, "", field_maps)