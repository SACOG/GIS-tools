"""
Name: join_fields_fast.py
Purpose: 
    -Given feature class A and feature class B, with shared attribute key, take a user-selected field
    from FC A and append it to FC B.
    -Normally this is easy to do with an attribute join in the arcgis interface, but for large files (e.g. parcel file)
    a normal join or field calculation can take a long time (hours in some cases). Using SearchCursor(), this script does
    it much faster

    ROADMAP: ideally this schould be turned into an arc toolbox
        
          
Author: Darren Conly
Last Updated: Dec 2021
Updated by: <name>
Copyright:   (c) SACOG
Python Version: 3.x
"""

from time import perf_counter
from arcpy import env, ListFields, management
from arcpy.da import SearchCursor, UpdateCursor


def fast_join(fc_target, fc_target_keyfield, fc_join, fc_join_keyfield, fields_to_join):

    start_time = perf_counter()

    # make field dict for join fc fields {fname: [dtype, len]}
    jfields_names = [f.name for f in ListFields(fc_join)]
    jfields_dtypes = [f.type for f in ListFields(fc_join)]
    jfields_len = [f.length for f in ListFields(fc_join)]
    dts_lens = [[type, len] for type, len in zip(jfields_dtypes, jfields_len)]
    jfields_dict = dict(zip(jfields_names, dts_lens))

    # field names in the target fc
    target_start_fields = [f.name for f in ListFields(fc_target)]

    # as needed, add field(s) to target FC if it doesn't already exist.
    print(f"Adding fields {fields_to_join} to target table {fc_target}...")
    for jfield in fields_to_join:
        if jfield not in target_start_fields:
            ftype = jfields_dict[jfield][0]
            flen = jfields_dict[jfield][1]
            
            management.AddField(in_table=fc_target, field_name=jfield,
                field_type=ftype, field_length=flen)
        else:
            print(f"\t{jfield} already in {fc_target}'s fields. Will be OVERWRITTEN with joined data...")


    cur_fields = [fc_target_keyfield] + fields_to_join
    
    join_dict = {}
    print("reading data from join table...")
    with SearchCursor(fc_join, cur_fields) as scur:
        for row in scur:
            jkey = row[cur_fields.index(fc_join_keyfield)]
            vals_to_join = [row[cur_fields.index(fname)] for fname in fields_to_join]
            join_dict[jkey] = vals_to_join

    print("writing join data to target table...")
    with UpdateCursor(fc_target, cur_fields) as ucur:
        for row in ucur:
            jkey = row[cur_fields.index(fc_join_keyfield)]

            # if a join id value is in the target table but not the join table,
            # skip the join. The values in the resulting joined column will be null for these cases.
            if join_dict.get(jkey):
                vals_to_join = join_dict[jkey]
            else:
                continue

            row_out = [jkey] + vals_to_join
            row = row_out
            ucur.updateRow(row)

    elapsed_sec = round(perf_counter() - start_time, 1)

    print(f"Successfully joined fields {fields_to_join} from {fc_join} onto {fc_target}" \
        f" in {elapsed_sec} seconds!")



if __name__ == '__main__':

    #===============INPUTS=========================

    target_fc = r'I:\Projects\Darren\PPA3_GIS\PPA3_GIS.gdb\hex_ILUT2020_63_DPSppa_web_map'  # feature class that you want the field added to
    jnfield_target = 'GRID_ID' # join key for target feature class

    fc_jn = r'I:\Projects\Darren\PPA3_GIS\PPA3_GIS.gdb\hex_ILUT2035_177_DPS_for_ppa_webmap'  # feature class whose data you want to join to the target fc
    jnfield_jnfc = 'GRID_ID' # join key for feature class you're pulling the new field from
    fc_jn_fields = ['DU35', 'EMPTOT35']  # list of fields in the "join" feature class that you want to append to the "target" feature class

    #===============RUN SCRIPT==============================
    env.overwriteOutput = True
    confirm = input(f"This script may OVERWRITE fields in the target file {target_fc}. Proceed (y/n)? ")
    if confirm.lower() == 'y':
        pass
    else:
        raise Exception("Process canceled.")

    fast_join(target_fc, jnfield_target, fc_jn, jnfield_jnfc, fc_jn_fields)
    



    
