from domain.estate.estate_model import Estate
from domain.estate.models.estate_apartment_model import EstateApartment
from domain.estate.models.estate_details_model import EstateDetails
from domain.estate.models.estate_house_model import EstateHouse
from domain.estate.models.estate_listing_model import EstateListing
from domain.estate.models.estate_location_model import EstateLocation
from domain.estate.models.estate_pricing_model import EstatePricing
from domain.estate.models.estate_utilities_model import EstateUtilities
from schemas.estate_schemas.requests.estate_filter_request import EstateSortBy

SORT_CONFIG = {
    EstateSortBy.created_at: (Estate.created_at, None),
    EstateSortBy.published_at: (EstateListing.published_at, Estate.listing),
    EstateSortBy.expires_at: (EstateListing.expires_at, Estate.listing),
    EstateSortBy.available_from: (
        EstateListing.available_from,
        Estate.listing,
    ),
    EstateSortBy.price: (EstatePricing.price, Estate.pricing),
    EstateSortBy.usable_area: (EstateDetails.usable_area, Estate.details),
    EstateSortBy.total_property_area: (
        EstateDetails.total_property_area,
        Estate.details,
    ),
    EstateSortBy.floor_number: (
        EstateApartment.floor_number,
        Estate.apartment,
    ),
    EstateSortBy.acceptance_year: (EstateHouse.acceptance_year, Estate.house),
}

DIRECT_FILTERS = (
    ("eq", Estate.agent_id, "agent_id"),
    ("in", Estate.estate_type, "estate_type"),
    ("in", Estate.offer_type, "offer_type"),
    ("range", Estate.created_at, "created_at_from", "created_at_to"),
)

RELATION_FILTERS = (
    ("in", Estate.location, EstateLocation.region, "region"),
    ("range", Estate.pricing, EstatePricing.price, "price_from", "price_to"),
    ("in", Estate.pricing, EstatePricing.price_unit, "price_unit"),
    (
        "range",
        Estate.pricing,
        EstatePricing.cost_of_living,
        "cost_of_living_from",
        "cost_of_living_to",
    ),
    (
        "eq",
        Estate.pricing,
        EstatePricing.commission_paid_by_owner,
        "commission_paid_by_owner",
    ),
    (
        "range",
        Estate.listing,
        EstateListing.published_at,
        "published_at_from",
        "published_at_to",
    ),
    (
        "range",
        Estate.listing,
        EstateListing.expires_at,
        "expires_at_from",
        "expires_at_to",
    ),
    (
        "range",
        Estate.listing,
        EstateListing.available_from,
        "available_from_from",
        "available_from_to",
    ),
    ("eq", Estate.utilities, EstateUtilities.has_cold_water, "has_cold_water"),
    ("eq", Estate.utilities, EstateUtilities.has_hot_water, "has_hot_water"),
    ("eq", Estate.utilities, EstateUtilities.has_gas, "has_gas"),
    ("eq", Estate.utilities, EstateUtilities.has_sewerage, "has_sewerage"),
    ("in", Estate.utilities, EstateUtilities.heating_source, "heating_source"),
    (
        "in",
        Estate.utilities,
        EstateUtilities.primary_internet_connection_type,
        "primary_internet_connection_type",
    ),
    ("in", Estate.details, EstateDetails.condition, "condition"),
    ("in", Estate.details, EstateDetails.energy_class, "energy_class"),
    ("in", Estate.details, EstateDetails.furnishing, "furnishing"),
    ("eq", Estate.details, EstateDetails.easy_access, "easy_access"),
    (
        "range",
        Estate.details,
        EstateDetails.usable_area,
        "usable_area_from",
        "usable_area_to",
    ),
    (
        "range",
        Estate.details,
        EstateDetails.total_property_area,
        "total_property_area_from",
        "total_property_area_to",
    ),
    (
        "in",
        Estate.apartment,
        EstateApartment.apartment_layout,
        "apartment_layout",
    ),
    (
        "range",
        Estate.apartment,
        EstateApartment.floor_number,
        "floor_number_from",
        "floor_number_to",
    ),
    ("eq", Estate.apartment, EstateApartment.has_elevator, "has_elevator"),
    (
        "presence",
        Estate.apartment,
        EstateApartment.balcony_area,
        "has_balcony",
    ),
    (
        "range",
        Estate.apartment,
        EstateApartment.balcony_area,
        "balcony_area_from",
        "balcony_area_to",
    ),
    ("presence", Estate.apartment, EstateApartment.loggia_area, "has_loggia"),
    (
        "range",
        Estate.apartment,
        EstateApartment.loggia_area,
        "loggia_area_from",
        "loggia_area_to",
    ),
    (
        "presence",
        Estate.apartment,
        EstateApartment.terrace_area,
        "has_terrace",
    ),
    (
        "range",
        Estate.apartment,
        EstateApartment.terrace_area,
        "terrace_area_from",
        "terrace_area_to",
    ),
    ("in", Estate.house, EstateHouse.room_count, "room_count"),
    ("in", Estate.house, EstateHouse.house_type, "house_type"),
    (
        "range",
        Estate.house,
        EstateHouse.acceptance_year,
        "acceptance_year_from",
        "acceptance_year_to",
    ),
    ("range", Estate.house, EstateHouse.floors, "floors_from", "floors_to"),
    ("presence", Estate.house, EstateHouse.garden_area, "has_garden"),
    (
        "range",
        Estate.house,
        EstateHouse.garden_area,
        "garden_area_from",
        "garden_area_to",
    ),
    (
        "range",
        Estate.house,
        EstateHouse.building_area,
        "building_area_from",
        "building_area_to",
    ),
    ("presence", Estate.house, EstateHouse.pool_area, "has_pool"),
    (
        "range",
        Estate.house,
        EstateHouse.pool_area,
        "pool_area_from",
        "pool_area_to",
    ),
    ("presence", Estate.house, EstateHouse.cellar_area, "has_cellar"),
    (
        "range",
        Estate.house,
        EstateHouse.cellar_area,
        "cellar_area_from",
        "cellar_area_to",
    ),
    ("presence", Estate.house, EstateHouse.garage_area, "has_garage"),
    (
        "range",
        Estate.house,
        EstateHouse.garage_area,
        "garage_area_from",
        "garage_area_to",
    ),
)
