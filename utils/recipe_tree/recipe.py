import json
import requests

from utils.recipe_tree.constants import URL_TO_FILES
from utils.recipe_tree.exceptions import RecipeNotFoundException

class Recipe:
    def __init__(self, items_required):
        self.items_required = items_required
    
class Item:
    def __init__(self, name, recipe = None):
        self.recipe = recipe
        self.name = name
        self.craftable = recipe is not None

def find_item_recipe(item_name):
    recipe_data = None

    try:
        recipe_data = json.loads(requests.get(URL_TO_FILES + item_name + ".json").text)
    except:
        raise RecipeNotFoundException()
    
    if "recipe" in recipe_data:
        recipe_items_basic = {}
        for key in recipe_data["recipe"].keys():
            if recipe_data["recipe"][key] != "":
                name, amount = recipe_data["recipe"][key].split(":")
                if name in recipe_items_basic:
                    recipe_items_basic[name] += int(amount)
                    continue
                recipe_items_basic[name] = int(amount)

        
        recipe_items = {}

        for key in recipe_items_basic.keys():
            recipe_items[Item(key)] = recipe_items_basic[key]

        return Item(item_name, Recipe(recipe_items))

    return Item(item_name)

def find_item_recipe_tree(item_name):
    recipe_data = None

    try:
        recipe_data = json.loads(requests.get(URL_TO_FILES + item_name + ".json").text)
    except:
        raise RecipeNotFoundException()
    
    if "recipe" in recipe_data:
        recipe_items_basic = {}
        for key in recipe_data["recipe"].keys():
            if recipe_data["recipe"][key] != "":
                name, amount = recipe_data["recipe"][key].split(":")
                if name in recipe_items_basic:
                    recipe_items_basic[name] += int(amount)
                    continue
                recipe_items_basic[name] = int(amount)

        # Stop infinate loops with items and their block forms
        if len(recipe_items_basic.keys()) == 1 and recipe_items_basic[recipe_items_basic.keys()[0]] == 1:
            return Item(item_name)
        
        recipe_items = {}

        for key in recipe_items_basic.keys():
            recipe_items[find_item_recipe_tree(key)] = recipe_items_basic[key]

        return Item(item_name, Recipe(recipe_items))

    return Item(item_name)
