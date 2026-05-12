from enum import Enum


class PropertyCondition(Enum):
    very_goody = "Very good"
    goody = "Good"
    poor = "Poor"
    new = "New"


class EnergyClass(Enum):
    a = "A"
    b = "B"
    c = "C"
    d = "D"
    e = "E"
    f = "F"
    g = "G"


class Furnishing(Enum):
    furnished = "Furnished"
    unfurnished = "Unfurnished"
    partially = "Partially"
