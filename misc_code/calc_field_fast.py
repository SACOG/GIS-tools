# This code intended to be copy/pasted into the python window in ArcMap or ArcGIS Pro
# for large files (>100k rows) it is faster than using Calculate Field


import arcpy


in_fc = 'parcel_data_pts_2016'
field_to_calc = 'Urbn2010'


with arcpy.da.UpdateCursor(in_fc, field_names=[field_to_calc]) as ucur:
    for row in ucur:
        row[0] = 0
        ucur.updateRow(row)