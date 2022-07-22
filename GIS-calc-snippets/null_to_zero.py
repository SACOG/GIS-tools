#Use this function or integrate it in other calc scripts to set nulls as 0
def null_to_zero(nb):
    if nb is None:
        return 0
    else:
        return nb