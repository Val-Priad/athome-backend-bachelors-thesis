from enum import Enum


class EstateType(Enum):
    apartment = "apartment"
    house = "house"


class OfferType(Enum):
    sale = "sale"
    lease = "lease"
