class ConstantMeta(type):
    _constants = {}

    def __new__(mcs, *args, **kwargs):
        self = super(ConstantMeta, mcs).__new__(mcs, *args, **kwargs)
        mcs._constants[self] = args[2]
        return self

    def __getitem__(self, item):
        return self._constants[self][item]


class Constant(metaclass=ConstantMeta):
    pass


class Filter(Constant):
    DEFAULT_MIN_PROFIT = 100_000


class API(Constant):
    RATE_LIMITS = [0, 6, 15, 30, 60, 90, 120, 120, 120, 120, 120, ]


class Misc(Constant):
    PET_LEVEL_GROUPS = [
        0,
        50,
        90,
        100,
    ]

# noinspection SpellCheckingInspection
class Skyblock(Constant):
    TIERS = ("common", "uncommon", "rare", "epic", "legendary", "mythic", "supreme", "special", "very_special")

    PET_RARITY_OFFSET = {
        "COMMON": 0,
        "UNCOMMON": 6,
        "RARE": 11,
        "EPIC": 16,
        "LEGENDARY": 20,
        "MYTHIC": 20,
    }

    PET_LEVELS = [100, 110, 120, 130, 145, 160, 175, 190, 210, 230, 250, 275, 300, 330, 360, 400, 440, 490, 540, 600,
                  660, 730, 800, 880, 960, 1050, 1150, 1260, 1380, 1510, 1650, 1800, 1960, 2130, 2310, 2500, 2700, 2920,
                  3160, 3420, 3700, 4000, 4350, 4750, 5200, 5700, 6300, 7000, 7800, 8700, 9700, 10800, 12000, 13300,
                  14700, 16200, 17800, 19500, 21300, 23200, 25200, 27400, 29800, 32400, 35200, 38200, 41400, 44800,
                  48400, 52200, 56200, 60400, 64800, 69400, 74200, 79200, 84700, 90700, 97200, 104200, 111700, 119700,
                  128200, 137200, 146700, 156700, 167700, 179700, 192700, 206700, 221700, 237700, 254700, 272700,
                  291700, 311700, 333700, 357700, 383700, 411700, 441700, 476700, 516700, 561700, 611700, 666700,
                  726700, 791700, 861700, 936700, 1016700, 1101700, 1191700, 1286700, 1386700, 1496700, 1616700,
                  1746700, 1886700, ]
