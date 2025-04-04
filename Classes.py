from typing import Any
from MixingFinalVar import *

class Item:
    def __init__(self, code:str, rank:int, cost:int=0):
        self.code = code
        self.cost = cost
        self.rank = rank
        
class Effect:
    def __init__(self, abbr, name:str, color:str, multi:float=0):
        self.abbr = abbr
        self.name = name
        self.multi = multi
        self.color = color

class Substance(Item):
    def __init__(self, code, name, rank, effect:Effect, reactions:list[dict[str, Any]], cost=0):
        super(Substance, self).__init__(code, rank, cost)
        self.name = name
        self.effect = effect
        self.reactions = reactions
        
    def react(self, effects):
        new_effects = effects
        applied_replacements = set()
        deffered_reactions = []
        
        for reaction in self.reactions:
            if all(effect in effects for effect in reaction['if_present']):
                if any(effect in effects for effect in reaction['if_not_present']):
                    deffered_reactions.append(reaction)  # Ditunda untuk Phase 2
                    continue
                
                # Lakukan penggantian efek
                for old, new in reaction['replace'].items():
                    if old in get_effects_name(effects) and old not in applied_replacements:
                        new_effects = {new if effect.name == old else effect for effect in new_effects}
                        applied_replacements.add(old)
                
                # Tambahkan efek baru jika belum ada
                # for add in reaction['addition']:
                #     if add not in new_effects and len(new_effects) < MAX_EFFECT:
                #         new_effects.append(add)

        for reaction in deffered_reactions:
            if not any(effect in new_effects for effect in reaction['if_not_present']):
                # Lakukan penggantian efek
                for old, new in reaction['replace'].items():
                    if old in get_effects_name(new_effects):
                        new_effects = {new if effect.name == old else effect for effect in new_effects}

                # Tambahkan efek baru
                # if all(effect in effects for effect in reaction['if_present']):
                #     for add in reaction['addition']:
                #         if add not in new_effects and len(new_effects) < MAX_EFFECT:
                #             new_effects.append(add)
        
        if self.effect not in new_effects and len(new_effects) < MAX_EFFECT:
            new_effects.add(self.effect)
        return new_effects

    # def react(self, effects) -> list[Effect]:
    #     new_effects = []
    #     for effect in effects:
    #         if effect in self.reaction: new_effects.append(self.reaction[effect])
    #         else: new_effects.append(effect)
    #     if self.effect not in new_effects and new_effects.len < MAX_EFFECT: new_effects.append(self.effect)
    #     return new_effects

class Product(Item):
    def __init__(self, code, rank, effects:set[Effect], base_price, cost=0):
        super(Product, self).__init__(code, rank, cost)
        self.base_code = code
        self.effects = effects
        self.base_price = base_price
    
    def print_effects(self):
        print([effect.name for effect in self.effects])
    
    def final_price(self) -> int:
        return int(self.base_price*(1+sum(effect.multi for effect in self.effects)))
        
class MixedProduct(Product):
    def __init__(self, code, rank, effect, substances:list[Substance], base_price):
        super(MixedProduct, self).__init__(code, rank, effect, base_price)
        self.base_code = code.split("_")[0]
        self.sub_hist = substances
        self.cost = self.final_cost()
        self.rank = get_substances_rank(substances) if get_substances_rank(substances) > self.rank else self.rank
    
    def print_substances(self):
        print([substance.name for substance in self.sub_hist])
        
    def final_cost(self) -> int:
        return sum(substance.cost for substance in self.sub_hist)

def get_substances_rank(substances:list[Substance]):
    if len(substances)>0:
        return max([substance.rank for substance in substances])
    else: return 0

def get_substances_name(substances:list[Substance])->set:
    if len(substances)>0:
        return set([substance.name for substance in substances])
    else: return {}
    
def get_effects_name(effects:list[Effect])-> set:
    if len(effects)>0:
        return set([effect.name for effect in effects])
    else: return {}