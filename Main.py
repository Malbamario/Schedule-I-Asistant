from datetime import datetime
from mpi4py import MPI
import pandas as pd
import pprint as pp
import json
import sys
import os
from ProcessingData import *

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

def object_2_df(new_products:list[Product], product_type:dict):
    result = []
    for product in new_products:
        result_data = {
            "code": product.code,
            "product_type": product_type[product.base_code],
            "effects": ', '.join(sorted(get_effects_name(product.effects))),
            "effects_len": len(product.effects),
            "substances": ', '.join(get_substances_name(product.sub_hist)),
            "substances_len": len(product.sub_hist),
            "minimum_rank": product.rank,
            "mix_cost": product.cost,
            "sell_price": product.final_price()
        }
        if SPLIT_PRODUCTS: result_data.pop("product_type", None)
        result.append(result_data)
        
    return pd.DataFrame(result)

def export_2_xlsx(path, df:pd.DataFrame=pd.DataFrame([]), list_df:list[pd.DataFrame]=[], output_filename="", products_name=[]):
    if SPLIT_PRODUCTS and SPLIT_TYPE=="Sheet":
        with pd.ExcelWriter(output_filename) as writer:
            for i, df in enumerate(list_df):
                df.to_excel(writer, sheet_name=products_name[i], index=False)
            writer.save()
    else:
        output_filename = OUTPUT_FILENAME if output_filename=="" else output_filename
        df.to_excel(f"{path}/{output_filename}", index=False)
    print(f'{output_filename} is exported!')

def main():
    if rank==0:
        start_time = datetime.now()
        path = f"Result/{start_time.strftime("%Y-%m-%d %H.%M.%S")}_{os.path.splitext(os.path.basename(OUTPUT_FILENAME))[0]}"
        os.mkdir(path)
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
        path = None
    comm.barrier()
    
    substances, ranks, products, products_code, product_type, path = comm.bcast([substances, ranks, products, products_code, product_type, path], root=0)
    
    temp= [None] * len(products)
    products_name = [None] * len(products)
    for i, product in enumerate(products):
        if rank==i%size:
            print(f"{rank} is running the {product.code}")
            print(f"{product_type[product.base_code]} is processing ...", flush=True)
            new_products:list[MixedProduct] = produce(product, substances)
            if SPLIT_PRODUCTS:
                if len(new_products)>0:
                    match SPLIT_TYPE:
                        case "File":
                            print(f"{product.code} exported")
                            df = object_2_df(new_products, product_type)
                            export_2_xlsx(path, df, output_filename=f"{product_type[product.base_code]}-{OUTPUT_FILENAME}")
                        case "Sheet":
                            # print(i, product.code)
                            # temp[i] = product.code
                            # print(i, temp)
                            temp[i] = object_2_df(new_products, product_type)
                            products_name[i] = product_type[product.base_code]
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
        df = object_2_df(result, product_type)
        export_2_xlsx(path, df)

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