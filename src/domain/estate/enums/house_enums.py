from enum import Enum


class HouseType(str, Enum):
    detached = "detached"
    semi_detached = "semi_detached"
    terraced = "terraced"


class RoomCount(str, Enum):
    one = "one"
    two = "two"
    three = "three"
    four = "four"
    five_plus = "five_plus"
    atypical = "atypical"
