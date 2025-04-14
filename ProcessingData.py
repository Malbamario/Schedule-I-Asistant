import pandas as pd
import json
from Classes import *

def data_processing():
    
    with open(MIXING_CALCULATOR_DATA_FILE, 'r') as file:
        data_v3 = json.load(file)
    
    with open("product_code.json", 'r') as file:
        data_malba_version = json.load(file)
        
    validate_data(data_v3, data_malba_version)
    
    effects = {
        code: Effect(code, name, data_v3["effect_color"][code], float(data_v3["effect_price"][code]))
        for code, name in data_v3["effect_abbreviations"].items()
    }
    
    substances:list[Substance] = [
        Substance(
            subs["substance"],
            data_v3["substances"][subs["substance"]],
            int(data_malba_version["substances_rank"][subs["substance"]]),
            effects[subs["effect"][0]],
            [
                {
                    "if_present": {effects[x] for x in rule["if_present"]},
                    "if_not_present": {effects[x] for x in rule["if_not_present"]},
                    "replace": {effects[old].name: effects[new] for old, new in rule["replace"].items()}
                }
                
                for rule in data_v3["rules"] if rule["requires_substance"] == subs["substance"]
            ],
            int(data_v3["substances_price"][subs["substance"]])
        )
        for subs in data_v3["effects"]
    ]
    
    products = [
        Product(
            code=data_malba_version["product_code"][name],
            rank=int(data_malba_version["product_rank"][data_malba_version["product_code"][name]]),
            effects=set([effects[effect] for effect in data_v3["weed_types"].get(name, [])]),
            base_price=int(data_v3["weed_price"][name])
        )
        for name in data_v3["weed_price"]
    ]
        
    return substances, data_malba_version["ranks"], products, data_malba_version["product_code"]
    
    # effects_df = pd.read_csv("Schedule 1 Game - Effects.csv")
    # products_df = pd.read_csv("Schedule 1 Game - Products.csv").fillna(NULL_STRING_ESCAPE)
    # substances_df = pd.read_csv("Schedule 1 Game - Substances.csv")
    # subs_reaction_df = pd.read_csv("Schedule 1 Game - Substances_reactions.csv").fillna(NULL_STRING_ESCAPE)
    
    # effects:list[Effect] = []
    # for i, effect in effects_df.iterrows():
    #     effects.append(Effect(effect["Name"], effect["Multiplier"]))
        
    # products = []
    # for i, product in products_df.iterrows():
    #     effect = search_effect(product["effects"], effects)
    #     products.append(Product(product["code"], effect, product["base_price"]))
    
    # substances = []
    # for i, substance in substances_df.iterrows():
    #     effect = search_effect(substance["effect"], effects)
    #     reactions = subs_reaction_df[(subs_reaction_df.subs_effect == effect.name)][["product_effect", "exist_influencing_effect", "not_exist_influencing_effect", "effect_result", "other_added_effect"]].to_dict('records')
        
    #     if i==0: print(reactions)
        
    #     substances.append(Substance(substance["code"], effect, reactions))

# def search_effect(effect_name:str, effects: list[Effect]):
#     for e in effects:
#         if e.name == effect_name:
#             return e

def validate_data(data_v3, data_product):
    # Validate substances
    for substance in data_v3["substances"]:
        if substance not in data_product["substances_rank"]:
            raise ValueError(f"Substance {substance} is missing in substances_rank")

    # Validate products
    for product in data_product["product_code"]:
        if product not in data_v3["weed_price"]:
            raise ValueError(f"Product {product} is missing in weed_price")

def export_mixing_config(path, start, end=""):
    config_dict = {
        "APP_VERSION": APP_VERSION,
        "MIXING_CALCULATOR_DATA_FILE": MIXING_CALCULATOR_DATA_FILE,
        "MAX_EFFECT": MAX_EFFECT,
        "SUBSTANCE_STACK": SUBSTANCE_STACK,
        "USER_RANK": USER_RANK,
        "MODE": MODE,
        "NO_REDUNDANT_PRODUCT": NO_REDUNDANT_PRODUCT,
        "SPLIT_PRODUCTS": SPLIT_PRODUCTS,
        "SPLIT_TYPE": SPLIT_TYPE,
        "OUTPUT_FILENAME": OUTPUT_FILENAME,
        "USER_SUBSTANCES": USER_SUBSTANCES,
        "USER_PRODUCT_TYPE": USER_PRODUCT_TYPE,
        "USER_TARGET_EFFECTS": USER_TARGET_EFFECTS,
        "start_time": start,
        "end_time": end
    }
    
    with open(f'{path}/config.json', 'w') as fp:
        json.dump(config_dict, fp)
    print(f"config exported at {path}/config.json")
        
def object_2_df(new_products:list[Product], product_name='', product_type:dict={}):
    result = []
    for product in new_products:
        result_data = {
            "code": product.code,
            "product_type": product_type[product.base_code] if product_type else product_name,
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
