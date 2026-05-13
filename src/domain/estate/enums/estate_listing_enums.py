from enum import Enum


class ListingStatus(Enum):
    draft = "Draft"
    suggested = "Suggested"
    rejected = "Rejected"
    active = "Active"
    expired = "Expired"
    archived = "Archived"
