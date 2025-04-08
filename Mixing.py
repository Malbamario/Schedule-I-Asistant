import logging
logging.basicConfig(level=logging.INFO)
import sys
from Classes import *

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
    return MixedProduct(new_code, product.rank, new_effects, new_substances, product.base_price)

def recursion_mixing(mixed_products: list[MixedProduct], product: Product, substances: list[Substance]):
    result = mixed_products[:]
    depth = len(product.sub_hist) if len(product.code.split("_")) > 1 else 0
    
    if depth == SUBSTANCE_STACK:
        return result

    for substance in substances:
        new_product = mixing(product, substance)
        new_product_effects_name = get_effects_name(new_product.effects)
        new_product_sub_name = get_substances_name(new_product.sub_hist)
        
        if new_product_effects_name == get_effects_name(product.effects):
            continue
        
        result = recursion_mixing(result, new_product, substances)
        print(f"Depth: {depth}, Results: {len(mixed_products)}, code={new_product.code}", end='\r')
        
        if USER_TARGET_EFFECTS:
            if not all(effect in USER_TARGET_EFFECTS for effect in new_product_effects_name):
                continue
            
        # if USER_TARGET_EFFECTS:
        #     if not all(effect in new_product_effects_name for effect in USER_TARGET_EFFECTS):
        #         continue
        
        is_redundant = False
        for idx, mixed_product in enumerate(result):
            mixed_product_sub_name = set(get_substances_name(mixed_product.sub_hist))
            
            if get_effects_name(mixed_product.effects) == new_product_effects_name:
                in_mixed_product_sub_name = all(sub in mixed_product_sub_name for sub in new_product_sub_name)
                in_new_product_sub_name = all(sub in new_product_sub_name for sub in mixed_product_sub_name)
                if mixed_product_sub_name != new_product_sub_name and not (in_mixed_product_sub_name or in_new_product_sub_name):
                    if new_product.cost < mixed_product.cost:
                        if NO_REDUNDANT_PRODUCT: result.pop(idx)
                        continue
                    elif new_product.cost == mixed_product.cost: continue
                
                is_redundant = True
                break
        
        if is_redundant: continue
        # mixed_product_sub_name = [get_substances_name(mixed_product.sub_hist) for mixed_product in result]
        # print(all(sub in new_product_sub_name for sub in mixed_product_sub_name))
        result.append(new_product)
    return result

def produce(product:Product,substances:list[Substance]):
    
    if USER_RANK>0 and product.rank>USER_RANK:
        print("Produk tidak dapat anda gunakan dengan rank anda saat ini")
        return []
    
            
    if USER_PRODUCT_TYPE and product.code not in USER_PRODUCT_TYPE:
        print("Produk tidak ada pada daftar produk yang ingin anda gunakan")
        return []
    
    substances = [s for s in substances if s.rank <= USER_RANK]
    
    if len(USER_SUBSTANCES)>0:
        substances = [s for s in substances if s.name in USER_SUBSTANCES]
        if not substances:
            print("Substance tidak ada pada daftar substance yang ingin anda gunakan")
            return []
    
    return recursion_mixing([], product, substances)
    
    
    # for i in range(SUBSTANCE_STACK):
    #     temp2=[]
    #     for product in temp:
    #         for substance in substances:
    #             mixed_product = mixing(product, substance)
    #             mixed_effects_name = get_effects_name(mixed_product.effects)
    #             if sorted(mixed_effects_name) != sorted(get_effects_name(product.effects)):
    #                 if any(mixed_effect_name in USER_TARGET_EFFECT for mixed_effect_name in mixed_effects_name)
    #                     temp2.append(mixed_product)
    #     temp = temp2[:]
    #     result.extend(temp