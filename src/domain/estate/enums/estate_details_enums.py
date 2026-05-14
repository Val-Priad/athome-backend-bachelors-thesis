from enum import Enum


class PropertyCondition(str, Enum):
    very_good = "very_good"
    good = "good"
    poor = "poor"
    new = "new"


class EnergyClass(str, Enum):
    a = "a"
    b = "b"
    c = "c"
    d = "d"
    e = "e"
    f = "f"
    g = "g"


class Furnishing(str, Enum):
    furnished = "furnished"
    unfurnished = "unfurnished"
    partially = "partially"
