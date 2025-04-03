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

def mixing(product:Product, substance:Substance):
    new_effects = substance.react(product.effects[:])
    
    if len(product.code.split("_"))>1:
        new_substances = product.sub_hist[:]
        # if substance.code == "D" and substance in new_substances: 
        #     print("before: ", product.code)
        new_code = f"{product.code}{substance.code}"
    else :
        new_substances = []
        new_code = f"{product.code}_{substance.code}"
    
    new_substances.append(substance)
    # if substance.code == "D" and substance in new_substances: 
    #     print("after : ", new_code)
    return MixedProduct(new_code, product.rank, new_effects, new_substances, product.base_price)

def recursion_mixing(mixed_products:list[Product], product:Product, substances:list[Substance]):
    result = mixed_products[:]
    # temp = []
    if len(product.code.split("_"))>1:
        if len(product.sub_hist) == SUBSTANCE_STACK: return result
    
    for substance in substances:
        
        new_product = mixing(product, substance)
        new_effects_name = get_effects_name(new_product.effects)
                
        if sorted(new_effects_name) != sorted(get_effects_name(product.effects)):
            if REDUNDANT_PRODUCT:
                is_same = False
                for mixed_product in result:
                    if set(mixed_product.effects) == set(new_product.effects):
                        if new_product.cost >= new_product.cost and set(mixed_product.sub_hist) == set(new_product.sub_hist):
                            new_product = None
                            is_same = True
                            break
                if is_same: continue
                
            if len(USER_TARGET_EFFECTS)>0:
                if all(target_effect_name in new_effects_name for target_effect_name in USER_TARGET_EFFECTS):
                    # temp = recursion_mixing(result, new_product, substances)
                    # result.extend(temp)
                    result.append(new_product)
                    print(USER_TARGET_EFFECTS, product.code, new_product.code)
                    # result_code = [mixed_product.code for mixed_product in result]
                    # print(result_code)
            else: result.append(new_product)
            
            result = recursion_mixing(result, new_product, substances)
            
    return result

def produce(product:Product,substances:list[Substance]):
    result = []
    
    if USER_RANK>0 and product.rank>USER_RANK: return result
    
    substances = list(filter(lambda x: x.rank<=USER_RANK, substances))
            
    if len(USER_PRODUCT_TYPE)>0:
        if product.code not in USER_PRODUCT_TYPE:
            print("Produk tidak dapat anda gunakan dengan rank anda saat ini")
            return result
    
    if len(USER_SUBSTANCES)>0:
        if any(substance.name in USER_SUBSTANCES for substance in substances):
            substances = list(filter(lambda x: x.name in USER_SUBSTANCES, substances))
        else: print("Tidak ada Substance yang dapat anda gunakan dengan rank anda saat ini")
            
    result = recursion_mixing(result, product, substances)
    return result
    
    
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
    #     result.extend(temp)