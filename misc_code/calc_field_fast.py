# This code intended to be copy/pasted into the python window in ArcMap or ArcGIS Pro
# for large files (>100k rows) it is faster than using Calculate Field


import arcpy


in_fc = 'Collisions2014to2018EJ_areatyp_tags'


with arcpy.da.UpdateCursor(in_fc, field_names=['EJ2018']) as ucur:
    for row in ucur:
        row[0] = 0
        ucur.updateRow(row)
