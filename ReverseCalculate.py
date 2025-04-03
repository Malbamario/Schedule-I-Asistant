import pandas as pd
import pprint as pp
import json
import sys
import os
from ProcessingData import *
from ReverseFinalVar import *

def data_laoding():
    with open(MIXED_FILE, 'r') as file:
        mixed_data = pd.read_excel(MIXED_FILE)
    mixed_data.info(verbose=True)
    
def main():
    data_laoding()
    
if __name__=="__main__":
    main()