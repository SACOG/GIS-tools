"""
Name: association_ddf.py
Purpose: Data class Association which takes SQL server parcel table with X/Y values
    representing parcel centroid, then user-selected polygon file,
    user-defined parcel fields to include polygon fields to include,
    then creates duplicate of parcel table with user-selected fields,
    then associates that temp table with the polygons, in simple 1/0 (yes/no)

    The resulting association object has:
        - dask dataframe of parcel table with polygon association
        - a "master" pyodbc connection that supports the global (## prefix) temp table staying open until closed.
        - a run_sql method that allows queries to be done on the temp table.

    Typical workflow: create association object > run whatever queries you need > close association object.


Author: Darren Conly
Last Updated: Apr 2025
Updated by: 
Copyright:   (c) SACOG
Python Version: 3.x
"""



import re
from pathlib import Path
from dataclasses import dataclass, field
from time import perf_counter

import pyodbc
import pandas as pd
import dask.dataframe as dd
import geopandas as gpd
import arcpy
from arcgis.features import GeoAccessor, GeoSeriesAccessor

from sqlqry2pandas import sqlqry_to_df
from esri_file_to_dataframe import esri_to_df

@dataclass
class AssociateTbl:
    dbname: str

    pcltbl: str
    f_pclx: str
    f_pcly: str
    f_pcluid: str
    f_pcltag: int # will be 1/0 flag indicating if parcel is in polygon or not
    

    fc_polygons: str
    sacog_crs: int=2226
    polygon_fields: list=field(default_factory=lambda: [])
    pcl_where_clause: str=None

    pcl_val_fields: list=field(default_factory=list)

    servername: str='SQL-SVR'
    trustedconn: str='yes'
    auto_commit: bool=True

    def __post_init__(self):
        
        self.field_map = None # placeholder for possible future ability to use spatial join instead of simple 1/0 tag

        self.sql_driver = self.get_odbc_driver()
        self.conn_str = f"DRIVER={self.sql_driver};" \
            f"SERVER={self.servername};" \
            f"DATABASE={self.dbname};" \
            f"Trusted_Connection={self.trustedconn};"
        
        # establish main connection that maintains global temp table 
        self.main_conn = pyodbc.connect(self.conn_str)
        self.main_conn.autocommit = self.auto_commit

        # load polygons into dataframe
        if not self.polygon_fields:
            self.polygon_fields = [arcpy.Describe(self.fc_polygons).OIDFieldName] # if no poly fields specified, just use the OID field

        polys_source_crs = arcpy.Describe(self.fc_polygons).SpatialReference.factoryCode
        self.search_polys = esri_to_df(self.fc_polygons, include_geom=True, field_list=self.polygon_fields, 
                                       crs_val=polys_source_crs).to_crs(self.sacog_crs)
        # if not self.field_map: self.search_polys = self.search_polys.dissolve()
        
        # add 1/0 tags indicating if each parcel is in polygon area *NOTE* this does not filter polygons. POtential future improvement.
        # self.tag_parcels()
        self.dd_taggedpcls = self.make_tagged_pcl_tbl()

    def get_odbc_driver(self):
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


    def run_sql_newconn(self, sql_str, auto_commit=True):
        # runs sql_str with a new connection object.
        conn = pyodbc.connect(self.conn_str)
        conn.autocommit = auto_commit

        cur = conn.cursor()
        cur.execute(sql_str)
        cur.commit()
        cur.close()


    def make_tagged_pcl_tbl(self, target_val=1, chunksize=100_000):
        # set up query for pulling and tagging points in polygon
        str_pcl_val_cols = ''
        if len(self.pcl_val_fields) > 0:
            str_pcl_val_cols = f", {', '.join(self.pcl_val_fields)}"
        pull_qry = f'SELECT {self.f_pcluid}, {self.f_pclx}, {self.f_pcly}{str_pcl_val_cols} FROM {self.pcltbl}'
        data_chunks = sqlqry_to_df(query_str=pull_qry, dbname=self.dbname, 
                                    servername=self.servername, trustedconn=self.trustedconn, 
                                    chunk_size=chunksize)        

        for i, chunk in enumerate(data_chunks):
            # https://stackoverflow.com/questions/76121937/how-to-append-new-data-to-an-existing-parquet-file
            chunk = gpd.GeoDataFrame(chunk, geometry=gpd.points_from_xy(chunk[self.f_pclx], chunk[self.f_pcly]), 
                                     crs=f"EPSG:{self.sacog_crs}")
            
            tagged_pts = gpd.sjoin(chunk, self.search_polys, predicate='within')
            del chunk['geometry'] # free up space

            tagged_pts[self.f_pcltag] = target_val
            tagged_pts = tagged_pts[[self.f_pcluid, self.f_pcltag]]

            chunk = chunk.merge(tagged_pts, how='left', on=self.f_pcluid)
            chunk[self.f_pcltag] = chunk[self.f_pcltag].fillna(0)

            ddchunk = dd.from_pandas(chunk, npartitions=1)

            if i == 0: 
                dd_master = ddchunk
            else:
                dd_master = dd.concat([dd_master, ddchunk])

        return dd_master
    
    def export_associated_tbl(self, format='csv'):
        # placeholder method in case you want to export associated parcel table to CSV or parquet, or even geoparquet
        pass



if __name__ == '__main__':
    db_name = 'MTP2024'
    parcel_data = 'ilut_combined2035_182_DPS' # name of table with field you want to update; assumes table is point layer with x/y fields
    f_tagname = 'birthrate' # name of field that you want the 1/0 tag in indicating whether parcel is within source_polys
    use_pcl_fields = ['PT_TOT_RES', 'TRN_TOT_RES', 'BIK_TOT_RES']

    # polygons you want to associate with points in table (e.g. want to find points in these polygons and tag points accordingly)
    source_polys = r'Q:\MTPSCS_2025\EquityAnalysis\Equity_Analysis_25.gdb\Birth_Rate_Higher_than_nat_avg'  # r'I:\Projects\Darren\2025BlueprintTables\Blueprint_Table_GIS\Blueprint_Table_GIS.gdb\EJ_2025_final'

    # ============================================
    # seldom-changed ILUT field names
    f_x = 'XCOORD'
    f_y = 'YCOORD'
    f_uid = 'PARCELID' # field in target table indicating unique ID of each point.

    example = AssociateTbl(db_name, parcel_data, f_x, f_y, f_uid, f_tagname, source_polys, pcl_val_fields=use_pcl_fields)
    import pdb; pdb.set_trace()