"""
Name: fast_spatial_select.py
Purpose: Selects features from one feature class based on spatial relationship to other feature class
    E.g., selecting all parcels in some polygon-based area.

    It's much faster than arcpy's SelectByLocation method, but does not have option for "have their center in" selection

    Planned improvement: enable search distance or buffering around the selection feature (currently not available)


Author: Darren Conly
Last Updated: Apr 2025
Updated by: 
Copyright:   (c) SACOG
Python Version: 3.x
"""
import os
import arcpy

def fast_spatial_select(input_features, selection_features, out_gdb, out_fc_name,
                        select_relationship='INTERSECTS'):
    """
    Creates feature class that is subset of input_features that intersect
     selection_features. Is a much faster (6-8x faster) version of arcpy SelectLayerByLocation.
     NOTE - Cannot select based on "has their center in" relationship, NOR can you add a buffer around the selection feature.
    """
        
    pcl_meta = arcpy.Describe(input_features)
    out_fc_path = os.path.join(out_gdb, out_fc_name)
    arcpy.management.CreateFeatureclass(out_gdb, out_fc_name, template=input_features,
                                        geometry_type=pcl_meta.shapeType.upper(),
                                        spatial_reference=pcl_meta.spatialReference)
    
    polys = []
    with arcpy.da.SearchCursor(selection_features, field_names=['SHAPE@']) as pcur:
        for row in pcur:
            polys.append(row[0])

    if len(polys) == 0:
        raise Exception(f"ERROR: no features in {selection_features}")

    inscur = arcpy.da.InsertCursor(out_fc_path, field_names="*")

    pcl_fnames = [f.name for f in arcpy.ListFields(out_fc_path)] # needed to ensure correct order of attributes for insert cursor
    for selection_poly in polys:
        with arcpy.da.SearchCursor(input_features, field_names=pcl_fnames,
                                   spatial_filter=selection_poly,
                                   spatial_relationship=select_relationship) as scur:
            for row in scur:
                try:
                    inscur.insertRow(row)   
                except:
                    import pdb; pdb.set_trace()

    return out_fc_path   



if __name__ == '__main__':
    pass