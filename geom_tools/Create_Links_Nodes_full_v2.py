#--------------------------------
# Name: Create_Links_Nodes_full.py
# Purpose: To prepare the Link and Nodes for Circuity Buffer Process (DAYSIM Inputs)
# Author: Kyle Shipley
# Created: 1/09/18
# Update - 1/24/18
# Copyright:   (c) SACOG
# ArcGIS Version:   10.5
# Python Version:   2.8
#--------------------------------

import arcpy,traceback, sys, os, time, csv
from arcpy import env

start_time = time.time()

####################################################

###USER INPUTS
#Input Feature Class
inStreet = r'I:\Projects\Kyle\2020MTP\Parcel_Update\GIS\Input_Link.gdb\RegionalCenterline'
#output Names
outStreetName = "input_link"
outNodesName = "input_node"

####################################################

#set workspace
workspace = os.path.dirname(inStreet)
env.workspace = workspace
env.overwriteOutput = True
parentfolder = os.path.dirname(workspace)
outCSVfolder = os.path.join(parentfolder,"results")
if not os.path.exists(outCSVfolder):
    os.makedirs(outCSVfolder)

#outputs
outLink = os.path.join(workspace,outStreetName)
outNodes = os.path.join(workspace,outNodesName)
outLinkCSV = os.path.join(outCSVfolder,outStreetName + ".csv")
outNodesCSV = os.path.join(outCSVfolder,outNodesName + ".csv")

#output field names needed
#LinkFields
OrderedoutLinkFields = [
    "from_node_id","to_node_id","link_id",
    "length_in_mile","direction","name",
    "speed_limit_in_mph","number_of_lanes",
    "link_type","lane_capacity_in_vhc_per_hour"
]

OrderedoutNodeFields = [
    "ID","X","Y"
]

#Fields Name & Type
from_node_id = "from_node_id"
from_node_idT = "Long"

to_node_id = "to_node_id"
to_node_idT = "Long"

link_id = "link_id"
link_idT = "Long"

length_in_mile = "length_in_mile"
length_in_mileT = "Double"

direction = "direction"
directionT = "Long" #Confirm type, unclear by example

name = "name"
nameT = "Text"

speed_limit_in_mph = "speed_limit_in_mph"
speed_limit_in_mphT = "Long"

number_of_lanes = "number_of_lanes"
number_of_lanesT = "Long"

link_type = "link_type"
link_typeT = "Long"

lane_capacity_in_vhc_per_hour = "lane_capacity_in_vhc_per_hour"
lane_capacity_in_vhc_per_hourT = "Long"

ID = "ID"
IDT = "Long"

X = "X"
XT = "Long"

Y = "Y"
YT = "Long"

###########
# Functions
###########

# Check if fields already exist
def FieldExist(featureclass, fieldname):
    # Check if a field in a feature class field exists and return true it does, false if not.
    fieldList = arcpy.ListFields(featureclass, fieldname)
    fieldCount = len(fieldList)
    if (fieldCount >= 1):  # If there is one or more of this field return true
        return True
    else:
        return False


def AddNewField(in_table, field_name,field_type, field_precision="#", field_scale="#",
                field_length="#",
                field_alias="#", field_is_nullable="#", field_is_required="#", field_domain="#"):
    # Add a new field if it currently does not exist
    if FieldExist(in_table, field_name):
        arcpy.AddMessage(field_name + " Exists")
    else:
        if  field_type == "TEXT":
            field_length = 50
        arcpy.AddMessage("Adding " + field_name + " as - " + field_type)
        arcpy.AddField_management(in_table, field_name, field_type, field_precision, field_scale,
                                  field_length,
                                  field_alias,
                                  field_is_nullable, field_is_required, field_domain)

#Insert Update DA Cursor with indexed fields,
#  include of addional fields to add.
def LoadUCursor(fc,flist=None):
    """Important note: Function creates two outputs, also only opens cursor,
     no "with" function to automatically close,
      remeber to delete cursor and fieldlist when finished"""
    fields = [field.name for field in arcpy.ListFields(fc)]
    if flist:
        for f in flist:
            fields.append(f)
    cursor = arcpy.da.UpdateCursor(fc,fields)
    flist = cursor.fields
    return cursor, flist

def linkspeedest(fclass):
    spd = 0
    if fclass == 'A':
        spd = 55
    elif fclass == 'ALLEY':
        spd = 15
    elif fclass == 'C':
        spd = 45
    elif fclass == 'LOCAL':
        spd = 25
    elif fclass == 'PED':
        spd = 10
    elif fclass == 'TO':
        spd = 10
    else:
        spd = 30
    return spd

def fixOutputs(fixCSVTemp,fname_out):
    with open(fixCSVTemp, 'rb') as fin, open(fname_out, 'wb') as fout:
        reader = csv.reader(fin)
        writer = csv.writer(fout)
        for row in reader:
            writer.writerow(row[1:])
    os.remove(fixCSVTemp)
    arcpy.AddMessage("Output to CSV Fix: %s minutes ---" % (round((time.time() - start_time) / 60, 1)))

def OutputCSV(fc,outTable,flist=None):
    try:
        if flist:
                FMapping = arcpy.FieldMappings()
                FMapping.addTable(fc)
                for field in FMapping.fields:
                    if field.name not in flist:
                        FMapping.removeFieldMap(FMapping.findFieldMapIndex(field.name))

                # #Remove hidden fields to remove csv writing out step
                # desc = arcpy.Describe(fc)
                # flds = [fld.name for fld in desc.fields]
                # flds_remove = [desc.OIDFieldName]
                # for fld in flds_remove:
                #     flds.remove(fld)
                # if fld not in flist:
                #     flds.remove(fld)
        else:
            arcpy.AddWarning("No Field Mapping Specified")
            FMapping = ""

        folder = os.path.dirname(outTable)
        name = os.path.basename(outTable)
        tempName = name[:-4] + "_T.csv"
        TempOutTable = os.path.join(folder,tempName)
        arcpy.TableToTable_conversion(fc, folder, tempName, "", FMapping)

        # Remove OID from CSV - note should try to remove in output to csv functions.
        arcpy.AddMessage("Start Fix Output: %s minutes ---" % (round((time.time() - start_time) / 60, 1)))
        fixOutputs(TempOutTable ,outTable)

        arcpy.AddMessage("Output Table Created: " + name)

    except arcpy.ExecuteError:
        arcpy.AddMessage(arcpy.GetMessages(2))
    except Exception as e:
        arcpy.AddMessage(e.args[0])
        tb = sys.exc_info()[2]
        arcpy.AddMessage("An error occured on line %i" % tb.tb_lineno)
        arcpy.AddMessage(str(e))

def SplitLinksAnalysis(inStreetfile,Outfile):
    """This function first removes all freeways and ramps, then splits all roadway
    segments to less than 530 feet to prepare the street link and nodes file."""
    global start_time
    global workspace

    # Remove Highways and Ramps
    try:
        whereclause1 = '''NOT "CLASS" = 'H' AND NOT "CLASS" = 'RAMP' '''  # Note Centerline file did not have HWY
        arcpy.AddMessage("Create All Streets Network: Remove Highways and Ramps")
        arcpy.AddMessage("Where Clause: " + whereclause1)
        allstreetlyr = arcpy.MakeFeatureLayer_management(inStreetfile, "allstreetlyr", whereclause1)

        # Cleanup incase thier is any hanging files...
        if arcpy.Exists("SplitLine"):
            arcpy.Delete_management("SplitLine")

        # Split Lines until all roadway segments are less than 530 feet.
        count = 1
        i = 0
        RndptD = 250  # Used to split segments, halved every iteration to adjust random point splits.

        SptLn_start_time = time.time()
        arcpy.AddMessage("Start Split Line Process at: %s minutes ---" % (round((time.time() - start_time) / 60, 1)))
        while count > 0:
            i += 1
            # Get Count of Features Greater than 530 feet
            arcpy.AddMessage(str(i) + " : Split segments >= 530 feet")
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

                # Find Endpoints to remove slivers
                Ends1_lyr = arcpy.FeatureVerticesToPoints_management(allstreetlyr, "Ends1_lyr", "BOTH_ENDS")
                buffer = "50 Feet"
                Int4_buf_lyr = arcpy.Buffer_analysis(Ends1_lyr, "Int4_buf_lyr", buffer)

                # Split Lines at Random points based on "RndptsD", should splits 99% of points to required length.
                Rndptsft = arcpy.CreateRandomPoints_management(workspace, "Rndptsft", street2_lyr,
                                                               "", 10000, RndPtsSplt)
                Rndptsft2_lyr = arcpy.MakeFeatureLayer_management(Rndptsft, "Rndptsft2_lyr")
                SplitptsLayer = arcpy.SelectLayerByLocation_management(
                    in_layer=Rndptsft2_lyr,
                    overlap_type="INTERSECT",
                    select_features=Int4_buf_lyr,
                    search_distance=".001 Feet",
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

            # Split Line
            ArcpySptLn_start_time = time.time()
            arcpy.AddMessage(
                "      Start Splitting Lines Process at: %s minutes ---" % (round((time.time() - start_time) / 60, 1)))
            SplitLine = arcpy.SplitLineAtPoint_management(allstreetlyr2, SplitptsLayer, "SplitLine", "1 Feet")
            arcpy.AddMessage("      Complete Splitting Lines Processing Time: %s minutes ---" % (
            round((time.time() - ArcpySptLn_start_time) / 60, 1)))
            arcpy.AddMessage(str(i) + " :Split Line Process Complete            %s minutes ---" % (
            round((time.time() - start_time) / 60, 1)))
            arcpy.AddMessage("Finish Process Iteration:  " + str(i))
            arcpy.AddMessage("------------------------------")

        arcpy.AddMessage("Complete Split Line Process at: %s minutes ---" % (round((time.time() - start_time) / 60, 1)))

        # Copy Final Feature Layers
        arcpy.AddMessage("Creating Outputs")

        # arcpy.CopyFeatures_management(Int3_lyr,outStreet + "_Ints")
        arcpy.CopyFeatures_management(SplitLine, Outfile)
        arcpy.AddMessage(
            "Total Process Time:         %s minutes ---" % (round((time.time() - SptLn_start_time) / 60, 1)))
        arcpy.AddMessage("----------------------------------------------")

        # Cleanup
        arcpy.Delete_management(street2_lyr)
        arcpy.Delete_management(Int4_buf_lyr)
        arcpy.Delete_management(Rndptsft)
        arcpy.Delete_management(Rndptsft2_lyr)
        for x in range(i):
            try:
                ItsSplitLine = "in_memory/SplitLine" + str(x)
                arcpy.Delete_management(ItsSplitLine)
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
        arcpy.AddWarning("Check feature class has CLASS field and H and RAMP values")
        print("--- %s minutes ---" % (round((time.time() - start_time) / 60, 1)))

#Start Analysis
SplitLinksAnalysis(inStreet,outLink)

#Link File
##Check if fields exists, else add new fields
arcpy.AddMessage("Checking for Required Link Output Fields at: %s minutes ---" % (round((time.time() - start_time) / 60, 1)))
AddNewField(outLink,from_node_id,from_node_idT)
AddNewField(outLink,to_node_id,to_node_idT)
AddNewField(outLink,link_id,link_idT)
AddNewField(outLink,length_in_mile,length_in_mileT)
AddNewField(outLink,direction,directionT)
AddNewField(outLink,name,nameT)
AddNewField(outLink,speed_limit_in_mph,speed_limit_in_mphT)
AddNewField(outLink,number_of_lanes,number_of_lanesT)
AddNewField(outLink,link_type,link_typeT)
AddNewField(outLink,lane_capacity_in_vhc_per_hour,lane_capacity_in_vhc_per_hourT)

#Working Fields
AddNewField(outLink,"From_X_Y","TEXT")
AddNewField(outLink,"To_X_Y","TEXT")

#list fields, set update cursor to link file
arcpy.AddMessage("Update Required Link Fields - Start at: %s minutes ---" % (round((time.time() - start_time) / 60, 1)))

LU1cursor, fieldlist = LoadUCursor(outLink,['SHAPE@'])
i = 0
for row in LU1cursor:
    #Create LINK ID Starting with 1
    i = i + 1
    row[fieldlist.index(link_id)] = i

    Linkmiles = row[fieldlist.index('SHAPE@')].getLength('PLANAR','MILES')
    row[fieldlist.index(length_in_mile)] = round(Linkmiles,2)

    #Confirm these are correct as defaults...
    row[fieldlist.index(direction)] = 0
    row[fieldlist.index(name)] = row[fieldlist.index('FULLSTREET')]

    Speed = linkspeedest(row[fieldlist.index('CLASS')])
    row[fieldlist.index(speed_limit_in_mph)] = Speed

    row[fieldlist.index(number_of_lanes)] = row[fieldlist.index('LANES')]
    row[fieldlist.index(link_type)] = 1
    row[fieldlist.index(lane_capacity_in_vhc_per_hour)] = 2000

    #Set First Point, Last Point Node X_Y UID
    from_X = row[fieldlist.index('SHAPE@')].firstPoint.X
    from_Y = row[fieldlist.index('SHAPE@')].firstPoint.Y
    from_X_Y_coords = str(int(from_X)) + "_" + str(int(from_Y))
    row[fieldlist.index("From_X_Y")] = from_X_Y_coords

    to_X = row[fieldlist.index('SHAPE@')].lastPoint.X
    to_Y = row[fieldlist.index('SHAPE@')].lastPoint.Y
    to_X_Y_coords = str(int(to_X)) + "_" + str(int(to_Y))
    row[fieldlist.index("To_X_Y")] = to_X_Y_coords

    LU1cursor.updateRow(row)

arcpy.AddMessage("Update Required Link Fields - Complete at: %s minutes ---" % (round((time.time() - start_time) / 60, 1)))
#cleanup
del fieldlist, row, LU1cursor

#Create Node File
arcpy.AddMessage("Create Nodes Feature Class")
Nodes = arcpy.FeatureVerticesToPoints_management(outLink, "TempNodes", "BOTH_ENDS")

#working fields
AddNewField(Nodes,"X_Y","Text")

NU1cursor, fieldlist = LoadUCursor(Nodes,['SHAPE@XY'])
for row in NU1cursor:
    xcoord = row[fieldlist.index('SHAPE@XY')][0]
    ycoord = row[fieldlist.index('SHAPE@XY')][1]
    row[fieldlist.index("X_Y")] = str(int(xcoord)) + "_" + str(int(ycoord))

    NU1cursor.updateRow(row)
#cleanup
del fieldlist, row, NU1cursor

#Remove Duplicate Points
arcpy.Dissolve_management(in_features=Nodes,
                          out_feature_class=outNodes,
                          dissolve_field="X_Y",
                          statistics_fields="",
                          multi_part="SINGLE_PART",
                          unsplit_lines="DISSOLVE_LINES")

##Check if fields exists, else add new fields
arcpy.AddMessage("Checking for Required Node Output Fields")
AddNewField(outNodes,ID,IDT)
AddNewField(outNodes,X,XT)
AddNewField(outNodes,Y,YT)

arcpy.AddMessage("Update Required Node Fields - Start at: %s minutes ---" % (round((time.time() - start_time) / 60, 1)))

NU2cursor, fieldlist = LoadUCursor(outNodes,['SHAPE@XY'])
i = 0
NIDdict = {}
for row in NU2cursor:
    #Create Node ID Starting with 1
    i = i + 1
    xcoord = row[fieldlist.index('SHAPE@XY')][0]
    ycoord = row[fieldlist.index('SHAPE@XY')][1]
    key = str(int(xcoord)) + "_" + str(int(ycoord))
    NIDdict[key] = i

    row[fieldlist.index(ID)] = i
    row[fieldlist.index(X)] = xcoord
    row[fieldlist.index(Y)] = ycoord

    NU2cursor.updateRow(row)
# cleanup
del fieldlist, row, NU2cursor, #Nfields
arcpy.AddMessage("Update Required Node Fields - Complete at: %s minutes ---" % (round((time.time() - start_time) / 60, 1)))
# Next Steps
# Associate links with from and to node UID.

#list fields, set update cursor to link file
arcpy.AddMessage("Associate links with 'from' and 'to' node UID - Start at: %s minutes ---" % (round((time.time() - start_time) / 60, 1)))

#Set Cursors
LU2cursor, fieldlist = LoadUCursor(outLink)
for row in LU2cursor:

    if row[fieldlist.index("From_X_Y")] in NIDdict:
        from_X_Y_coords = row[fieldlist.index("From_X_Y")]
        row[fieldlist.index(from_node_id)] =  NIDdict[from_X_Y_coords]
    else:
        arcpy.AddWarning("Warning - Check Link: " + str(row[fieldlist.index(link_id)]))

    if row[fieldlist.index("To_X_Y")] in NIDdict:
        to_X_Y_coords = row[fieldlist.index("To_X_Y")]
        row[fieldlist.index(to_node_id)] =  NIDdict[to_X_Y_coords]
    else:
        arcpy.AddWarning("Warning - Check Link: " + str(row[fieldlist.index(link_id)]))

    LU2cursor.updateRow(row)
# cleanup
del fieldlist, row, LU2cursor
arcpy.AddMessage("Associate links with 'from' and 'to' node UID - Complete at: %s minutes ---" % (round((time.time() - start_time) / 60, 1)))

# Create Output Tables
arcpy.AddMessage("Create CSV Outputs: " + outCSVfolder)
OutputCSV(outLink,outLinkCSV,OrderedoutLinkFields)
OutputCSV(outNodes,outNodesCSV,OrderedoutNodeFields)

arcpy.AddMessage("Process Complete: %s minutes ---" % (round((time.time() - start_time) / 60, 1)))

