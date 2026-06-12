from enum import Enum


class ListingStatus(str, Enum):
    suggested = "suggested"
    rejected = "rejected"
    active = "active"
    expired = "expired"
    archived = "archived"
