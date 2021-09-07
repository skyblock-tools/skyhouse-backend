from . import constants


def get_level_from_pet_xp(tier: str, exp: int) -> int:
    offset = constants.Skyblock.PET_RARITY_OFFSET[tier]
    levels = constants.Skyblock.PET_LEVELS[offset: offset + 99]
    level = 1
    xp_total = 0
    for i in range(99):
        xp_total += levels[i]
        if xp_total > exp:
            xp_total -= levels[i]
            break
        else:
            level += 1
    return level


def get_level_from_table(table: list[int], exp: int) -> int:
    level = -1
    for x in table:
        if exp >= x:
            level += 1
        else:
            break
    return level
