from enum import Enum


class EstateType(Enum):
    apartment = "Apartment"
    house = "House"


class ListingOfferType(Enum):
    sale = "Sale"
    lease = "Lease"
