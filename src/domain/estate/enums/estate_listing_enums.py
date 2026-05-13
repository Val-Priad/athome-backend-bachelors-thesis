from enum import Enum


class ListingStatus(Enum):
    archived = "Archived"
    suggested = "Suggested"
    rejected = "Rejected"
    draft = "Draft"
