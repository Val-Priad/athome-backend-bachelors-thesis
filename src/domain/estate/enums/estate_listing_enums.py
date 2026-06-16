from enum import Enum


class ListingStatus(str, Enum):
    draft = "draft"
    suggested = "suggested"
    rejected = "rejected"
    active = "active"
    expired = "expired"
    archived = "archived"
