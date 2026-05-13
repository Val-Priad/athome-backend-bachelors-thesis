from enum import Enum


class PriceUnit(Enum):
    per_property = "per_property"
    per_month = "per_month"
    per_night = "per_night"
    per_m = "per_m2"
    per_m_per_month = "per_m2_per_month"
    per_m_per_day = "per_m2_per_day"
