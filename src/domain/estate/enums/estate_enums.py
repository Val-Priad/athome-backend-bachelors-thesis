from enum import Enum


class EstateType(Enum):
    apartment = "Apartment"
    house = "House"


class OfferType(Enum):
    sale = "Sale"
    lease = "Lease"
