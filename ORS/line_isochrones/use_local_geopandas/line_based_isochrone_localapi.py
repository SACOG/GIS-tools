"""
Name: line_based_isochrone.py
Purpose: Generates isochrones for user-specified line using OpenRouteService API.
THIS VERSION USES A LOCAL API VIA INSTALLING A LOCAL DOCKER IMAGE OF THE ORS CODE
    References:
        -https://openrouteservice.org/
        -https://openrouteservice.org/dev/#/api-docs/v2/isochrones/{profile}/post
        
          
Author: Darren Conly
Last Updated: Nov 2021
Updated by: <name>
Copyright:   (c) SACOG
Python Version: 3.x
"""

import os
import datetime as dt
from time import perf_counter, sleep
import requests
import geopandas as gpd
import pandas as pd
from arcgis.features import GeoAccessor, GeoSeriesAccessor
import arcpy
arcpy.env.overwriteOutput = True


def sedf_to_fc_workaround(in_sedf, out_fc_path):
    """Circuitous method to convert a Spatially-Enabled data frame to feature class
    SEDF is *supposed* to be convertible directly to feature class, but as of 12/19/2021,
    there is issue where the resulting feature class is empty, thus for now there is this workaround method.
    More info at https://community.esri.com/t5/arcgis-api-for-python-questions/converting-spatially-enabled-dataframe-to-feature/m-p/1127417
    """
    out_fgdb = os.path.dirname(out_fc_path)
    out_fc_name = os.path.basename(out_fc_path)
    
    # https://developers.arcgis.com/python/api-reference/arcgis.features.toc.html#featureset
    featureset = in_sedf.spatial.to_featureset()
    featureset.save(save_location=out_fgdb, out_name=out_fc_name)

class ORSIsochrone:
    def __init__(self, api_file, isoc_type, range_mins_or_mi, trav_mode, batch_size=5):
        """Generates an isochrone (time- or distance-based buffer polygon) around

        Args:
            api_file ([type]): one-line text file containing the ORS API key
            isoc_type (string): whether the iso is time- or distance-based
            range_mins_or_mi (int): max time (in minutes) or distance (in miles) from origin point
            trav_mode (string): travel mode used
            batch_size (int, default=5): number of points to make isochrones around for each ORS API call
            As of 12/12/2021, each ORS call can generate isochrones for up to 5 points. Thus, batch_size default value is 5
        """

        self.trav_modes = ["driving-car", "foot-walking", "cycling-regular"]
        self.isoc_types = ["time", "distance"] # whether you want isochrone based on time or distance
        self.api_key = self.get_api_key(api_file)
        self.isoc_type = isoc_type
        self.trav_mode = trav_mode
        self.range_input_val = range_mins_or_mi
        self.isoc_range = self.get_range(self.range_input_val)
        self.batch_size = batch_size

    def get_api_key(self, api_txtfile):
        """Takes in api_textfile and returns string containing ORS API key"""
        with open(api_txtfile, 'r') as f:
            api_key = f.readline()
        return api_key

    def get_range(self, in_range_val):
        """Takes the user's in_range_val (minutes for time-based isochrone 
        or miles for distance) and converts them to ORS's range units
        (seconds for time; meters for distance)"""
        if self.isoc_type == "time":
            out_val = in_range_val * 60 # convert minutes to seconds, which ORS uses
        elif self.isoc_type == "distance":
            out_val = in_range_val * 1609.34 # convert miles to meters
        else:
            raise Exception(f"""Isochrone type must be either 'distance' or 'time'. 
            '{self.isoc_type}'' is not an acceptable value.""")

        return out_val


    def points_from_line_fc(self, line_fc, interval_ft):
        """Make a list of X/Y coordinates that the ORS API can take in and build isochrones around.
            Example: If you want to build isochrones every 1,000 feet along a 1-mile project line,
            you would specify interval_ft = 1000
        Returns: lists of X/Y coordinate batches that can be fed into ORS API to generate isochrones around each X/Y point
        """

        # ORS needs WGS84 (WKID 4326) coordinate system to generate isochrones
        sref_wgs84 = arcpy.SpatialReference(4326)


        # make temporary feature class of points at regular intervales along lines
        # FYI, time permitting, the shapely library has some options for doing this that *might* be faster than ESRI tool
        temp_pt_fc = os.path.join("memory", "TEMP_pts") 
        
        arcpy.management.GeneratePointsAlongLines(line_fc, temp_pt_fc,
                                                    "DISTANCE", 
                                                    Distance=f"{interval_ft} feet", 
                                                    Include_End_Points="END_POINTS")


        # calc x/y coords in WGS84 (WKID 4326) for compatibility with ORS API
        pt_fl = "pt_fl"
        arcpy.MakeFeatureLayer_management(temp_pt_fc, pt_fl)
        arcpy.AddGeometryAttributes_management(Input_Features=pt_fl, 
                                            Geometry_Properties=['POINT_X_Y_Z_M'],
                                            Coordinate_System=sref_wgs84)

        # make array of points at regular intervals along line to
        line_pts = []
        with arcpy.da.SearchCursor(pt_fl, ["POINT_X", "POINT_Y"]) as cur:
            for row in cur:
                lon = row[0]
                lat = row[1]
                pt_coords = [lon, lat]  # [lat, lon]
                line_pts.append(pt_coords)
                
        # batchify points into groups of 5, because ORS API cannot process more than 5 points in single call
        line_pts_batched = [line_pts[i:i+self.batch_size] for i, v in enumerate(line_pts) if i % self.batch_size == 0]
        
        return line_pts_batched


    def make_line_isochrone(self, in_line_fc, interval_feet, output_file=None):
        """[summary]

        Args:
            in_line_fc (shape file or feature class): line around which you'll be making a buffer
            interval_feet (int): interval between points that you make along line. Isochrones will be around these points.
            output_file (file path, optional): Output feature class or SHP of the polygon. Defaults to None.

            Returns: ESRI shapefile or feature class if output_file specified. Otherwise returns pandas geodataframe.
        """
        

        self.in_line_fc = in_line_fc # if user enters line_fc, make it a new attribute of the ORSIsochrone class

        # generate the points along the input line around which you'll generate isochrones.
        line_pts_batched = self.points_from_line_fc(in_line_fc, interval_feet)

        gdf_master = gpd.GeoDataFrame() # Create geodaframe to store all polygons in

        # Go through each batch of 5 points and draw an isochrone around them, then combine all the batches together
        # into 1 geodatframe with all relevant isochrone polygons in it. Next step would then be dissolve all polygons.

        for i, pts_batch in enumerate(line_pts_batched):
            
            # sleep(3) # ORS online API only accepts 20 hits/minute, so cannot overload it! Shouldn't be issue for local API

            body = {"locations":pts_batch, "range":[self.isoc_range], "range_type":self.isoc_type}

            headers = {
                'Accept': 'application/json, application/geo+json, application/gpx+xml, img/png; charset=utf-8',
                'Authorization': self.api_key,
                'Content-Type': 'application/json; charset=utf-8'
            }

            # api_url = f'https://api.openrouteservice.org/v2/isochrones/{self.trav_mode}' # use remote API
            api_url = f'http://localhost:8080/ors/v2/isochrones/{self.trav_mode}' # use local API installed via docker
            call = requests.post(api_url, json=body, headers=headers)
            
            try:
                polygon_json = call.json()['features']
            except:
                json_result = call.json()
                exc_msg = f"""
                    Script Failed. Last request to OpenRouteService API returned the following message:\n
                    {json_result}
                    """
                raise Exception(f"{exc_msg}")
            
            gdf_batch = gpd.GeoDataFrame.from_features(polygon_json) # FYI, as of 12/12/2021, geopandas read_file() does not work due to a fiona compatibility issue.
            gdf_batch['dissolve_col'] = 0
            gdf_master = gdf_master.append(gdf_batch)
        
        # 'value' is column that always gets made in ORS API call, and it has same value, so is good for dissolving all polys in GDF into single poly
        # 3/25/2022 WARNING - Using Geopandas dissolve is way faster than ESRI's/arcpy, but it creates errors and polygons
        # that are incorrect. Use with caution and carefully review all outputs.
        gdf_diss = gdf_master.dissolve('value') 
        # print("created gdf_diss...")

        if output_file:
            sedf = pd.DataFrame.spatial.from_geodataframe(gdf_diss)
            # sedf.spatial.to_featureclass(output_file) # as of 12/19/2021, this method returns empty featureclass, so using workaround function.
            sedf_to_fc_workaround(sedf, output_file)
        else:
            return gdf_diss


if __name__ == '__main__':

    # =================INPUTS==========================
    in_api_file = r"C:\Users\dconly\GitRepos\GIS-tools\ORS\api2_DO_NOT_COMMIT.txt"  # input("enter file path of the ORS API text file: ")
    mode = "cycling-regular"  # "driving-car", "foot-walking", "cycling-regular"
    isoctype = "distance" # "time", "distance" 
    travel_range_mins = 0.5 # enter time in minutes, distance in miles
    batch_sz = 1 # how many points you want to make isos around for each request you send to ORS--max is 5.

    project_line = r'I:\Projects\Darren\PPA_V2_GIS\ATPTrailsAnalyses2022.gdb\LongerTrails2022'  # r"I:\Projects\Darren\PEP\PEP_GIS\PEP_GIS.gdb\test_sr51"  #  
    isoch_pts_per_mile = 8 # how close together you want the isochrones' origin points to be along the project line
    output_fgdb = r"I:\Projects\Darren\PPA_V2_GIS\ATPTrailsAnalyses2022.gdb" # file geodatabase where output isochrone FC will go


    # =================RUN SCRIPT==========================
    start_time = perf_counter()
    tstamp_str = str(dt.datetime.now().strftime('%Y%m%d_%H%M'))

    mode_short = mode.split('-')[0]
    out_fc_name = f"isoch_{mode_short}"
    output_fc = os.path.join(output_fgdb, f"{out_fc_name}{tstamp_str}")

    isoch_pt_interval = 5280 / isoch_pts_per_mile

    print("building isochrone...")
    line_iso = ORSIsochrone(api_file=in_api_file, isoc_type=isoctype,
                            range_mins_or_mi=travel_range_mins, trav_mode=mode, batch_size=batch_sz)

    line_iso.make_line_isochrone(in_line_fc=project_line, interval_feet=isoch_pt_interval,
                            output_file=output_fc)


    elapsed = round(perf_counter() - start_time,1)
    print(f"Made isochrone around {project_line} in {elapsed} seconds. Output is {output_fc}.")



        





