"""
Name: update_sqltbl_spatial_tags.py
Purpose: for SQL Server table with x/y values, tag which records are within user-specified polygon file.
    Example 1: give tag value of 1 for all parcel points that are in an Environmental Justice polygon.
	Example 2: can also effectively do spatial join, e.g., getting the community type each point is in based on intersection
		with a layer of polygons representing community types.


Author: Darren Conly
Last Updated: Mar 2025
Updated by: 
Copyright:   (c) SACOG
Python Version: 3.x
"""



import re
from time import perf_counter

import pyodbc
import geopandas as gpd

from sqlqry2pandas import sqlqry_to_df
from esri_file_to_dataframe import esri_to_df


def get_odbc_driver():
    # gets name of ODBC driver, with name "ODBC Driver <version> for SQL Server"
    drivers = [d for d in pyodbc.drivers() if 'ODBC Driver ' in d]
    
    if len(drivers) == 0:
        errmsg = f"ERROR. No usable ODBC Driver found for SQL Server." \
        f"drivers found include {drivers}. Check ODBC Administrator program" \
        "for more information."
        
        raise Exception (errmsg)
    else:
        d_versions = [re.findall('\d+', dv)[0] for dv in drivers]
        latest_version = max([int(v) for v in d_versions])
        driver = f"ODBC Driver {latest_version} for SQL Server"
    
        return driver



def run_sql(sql_driver, servername, db, sql_str, auto_commit=True): 
    trustedconn = 'yes'

    conn_str = f"DRIVER={sql_driver};" \
        f"SERVER={servername};" \
        f"DATABASE={db};" \
        f"Trusted_Connection={trustedconn};" \
        "autocommit=True;"
        
    conn = pyodbc.connect(conn_str)
    conn.autocommit = auto_commit

    cur = conn.cursor()
    cur.execute(sql_str)
    cur.commit()
    cur.close()

def apply_updates(tup_id_list, sql_tablename, tbl_uid_field, target_field, target_val, tup_sql_conn_info):
    qry_update = None # if no parcels in chunk are in poly, then no need to update tag; just keep as default
    if len(tup_id_list) == 1: # if only 1 parcel in chunk is in poly, then need to reformat tuple so you do not get sql syntax error
        qry_update = f"UPDATE {sql_tablename} SET {target_field} = {target_val} WHERE {tbl_uid_field} = {tup_id_list[0]}"
    elif len(tup_id_list) > 1:
        qry_update = f"UPDATE {sql_tablename} SET {target_field} = {target_val} WHERE {tbl_uid_field} IN {tup_id_list}"

    if qry_update:
        # run_sql(driver, svrname, db_name, qry_update)--first 3 provided by tup_sql_conn_info
        run_sql(*tup_sql_conn_info, qry_update)


if __name__ == '__main__':
    db_name = 'MTP2024'
    target_tbl_name = 'PARCEL_MASTER' # name of table with field you want to update; assumes table is point layer with x/y fields
    f_x = 'XCOORD'
    f_y = 'YCOORD'
    f_to_update = 'JOBCTR' # name of field in target table whose value you want to set based on spatial association
    f_uid = 'PARCELID' # field in target table indicating unique ID of each point.

    tagval = 1 # where parcels intersect with polygon, specify what tag value (e.g. tag with 1 if you're doing 1/0 field)
    # NOTE - this tagval is overridden if field_map is specified below

    reset_to_defaults = True
	default_val = 0 


    # polygons you want to associate with points in table (e.g. want to find points in these polygons and tag points accordingly)
    source_polys = r'Q:\SACSIM23\2050\DPS\1 Parcel\parcel_prep_2050_v5\parcel_prep_2050_v5.gdb\JobCenter_2050'  # r'I:\Projects\Darren\2025BlueprintTables\Blueprint_Table_GIS\Blueprint_Table_GIS.gdb\EJ_2025_final'
    poly_id_field = 'OBJECTID'

    # field map effectively does a spatial join, rather than simple 1/0 tagging
    field_map = {'Status': 'JOBCTR'} # {source field in polygon file: destination field in parcel table}

    #==============RUN SCRIPT=======================
    # seldom-changed variables
    svrname = 'SQL-SVR'
    srid = 2226
    driver = get_odbc_driver() 

    # reset all field values to a default value
	if reset_to_defaults:
		print("resetting field to default values...")
		qry_setdefault = f"UPDATE {tblname} SET {f_to_update} = {default_val}"
		run_sql(driver, svrname, db_name, qry_setdefault)

    print("loading polygon to associate with...")
    pclfields = [poly_id_field]
    if field_map: pclfields = [fn for fn in field_map.keys()]
    search_polys = esri_to_df(source_polys, include_geom=True, field_list=pclfields, crs_val=srid)

    # set up query for pulling and tagging points in polygon
    pull_qry = f'SELECT {f_uid}, {f_x}, {f_y} FROM {tblname}'
    data_chunks = sqlqry_to_df(query_str=pull_qry, dbname=db_name, 
    servername=svrname, trustedconn='yes', chunk_size=10_000)

    print("processing data...")
    rows_complete = 0
    sql_conn_args = (driver, svrname, db_name)
    for chunk in data_chunks:
        chunk = gpd.GeoDataFrame(chunk, geometry=gpd.points_from_xy(chunk[f_x], chunk[f_y]), crs=f"EPSG:{srid}")
        tagged_pts = gpd.sjoin(chunk, search_polys, predicate='within')
        tagged_pts_len = tagged_pts.shape[0]
        
        if field_map:
            # spatial join tagging (pull attribute values from polygons to populate point fields)
            for srcfield, destfield in field_map.items():
                unique_tvals = tagged_pts[srcfield].drop_duplicates()
                for tval in unique_tvals:
                    chunk_tv = tagged_pts[tagged_pts[srcfield] == tval]
                    tagged_ids = tuple(chunk_tv[f_uid].values)
                    apply_updates(tup_id_list=tagged_ids, sql_tablename=tblname, tbl_uid_field=f_uid, 
                                  target_field=destfield, target_val=tval, tup_sql_conn_info=sql_conn_args)
        else:
            # simple tagging, i.e., if in polygon, then give single "yes" value (e.g. 1)
            tagged_ids = tuple(tagged_pts[f_uid].values)
            apply_updates(tup_id_list=tagged_ids, sql_tablename=tblname, tbl_uid_field=f_uid, 
                                  target_field=f_to_update, target_val=tagval, tup_sql_conn_info=sql_conn_args)
        
        rows_complete += chunk.shape[0]
        if rows_complete % 50_000 == 0:
            print(f" {rows_complete} total rows processed...")

    print(f"complete. {rows_complete} rows processed.")
