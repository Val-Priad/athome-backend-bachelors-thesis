from enum import Enum


class EstateType(str, Enum):
    apartment = "apartment"
    house = "house"


class OfferType(str, Enum):
    sale = "sale"
    lease = "lease"
