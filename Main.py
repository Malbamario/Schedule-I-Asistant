from datetime import datetime
from mpi4py import MPI
import pandas as pd
import pprint as pp
import json
import os
from MixingFinalVar import *
from Mixing import *

comm = MPI.COMM_WORLD
rank = comm.rank
size = comm.size

def reduce_list(list1:list, list2:list):
    for i, nxtItem in enumerate(list2):
        if nxtItem: list1[i] = nxtItem
    return list1

def opReduceList(xmem, ymem, dt):
    if len(xmem) != 0 and len(ymem) != 0: return reduce_list(xmem, ymem)
    elif len(xmem) != 0: return xmem
    else: return ymem

def main():
    if rank==0:
        start_time = datetime.now()
        if MODE == "DFS":
            path = f"Result/DFS/{start_time.strftime("%Y-%m-%d %H.%M.%S")}_{os.path.splitext(os.path.basename(OUTPUT_FILENAME))[0]}"
        elif MODE == "BFS":
            path = f"Result/BFS/{start_time.strftime("%Y-%m-%d %H.%M.%S")}_{os.path.splitext(os.path.basename(OUTPUT_FILENAME))[0]}"
        os.makedirs(path)
        export_mixing_config(path, start_time.strftime("%Y-%m-%d %H.%M.%S"))
        
        print(f"The program is start from {start_time.strftime("%Y-%m-%d %H.%M.%S")}", flush=True)
        substances, ranks, products, products_code = data_processing()
        product_type = {item:name for name, item in products_code.items()}
    else:
        substances = None
        ranks = None
        products = None
        products_code = None
        product_type = None
    comm.barrier()
    
    substances, ranks, products, products_code, product_type = comm.bcast([substances, ranks, products, products_code, product_type], root=0)
    if MODE == "DFS":
        temp= [None] * len(products)
        products_name = [None] * len(products)
        for i, product in enumerate(products):
            if rank==i%size:
                print(f"{rank} is running the {product.code}")
                print(f"{product_type[product.base_code]} is processing ...", flush=True)
                new_products:list[MixedProduct] = produce_DFS(product, substances)
                if SPLIT_PRODUCTS:
                    if len(new_products)>0:
                        match SPLIT_TYPE:
                            case "File":
                                print(f"{product.code} exported")
                                df = object_2_df(new_products, product_type=product_type)
                                export_2_xlsx(path, df, output_filename=f"{product_type[product.base_code]}-{OUTPUT_FILENAME}")
                            case "Sheet":
                                # print(i, product.code)
                                # temp[i] = product.code
                                # print(i, temp)
                                products_name[i] = product_type[product.base_code]
                                temp[i] = object_2_df(new_products, product_name=products_name[i])
                            case _:
                                sys.exit("The Split Type not Recognized or not defined")
                else:
                    # temp[i] = product.code
                    temp[i] = new_products
                print(f"{product_type[product.base_code]} is done at {datetime.now().strftime("%Y-%m-%d %H.%M.%S")}\n", flush=True)

        comm.barrier()
        
        temp = comm.reduce(temp, MPI.Op.Create(opReduceList, True), root=0)
        if SPLIT_PRODUCTS and SPLIT_TYPE=="Sheet":
            products_name = comm.reduce(products_name, MPI.Op.Create(opReduceList, True), root=0)
            if rank==0:
                temp = list(filter(lambda x: x is not None, temp))
                products_name = list(filter(lambda x: x is not None, products_name))
                # pp.pprint(temp)
                # pp.pprint(products_name)
                # sys.stdout.flush()
                export_2_xlsx(path, list_df=temp, products_name=products_name)
        
        if not SPLIT_PRODUCTS and rank==0:
            # pp.pprint(temp)
            # sys.stdout.flush()
            temp = list(filter(lambda x: x is not None, temp))
            result = []
            for products in temp: result.extend(products)
            df = object_2_df(result, product_type=product_type)
            export_2_xlsx(path, df)
            
    elif MODE == "BFS":
        for i, product in enumerate(products):
            if rank==i%size:
                print(f"{rank} is running the {product.code}")
                print(f"{product_type[product.base_code]} is processing ...", flush=True)
                produce_BFS(product, substances, product_type[product.code], path)
                print(f"{product_type[product.base_code]} is done at {datetime.now().strftime("%Y-%m-%d %H.%M.%S")}\n", flush=True)
    
    comm.barrier()
    
    
    if rank==0:
        end_time = datetime.now()
        td = end_time-start_time
        print(f"The program is end at {end_time.strftime("%Y-%m-%d %H.%M.%S")}")
        
        hours, remainder = divmod(td.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        print(f"the program has been running for {hours}.{minutes}.{seconds}")
        
        export_mixing_config(path, start_time.strftime("%Y-%m-%d %H.%M.%S"), end_time.strftime("%Y-%m-%d %H.%M.%S"))
    
if __name__=="__main__":
    main()