from enum import Enum


class PriceUnit(Enum):
    per_property = "per property"
    per_month = "per month"
    per_night = "per night"
    per_m = "per m2"
    per_m_per_month = "per m2 per month"
    per_m_per_day = "per m2 per day"
