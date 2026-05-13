from enum import Enum


class HouseType(Enum):
    detached = "detached"
    semi_detached = "semi-detached"
    terraced = "terraced"


class RoomCount(Enum):
    one = "1"
    two = "2"
    three = "3"
    four = "4"
    five = "5+"
    atypical = "atypical"
