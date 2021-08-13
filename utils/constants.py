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


# noinspection SpellCheckingInspection
class Skyblock(Constant):
    TIERS = ("common", "uncommon", "rare", "epic", "legendary", "mythic", "supreme", "special", "very_special")
