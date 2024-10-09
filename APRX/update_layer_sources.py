"""
Name: update_multiple_layersrc.py
Purpose: Change the source directory for many layers in an APRX
    if those layers source directories change
        
          
Author: Darren Conly
Last Updated: Jan 2021
Updated by: <name>
Copyright:   (c) SACOG
Python Version: 3.x
"""

import os
from pathlib import Path
from copy import deepcopy

import arcpy



def update_all_aprx_sources(aprx_path, old_src_path, new_src_path):
    # for all layers in the APRX project, if source layer = old_src_path,
    # replace it with new_src_path
    
    print("updating all file paths...")
    
    aprx = arcpy.mp.ArcGISProject(os.path.join(aprx_dir, aprx_name))
    aprx.updateConnectionProperties(old_src_path, new_src_path)
    
    print("saving changes...")
    aprx.save()

    print(f"Finished, replaced all instances of {old_src_path} with {new_src_path}")


def update_map_layr_sources(aprx_path, map_name, old_src_path, new_src_path):
    # to update all layers within specific map of APRX project
    # 10/9/2024 - only tested on feature classes; may need modifying to work with shapefiles or other data source types.
    old_dataset = Path(old_src_path)
    new_dataset = Path(new_src_path)

    aprx = arcpy.mp.ArcGISProject(aprx_path)
    map_obj = aprx.listMaps(f"{map_name}*")[0]
    
    for lyr in map_obj.listLayers():
        if lyr.connectionProperties:
            oldprops = lyr.connectionProperties
            newprops = deepcopy(oldprops)
            newprops['connection_info']['database'] = str(new_dataset.parent)
            newprops['dataset'] = new_dataset.name
            lyr.updateConnectionProperties(oldprops, newprops)
        
    print([l.dataSource for l in map_obj.listLayers()])


if __name__ == '__main__':
    #======INPUTS==============
    aprx_dir = r"C:\Users\dconly\Desktop\Temporary\PPA2_share\APRX\MapImgMaker"
    aprx_name = "PPA2_GIS_SVR_v2.aprx"
    
    old_fgdb_path = r"\\arcserver-svr\D\PPA_v2_SVR\PPA2_GIS_SVR\owner_PPA.sde"
    new_fgdb_path = r"C:\Users\dconly\Desktop\Temporary\PPA2_share\PPA2_datalayers.gdb"
    
    
    #==============SCRIPT====================
    aprx_file = os.path.join(aprx_dir, aprx_name)
    find_replace_all(aprx_file, old_fgdb_path, new_fgdb_path)
