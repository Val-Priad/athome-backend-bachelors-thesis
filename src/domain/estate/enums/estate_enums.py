from enum import Enum


class EstateCategory(Enum):
    apartment = "Apartment"
    house = "House"


class ListingOfferType(Enum):
    sale = "Sale"
    lease = "Lease"
