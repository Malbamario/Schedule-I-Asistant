import sys
from ProcessingData import *

# def reacting(reactions:list[dict[str,]], subs_effect, product_effects):
#     new_effects = []
#     for effect in product_effects:
#         for reaction in reactions:
#             if all(comb in reaction["combination"] for comb in [subs_effect, effect]):
#                 if reaction["exist_influencing_effect"] != NULL_STRING_ESCAPE:
#                     if reaction["exist_influencing_effect"] not in product_effects:
#                         continue
#                 if reaction["not_exist_influencing_effect"] != NULL_STRING_ESCAPE:
#                     if reaction["not_exist_influencing_effect"] in product_effects:
#                         continue
#                 new_effects.append(reaction["effect_result"])
#                 if len(new_effects)<8:
#                     new_effects.append(subs_effect)
#                     if reaction["other_added_effect"] != NULL_STRING_ESCAPE:
#                         new_effects.append(reaction["other_added_effect"])
#     return new_effects

def mixing(product:Product, substance:Substance)->MixedProduct:
    new_effects = substance.react(product.effects)
    new_substances = product.sub_hist[:] if len(product.code.split("_")) > 1 else []
    new_code = f"{product.code}_{substance.code}" if not new_substances else f"{product.code}{substance.code}"
    new_substances.append(substance)
    # if substance.code == "D" and substance in new_substances: 
    #     print("after : ", new_code)
    # print(new_code, ', '.join(sorted(get_effects_name(product.effects))), ' -> ', ', '.join(sorted(get_effects_name(new_effects))), substance.name)
    return MixedProduct(new_code, product.rank, new_effects, new_substances, product.base_price)

def redundant_check(mixed_products: list[MixedProduct], new_product: MixedProduct):
    worse_products = []
    new_product_effects_name = get_effects_name(new_product.effects)
    new_product_sub_name = set(get_substances_name(new_product.sub_hist))
    
    for mixed_product in mixed_products:
        mixed_product_sub_name = set(get_substances_name(mixed_product.sub_hist))
        
        if get_effects_name(mixed_product.effects) == new_product_effects_name:
            in_mixed_product_sub_name = all(sub in mixed_product_sub_name for sub in new_product_sub_name)
            in_new_product_sub_name = all(sub in new_product_sub_name for sub in mixed_product_sub_name)
            if mixed_product_sub_name != new_product_sub_name and not (in_mixed_product_sub_name or in_new_product_sub_name):
                if new_product.cost < mixed_product.cost:
                    if NO_REDUNDANT_PRODUCT: worse_products.append(mixed_product)
                    continue
                elif new_product.cost == mixed_product.cost: continue
            
            return (True, worse_products)
    return(False, worse_products)
    

def recursion_mixing_dfs(mixed_products: list[MixedProduct], product: Product, substances: list[Substance]):
    result = mixed_products[:]
    depth = len(product.sub_hist) if "_" in product.code else 0
    
    if depth == SUBSTANCE_STACK:
        return result

    for substance in substances:
        new_product = mixing(product, substance)
        new_product_effects_name = get_effects_name(new_product.effects)
        
        if new_product_effects_name == get_effects_name(product.effects):
            continue
            
        result = recursion_mixing_dfs(result, new_product, substances)
        print(f"Depth: {depth}, Results: {len(mixed_products)}, code={new_product.code}  ", end='\r')
        
        if USER_TARGET_EFFECTS:
            if not all(effect in USER_TARGET_EFFECTS for effect in new_product_effects_name):
                continue
            
        # if USER_TARGET_EFFECTS:
        #     if not all(effect in new_product_effects_name for effect in USER_TARGET_EFFECTS):
        #         continue
        
        is_redundant, worse_products = redundant_check(result, new_product)
        
        if is_redundant: continue
        else:
            for worse_product in worse_products:
                result.remove(worse_product)
        
        # mixed_product_sub_name = [get_substances_name(mixed_product.sub_hist) for mixed_product in result]
        # print(all(sub in new_product_sub_name for sub in mixed_product_sub_name))
        result.append(new_product)
    return result

def mixing_bfs(base_product: Product, substances: list[Substance], product_name:str, path:str):
    temp = [base_product]
    
    result = []
    for depth in range (SUBSTANCE_STACK):
        temp2 = []
        for product in temp:
            for substance in substances:
                new_product = mixing(product, substance)
                new_product_effects_name = get_effects_name(new_product.effects)
                # print(new_product.code, ', '.join(sorted(get_effects_name(product.effects))), ' -> ', ', '.join(sorted(new_product_effects_name)), substance.name)
                
                if new_product_effects_name == get_effects_name(product.effects):
                    continue
                # if depth>0:
                #     if depth+1< len(product.sub_hist):
                #         print(f"Depth: {depth}, Temps: {len(temp)}, Results: {len(result)}, Product sub len: {len(product.sub_hist)}  ")
                temp2.append(new_product)
                    
                print(f"Depth: {depth}, Results: {len(result)}, code={new_product.code}  ", end='\r')
                
                if USER_TARGET_EFFECTS:
                    if not all(effect in USER_TARGET_EFFECTS for effect in new_product_effects_name):
                        continue
                    
                # if USER_TARGET_EFFECTS:
                #     if not all(effect in new_product_effects_name for effect in USER_TARGET_EFFECTS):
                #         continue
                
                is_redundant, worse_products = redundant_check(result, new_product)
                
                if is_redundant: continue
                else:
                    for worse_product in worse_products:
                        result.remove(worse_product)
                
                # mixed_product_sub_name = [get_substances_name(mixed_product.sub_hist) for mixed_product in result]
                # print(all(sub in new_product_sub_name for sub in mixed_product_sub_name))
                result.append(new_product)
        
        if depth > 1:
            print(f"\nDepth: {depth}, Results: {len(result)}")
            print(f"{base_product.code} Depth {depth} exported")
            result_df = object_2_df(result, product_name=product_name)
            export_2_xlsx(path, result_df, output_filename=f"{product_name}-D{depth}-{OUTPUT_FILENAME}")
            result = []
        temp = None
        temp = temp2[:]

def filter_prod_n_subs(product:Product,substances:list[Substance]):
    if USER_RANK>0 and product.rank>USER_RANK:
        print("Produk tidak dapat anda gunakan dengan rank anda saat ini")
        return (None, substances)
    
            
    if USER_PRODUCT_TYPE and product.code not in USER_PRODUCT_TYPE:
        print("Produk tidak ada pada daftar produk yang ingin anda gunakan")
        return (None, substances)
    
    substances = [s for s in substances if s.rank <= USER_RANK]
    
    if len(USER_SUBSTANCES)>0:
        substances = [s for s in substances if s.name in USER_SUBSTANCES]
        if not substances:
            print("Substance tidak ada pada daftar substance yang ingin anda gunakan")
            return (None, substances)
    # print(', '.join(sorted(get_substances_name(substances))))
    return (product, substances)

def produce_BFS(product:Product,substances:list[Substance], product_name:str, path):
    product, substances = filter_prod_n_subs(product, substances)
    if product: mixing_bfs(product, substances, product_name, path)

def produce_DFS(product:Product,substances:list[Substance]):
    product, substances = filter_prod_n_subs(product, substances)
    if product: return recursion_mixing_dfs([], product, substances)
    return []