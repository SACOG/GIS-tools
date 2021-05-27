# --------------------------------
# Name: Find Intersections
# Purpose: Create intersection feature class from Line feature class.
# Author: Kyle Shipley
# Created: 1/12/18
# Update - 1/25/18
# Copyright:   (c) SACOG
# ArcGIS Version:   10.5
# Python Version:   2.7
# --------------------------------

import arcpy, os

# Inputs
allstreetlyr = r'Q:\SACSIM19\Buffering\Circuity\circuity_buffer_2016\DataCollection\Model.gdb\AllStreets'
output = "sacog_intersections_2016"
# To say no leave blank, example ... = ""
RemoveTwoWayInts = "YES"
KeepCulDeSac = "YES"

#####################################################

arcpy.env.workspace = os.path.dirname(allstreetlyr)
arcpy.env.overwriteOutput = True

if KeepCulDeSac:
    Int1_lyr = arcpy.FeatureVerticesToPoints_management(allstreetlyr, "in_memory/Int1_lyr", "BOTH_ENDS")
    arcpy.AddMessage("Keeping Cul De Sacs")
else:
    Int1_lyr = arcpy.Intersect_analysis(allstreetlyr, "in_memory/Int1_lyr", "ALL", "", "POINT")
arcpy.DeleteIdentical_management(Int1_lyr, "Shape")
Int2_lyr = arcpy.SpatialJoin_analysis(Int1_lyr, allstreetlyr, "InMemory/Int2_lyr","JOIN_ONE_TO_ONE")
whereclause3 = ""
if len(RemoveTwoWayInts) > 0:
    arcpy.AddMessage("Removing Two Way Intersections")
    whereclause3 = '''"Join_Count" <> 2'''
Int3_lyr = arcpy.MakeFeatureLayer_management(Int2_lyr, "in_memory/Int3_lyr", whereclause3)
arcpy.CopyFeatures_management(Int3_lyr,output)

arcpy.AddMessage("Complete")
