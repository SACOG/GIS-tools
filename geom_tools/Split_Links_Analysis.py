#--------------------------------
# Name: Split_Links_Analysis.py
# Purpose: To prepare the Split Links process as part of the Split_Links_Full.py script
# Author:Kyle Shipley
# Created: 1/09/18
# Update -
# Copyright:   (c) SACOG
# ArcGIS Version:   10.5
# Python Version:   2.8
#--------------------------------

import arcpy,traceback, sys, os, time
from arcpy import env

start_time = time.time()

#inputs
inStreet = r'I:\Projects\Kyle\2020MTP\Parcel_Update\GIS\Input_Link.gdb\RegionalCenterline'
outStreetName = "AllStreets_SplitLine"

#set workspace
workspace = os.path.dirname(inStreet)
env.workspace = workspace
env.overwriteOutput = True

#output
outStreet = os.path.join(workspace,outStreetName)

#Start

try:
    # Remove Highways and Ramps
    whereclause1 = '''NOT "CLASS" = 'H' AND NOT "CLASS" = 'RAMP' '''  # Note Centerline file did not have HWY
    arcpy.AddMessage("Where Clause: " + whereclause1)
    allstreetlyr = arcpy.MakeFeatureLayer_management(inStreet, "allstreetlyr", whereclause1)

    #Cleanup incase their are any hanging files...
    if arcpy.Exists("SplitLine"):
        arcpy.Delete_management("SplitLine")

    #Split Lines until all roadway segments are less than 530 feet.
    count = 1
    i = 0
    RndptD = 250 #Used to split segments

    SptLn_start_time = time.time()
    arcpy.AddMessage("Start Split Line Process at: %s minutes ---" % (round((time.time() - start_time) / 60, 2)))
    while count > 0:
        i += 1
        #Get Count of Features Greater than 530 feet
        arcpy.AddMessage(str(i)+" : Split segments >= 530 feet")
        whereclause2 = "shape_length >= 530"
        if not arcpy.Exists("SplitLine"):
            street2_lyr = arcpy.MakeFeatureLayer_management(allstreetlyr, "street2_lyr", whereclause2)
            allstreetlyr2 = allstreetlyr
            RndPtsSplt = str(RndptD) + " Feet"

            Cntresult = arcpy.GetCount_management(street2_lyr)
            count = int(Cntresult.getOutput(0))
            arcpy.AddMessage("records to split:" + str(count))
            if count < 1:
                break

            #Find Endpoints to remove slivers
            Ends1_lyr = arcpy.FeatureVerticesToPoints_management(allstreetlyr, "Ends1_lyr", "BOTH_ENDS")
            buffer = "50 Feet"
            Int4_buf_lyr = arcpy.Buffer_analysis(Ends1_lyr, "Int4_buf_lyr", buffer)

            #Split Lines at Random points based on "RndptsD", should split most lines to required length.
            Rndptsft = arcpy.CreateRandomPoints_management(workspace, "Rndptsft", street2_lyr, "", 10000,RndPtsSplt)
            Rndptsft2_lyr = arcpy.MakeFeatureLayer_management(Rndptsft, "Rndptsft2_lyr")
            SplitptsLayer = arcpy.SelectLayerByLocation_management(in_layer=Rndptsft2_lyr, overlap_type="INTERSECT",
                                             select_features=Int4_buf_lyr, search_distance=".001 Feet",
                                             selection_type="NEW_SELECTION",
                                             invert_spatial_relationship="INVERT")

        else:
            street2_lyr = arcpy.MakeFeatureLayer_management(SplitLine, "street2_lyr" + str(i), whereclause2)
            allstreetlyr2 = arcpy.CopyFeatures_management(SplitLine, "in_memory/SplitLine" + str(i))

            arcpy.AddMessage("Check for any remaining long segments")

            Cntresult = arcpy.GetCount_management(street2_lyr)
            count = int(Cntresult.getOutput(0))
            arcpy.AddMessage("records to split:" + str(count))
            if count < 1:
                break

            # Split Remaining Long Lines at Midpoints points to avoid slivers.
            SplitptsLayer = arcpy.FeatureVerticesToPoints_management(street2_lyr, "MidptsSplt", "MID")

        #Split Line
        ArcpySptLn_start_time = time.time()
        arcpy.AddMessage("      Start Splitting Lines Process at: %s minutes ---" % (round((time.time() - start_time) / 60, 2)))
        SplitLine = arcpy.SplitLineAtPoint_management(allstreetlyr2, SplitptsLayer, "SplitLine", "1 Feet")
        arcpy.AddMessage("      Complete Splitting Lines Processing Time: %s minutes ---" % (round((time.time() - ArcpySptLn_start_time) / 60, 2)))
        arcpy.AddMessage(str(i)+" :Split Line Process Complete            %s minutes ---" % (round((time.time() - start_time) / 60, 2)))
        arcpy.AddMessage("Finish Process Iteration:  " + str(i))
        arcpy.AddMessage("------------------------------")


    arcpy.AddMessage("Complete Split Line Process at: %s minutes ---" % (round((time.time() - start_time) / 60, 2)))

    #Copy Final Feature Layers
    arcpy.AddMessage("Creating Outputs")

    #arcpy.CopyFeatures_management(Int3_lyr,outStreet + "_Ints")
    arcpy.CopyFeatures_management(SplitLine,outStreet)
    arcpy.AddMessage("Total Process Time:         %s minutes ---" % (round((time.time() - SptLn_start_time) / 60, 2)))
    arcpy.AddMessage("----------------------------------------------")


    #Cleanup
    del street2_lyr,Int4_buf_lyr
    del Rndptsft,Rndptsft2_lyr
    for x in range(i):
        try:
            ItsSplitLine = "in_memory/SplitLine" + str(x)
            del ItsSplitLine
        except:
            pass


except arcpy.ExecuteError:
    arcpy.AddMessage(arcpy.GetMessages(2))
except Exception as e:
    arcpy.AddMessage(e.args[0])
    # If an error occurred, print line number and error message
    tb = sys.exc_info()[2]
    arcpy.AddMessage("An error occured on line %i" % tb.tb_lineno)
    arcpy.AddMessage(str(e))
    arcpy.AddMessage("Check feature class has CLASS field and H and RAMP values")
    print("--- %s minutes ---" % (round((time.time() - start_time) / 60, 2)))