import pandas as pd
import re
import numpy as np
import sys
sys.path.insert(0, '/Users/akhilvelamati/Downloads/AdvDS-Analysis-master/venv/lib/python3.9/site-packages')

def find_null(item):
    if not item or (type(item)!=str and np.isnan(item)) or (type(item)==str 
                                                            and item.strip().lower()in ['null', 'none']):
        return "Unknown"
    return item

def exceptions(data, verbose=False):
    for column in data.columns:
        for i in range(data.shape[0]):
            try:
                find_null(data[column][i])
            except:
                raise Exception(f"the index {i} in {column}")
    if verbose:
        print('No exceptions detected')

def get_ZIP(item):
    zip_code = item.split(',')[-1]
    if re.search(r'\d{5}', zip_code):
        return zip_code
    else:
        return "Unknown"
