from enum import Enum


class HouseAttachmentType(Enum):
    detached = "Detached"
    semi_detached = "Semi-detached"
    terraced = "Terraced"


class RoomCount(Enum):
    one = "1"
    two = "2"
    three = "3"
    four = "4"
    five = "5+"
    atypical = "Atypical"
