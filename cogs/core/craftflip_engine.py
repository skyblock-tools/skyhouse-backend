import os
import time
import json


from loguru import logger

items_and_crafts = {}

unwrapped_crafts = {}

auction_groups_by_neu_internal_name = {}

craftflips = []

craftflipsLive = []


def load_items():
    logger.info(f"loading items")
    if not os.path.isdir(os.getcwd() + "/items/"):
        logger.exception(
            f"Error loading items | please create 'items/' folder with items from https://github.com/NotEnoughUpdates/NotEnoughUpdates-REPO")
        exit(-1)
    else:
        try:
            for filename in os.listdir(os.getcwd() + "/items/"):
                citem = json.load(open(os.getcwd() + "/items/" + filename))
                items_and_crafts[citem["internalname"]] = citem;
            logger.info(f"successfully loaded items")
        except:
            logger.exception(f"Error loading items")
            exit(-1)

    logger.info(f"generating crafts")
    deep_craft_mappings = {1: get_combs_for_crafts(1), 2: get_combs_for_crafts(2), 3: get_combs_for_crafts(3),
                           4: get_combs_for_crafts(4), 5: get_combs_for_crafts(5), 6: get_combs_for_crafts(6),
                           7: get_combs_for_crafts(7), 8: get_combs_for_crafts(8), 9: get_combs_for_crafts(9)}
    for item in items_and_crafts:
        item = items_and_crafts[item];
        if "recipe" in item:
            recipe = list(item["recipe"].values())
            craftitems_with_recipes = 0
            for craftitem in recipe:
                craftitem = craftitem.split(":")[0]
                if craftitem != '' and craftitem in items_and_crafts:
                    craftitem = items_and_crafts[craftitem]
                    if "recipe" in craftitem:
                        craftitems_with_recipes += 1
            if craftitems_with_recipes == 0:
                unwrapped_crafts[item["internalname"]] = [recipe]
            else:
                deep_craft_mapping = deep_craft_mappings[craftitems_with_recipes]
                for craft_mapping in deep_craft_mapping:
                    craft_mapping = craft_mapping.copy()
                    new_recipe = recipe.copy()
                    for idx, craftitem in enumerate(recipe):
                        craftitem = craftitem.split(":")[0]
                        if craftitem != '' and craftitem in items_and_crafts:
                            craftitem = items_and_crafts[craftitem]
                            if "recipe" in craftitem:
                                if craft_mapping.pop():
                                    new_recipe[idx] = list(craftitem["recipe"].values())

                    if item["internalname"] in unwrapped_crafts:
                        unwrapped_crafts[item["internalname"]].append(new_recipe)
                    else:
                        unwrapped_crafts[item["internalname"]] = [new_recipe]
    logger.info(f"successfully generated "+str(len(unwrapped_crafts))+" crafts")


def find_craftflips(aucs: map):
    global auction_groups_by_neu_internal_name
    global craftflips
    start = time.time()
    auction_stack = list(aucs)
    auction_groups_by_neu_internal_name = get_auction_groups_by_neu_internal_name(auction_stack)
    for key, value in auction_groups_by_neu_internal_name.items():
        if key in unwrapped_crafts:
            for craft in unwrapped_crafts[key]:
                evaluate_craft(craft, value[0]["price"], key)
    end = time.time()
    logger.info(f"found {len(craftflipsLive)} craftflips in {round(end - start)} seconds")
    craftflips = craftflipsLive.copy()
    craftflipsLive.clear()

def evaluate_craft(craft: list, price_to_beat: int, result: str):
    required_materials_for_craft = {}
    for craftitem in craft:
        if type(craftitem) is list:
            for craftitem1 in craftitem:
                if craftitem1 != '':
                    a = craftitem1.split(":")
                    internal_name = a[0]
                    quantity = int(a[1])
                    if internal_name in required_materials_for_craft:
                        required_materials_for_craft[internal_name] = required_materials_for_craft[internal_name] + quantity
                    else:
                        required_materials_for_craft[internal_name] = quantity
        else:
            if craftitem != '':
                a = craftitem.split(":")
                internal_name = a[0]
                quantity = int(a[1])
                if internal_name in required_materials_for_craft:
                    required_materials_for_craft[internal_name] = required_materials_for_craft[internal_name] + quantity
                else:
                    required_materials_for_craft[internal_name] = quantity
    totalcost = 0
    for key, value in required_materials_for_craft.items():
        if key in auction_groups_by_neu_internal_name:
            auction_group = auction_groups_by_neu_internal_name[key]
            if len(auction_group) >= value:
                for idx in range(value):
                    totalcost += auction_group[idx]["price"]
            else:
                totalcost = 2147483647
                break
        else:
            totalcost = 2147483647
            break
    profit = int(price_to_beat*0.98) - totalcost
    if profit > 0:
        craftflip = {"profit": profit,
                     "cost_of_craft": totalcost,
                     "resell_price": price_to_beat,
                     "craft": craft,
                     "item": str(result)}
        craftflipsLive.append(craftflip)


# don't worry! nobody understands this bit of code!
def get_combs_for_crafts(n):
    combs = []
    for i in range(1 << n):
        s = bin(i)[2:]
        s = '0' * (n - len(s)) + s
        combs.append(list(s))
    for v in range(len(combs)):
        for a in range(len(combs[v])):
            if combs[v][a] == '0':
                combs[v][a] = False
            else:
                combs[v][a] = True
    return combs


def get_auction_groups_by_neu_internal_name(auction_stack: list):
    auction_groups_by_neu_internal_name1 = {}
    while len(auction_stack) > 0:
        current_auction = auction_stack.pop()[0]
        if current_auction["bin"]:
            current_auction_in = current_auction["internal_name"]
            if current_auction_in in auction_groups_by_neu_internal_name1:
                auction_groups_by_neu_internal_name1[current_auction_in].append(current_auction)
            else:
                auction_groups_by_neu_internal_name1[current_auction_in] = [current_auction]
    for key, value in auction_groups_by_neu_internal_name1.items():
        auction_groups_by_neu_internal_name1[key] = sorted(value, key=lambda i: i['price'])

    return auction_groups_by_neu_internal_name1
