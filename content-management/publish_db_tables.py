"""
Name: publish_db_tables.py
Purpose: Publishes all user-selected file geodatabase tables to Portal
    IMPORTANTLY:
        -File geodatabase must be within a folder that is a Data Store registered with Portal

    https://pro.arcgis.com/en/pro-app/latest/arcpy/sharing/featuresharingdraft-class.htm

Author: Darren Conly
Last Updated: Nov 2022
Updated by: 
Copyright:   (c) SACOG
Python Version: 3.x
"""

import os
from getpass import getpass

import arcpy
arcpy.env.overwriteOutput = True




#===================USER INPUTS=======================

# fgdb containing layers--MUST be registered data store
# in future, add automated check that checks if gdb is inside registered data store
file_gdb = r'\\arcserver-svr\D\PPA3_SVR\PPA3_GIS_SVR\PPA3_run_data.gdb'

aprx_file_path = r"I:\Projects\Darren\PPA3_GIS\PPA3_GIS.aprx"
aprx_map_name = 'ItemsToShare'

# list of all feature layers and tables in APRX map you want to publish
contents_to_publish = ['rp_artexp_vmt', 'rp_artexp_econ', 'rp_artexp_eq', 'rp_artexp_mm', 'rp_artexp_sgr', 
                'rp_fwy_vmt', 'rp_fwy_cong', 'rp_fwy_mm', 'rp_fwy_econ', 'rp_fwy_frgt', 'rp_fwy_saf', 
                'rp_artsgr_sgr', 'cd_compactdev', 'cd_mixeduse', 'cd_houschoice', 'cd_naturpres', 
                'rp_artexp_cong', 'rp_artexp_frgt', 'rp_artexp_saf', 'cd_trnchoice', 'cd_existgasset', 'project_master']

contents_to_publish = ['project_master']

#--------seldom-changed parameters-------------
portal_url = input("Enter Portal URL: ")
portal_folder = input("Enter Portal folder name: ")
server_type = "HOSTING_SERVER"

# sharing permissions - https://pro.arcgis.com/en/pro-app/latest/tool-reference/server/upload-service-definition.htm
override_val = "OVERRIDE_DEFINITION"
share_level = "PUBLIC" # "PRIVATE" # if you want to share tool with everyone or not
org_share = "SHARE_ORGANIZATION" # whether you want to share with organization


#================SELDOM-CHANGED PARAMETERS AND RUN SCRIPT====================

# Sign in to portal (uses Windows Authentication, no need to specify username or password)
arcpy.SignInToPortal(portal_url)

# Reference layers to publish
aprx = arcpy.mp.ArcGISProject(aprx_file_path)
map_obj = aprx.listMaps(aprx_map_name)[0]
map_obj_layer_names = [i.name for i in map_obj.listLayers()]
all_map_layers = [fl for fl in map_obj.listLayers()]
all_map_tables = [t for t in map_obj.listTables()]
all_map_contents = all_map_layers + all_map_tables


# Set temp folder for storing service definitions
outdir = arcpy.env.scratchFolder
svc_type = "FEATURE" # want to publish as queryable features instead of tiles

for item in contents_to_publish:
    arcpy.AddMessage(f"Starting publish process for {item}")
    # Set output file names
    service_name = item
    sddraft_filename = f"{service_name}.sddraft"
    sddraft_output_filename = os.path.join(outdir, sddraft_filename)

    sd_filename = f"{service_name}.sd"
    sd_output_filename = os.path.join(outdir, sd_filename)

    # Create FeatureSharingDraft
    if item in map_obj_layer_names:
        selected_layer = map_obj.listLayers(item)[0]
    else:
        selected_layer = map_obj.listTables(item)[0]

    # https://pro.arcgis.com/en/pro-app/latest/arcpy/sharing/featuresharingdraft-class.htm
    sddraft = map_obj.getWebLayerSharingDraft(server_type, svc_type, service_name, [selected_layer])
    sddraft.portalFolder = portal_folder

    # Create Service Definition Draft file
    sddraft.exportToSDDraft(sddraft_output_filename)

    # Stage Service
    arcpy.AddMessage("\tStaging...")
    arcpy.server.StageService(sddraft_output_filename, sd_output_filename)

    # Share to portal
    arcpy.AddMessage("\tUploading...")
    arcpy.server.UploadServiceDefinition(sd_output_filename, server_type, in_override=override_val, in_public=share_level,
                                        in_organization=org_share)

    arcpy.AddMessage(f"\tFinished publishing {item}")

arcpy.AddMessage("\nSuccess! All table(s) and feature layer(s) published successfully.")
    