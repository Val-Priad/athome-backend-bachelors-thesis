from enum import Enum


class ListingStatus(Enum):
    active = "Active"
    expired = "Expired"
    expiring = "Expiring"
    archived = "Archived"
    suggested = "Suggested"
