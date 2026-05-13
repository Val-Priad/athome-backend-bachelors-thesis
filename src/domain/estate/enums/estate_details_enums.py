from enum import Enum


class PropertyCondition(Enum):
    very_good = "very_good"
    good = "good"
    poor = "poor"
    new = "new"


class EnergyClass(Enum):
    a = "a"
    b = "b"
    c = "c"
    d = "d"
    e = "e"
    f = "f"
    g = "g"


class Furnishing(Enum):
    furnished = "furnished"
    unfurnished = "unfurnished"
    partially = "partially"
