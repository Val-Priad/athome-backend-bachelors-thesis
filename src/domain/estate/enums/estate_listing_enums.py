from enum import Enum


class ListingStatus(Enum):
    draft = "draft"
    suggested = "suggested"
    rejected = "rejected"
    active = "active"
    expired = "expired"
    archived = "archived"
