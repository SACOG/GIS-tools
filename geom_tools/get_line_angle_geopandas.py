"""
Name: get_line_angle_geopandas.py
Purpose: using first and last points on line, gets angle of a line in geopandas geodataframe


Author: Darren Conly
Last Updated: Feb 2023
Updated by: 
Copyright:   (c) SACOG
Python Version: 3.x
"""


import math

def get_line_angle(line_geom):
    coordlist = line_geom.coords
    x_start = coordlist[0][0]
    y_start = coordlist[0][1]
    x_end = coordlist[-1][0]
    y_end = coordlist[-1][1]
    
    xdiff = x_end - x_start
    ydiff = y_end - y_start
    
    angle = math.degrees(math.atan2(ydiff,xdiff))
    
    return angle



if __name__ == '__main__':
    pass

    """
    example application

    gdf['angle'] = gdf['geometry'].apply(lambda x: get_line_angle(x))
    """