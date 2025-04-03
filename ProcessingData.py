import pandas as pd
import json
from Mixing import *

def data_processing():
    
    with open(MIXING_CALCULATOR_DATA_FILE, 'r') as file:
        data_v3 = json.load(file)
    subs_names, subs_rank, ranks, subs_price, subs_effects, effect_abbreviations, effect_price, effect_color, products_base, products_effect, rules = data_v3.values()
    
    with open("product_code.json", 'r') as file:
        data_malba_version = json.load(file)
    ranks, products_code, product_rank, subs_rank = data_malba_version.values()
    
    subs_rank       = {key: int(val) for key, val in subs_rank.items()}
    product_rank    = {key: int(val) for key, val in product_rank.items()}
    ranks           = {int(key): val for key, val in ranks.items()}
    subs_price      = {key: int(i) for key, i in subs_price.items()}
    effect_price    = {key: float(i) for key, i in effect_price.items()}
    products_base   = {key: int(i) for key, i in products_base.items()}
    
    effects:dict[str, Effect] = {}
    
    for code, effect in effect_abbreviations.items():
        effects[code] = Effect(code, effect, effect_color[code], effect_price[code])
    
    substances:list[Substance] = []
    
    for subs in subs_effects:
        reactions:list[dict[str]] = []
        subs_code = subs['substance']
        for rule in rules:
            if rule['requires_substance']==subs_code:
                
                reaction:dict[str, Effect] = {
                    'if_not_present': [effects[x] for x in rule['if_not_present']],
                    'if_present': [effects[x] for x in rule['if_present']],
                    'replace': {},
                    # 'addition': []
                }
                
                if 'replace' in rule.keys():
                    old = next(iter(rule['replace']))
                    reaction['replace'] = {effects[old].name: effects[rule['replace'][old]]}
                # if 'add' in rule.keys():
                #     reaction['addition'] = [effects[x] for x in rule['add']]
        
                reactions.append(reaction)
        
        substances.append(Substance(subs_code, subs_names[subs_code], subs_rank[subs_code], effects[subs["effect"][0]], reactions, subs_price[subs_code]))
    
    products:list[Product] = []
    
    for name, effect in products_effect.items():
        product_effect = effect
        if len(effect)>0:
            product_effect = [effects[effect[0]]]
        code = products_code[name]
        products.append(Product(code, product_rank[code], product_effect, products_base[name]))
        
    return [substances, ranks, products, products_code]
    
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

def export_mixing_config(path):
    config_dict = {
        "APP_VERSION": APP_VERSION,
        "MIXING_CALCULATOR_DATA_FILE": MIXING_CALCULATOR_DATA_FILE,
        "MAX_EFFECT": MAX_EFFECT,
        "SUBSTANCE_STACK": SUBSTANCE_STACK,
        "USER_RANK": USER_RANK,
        "REDUNDANT_PRODUCT": REDUNDANT_PRODUCT,
        "SPLIT_PRODUCTS": SPLIT_PRODUCTS,
        "SPLIT_TYPE": SPLIT_TYPE,
        "REDUNDANT_PRODUCT_CODE": REDUNDANT_PRODUCT_CODE,
        "SPLIT_PRODUCTS_CODE": SPLIT_PRODUCTS_CODE,
        "OUTPUT_FILENAME": OUTPUT_FILENAME,
        "USER_SUBSTANCES": USER_SUBSTANCES,
        "USER_PRODUCT_TYPE": USER_PRODUCT_TYPE,
        "USER_TARGET_EFFECTS": USER_TARGET_EFFECTS,
    }
    
    with open(f'{path}/config.json', 'w') as fp:
        json.dump(config_dict, fp)