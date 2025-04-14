from datetime import datetime
from mpi4py import MPI
import pandas as pd
import pprint as pp
import json
import os
from MixingFinalVar import *
from Mixing import *


substances, ranks, products, products_code = data_processing()
product_type = {item:name for name, item in products_code.items()}

substances = [substance for substance in substances if substance.code == "J" or substance.code == "H"]

for product in products:
    if product.code == "W01":
        f1_mixed = None
        f2_mixed = None
        for sub in substances:
            if sub.code == "J":
                f1_mixed = mixing(product, sub)
        for sub in substances:
            if sub.code == "H":
                f2_mixed = mixing(f1_mixed, sub)
        print(get_effects_name(f1_mixed.effects))
        print(get_effects_name(f2_mixed.effects))
        