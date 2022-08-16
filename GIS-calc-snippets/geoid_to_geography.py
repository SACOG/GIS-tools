#Use this code to extract a geography from geoid
#Set only one geography you want to extract as true
def geoid_to_geography(geoid,state=False,county=False,tract=True,block_group=False):
    if state+county+tract+block_group!=1:
        raise Exception("Select ONE geography")
    if geoid is None:
        return None 
    geoid_s=str(geoid)
    digits=[i for i in geoid_s]
    if state==True:
        return int(digits[0]+digits[1])
    elif county==True:
        return int(digits[2]+digits[3]+digits[4])
    elif tract==True:
        return int(digits[5]+digits[6]+digits[7]+digits[8]+digits[9]+digits[10])
    elif block_group==True:
        return int(digits[11])
    else:
        return None

geoid_to_geography(geoid,state=False,county=False,tract=True,block_group=False)
