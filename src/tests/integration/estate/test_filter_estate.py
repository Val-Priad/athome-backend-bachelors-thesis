import uuid
from datetime import date, datetime, timedelta, timezone

import pytest

from domain.estate.enums.apartment_enums import ApartmentLayout
from domain.estate.enums.estate_details_enums import (
    EnergyClass,
    Furnishing,
    PropertyCondition,
)
from domain.estate.enums.estate_enums import EstateType, OfferType
from domain.estate.enums.estate_listing_enums import ListingStatus
from domain.estate.enums.estate_location_enums import Region
from domain.estate.enums.estate_media_enums import MediaType
from domain.estate.enums.estate_pricing_enums import PriceUnit
from domain.estate.enums.estate_vicinity_enums import VicinityType
from domain.estate.estate_model import Estate
from domain.estate.models.estate_apartment_model import EstateApartment
from domain.estate.models.estate_details_model import EstateDetails
from domain.estate.models.estate_listing_model import EstateListing
from domain.estate.models.estate_location_model import EstateLocation
from domain.estate.models.estate_media_model import EstateMedia
from domain.estate.models.estate_pricing_model import EstatePricing
from domain.estate.models.estate_translation_model import EstateTranslation
from domain.estate.models.estate_utilities_model import EstateUtilities
from domain.estate.models.estate_vicinity_model import EstateVicinity
from domain.estate.models.saved_estate_model import SavedEstate
from domain.user.user_model import UserRole
from tests.integration.conftest import API_PREFIX, ESTATE_PATH

FILTER_ESTATE_PATH = f"{API_PREFIX}{ESTATE_PATH}"


def create_filter_estate(
    db_session,
    *,
    title: str = "Test apartment",
    status: ListingStatus = ListingStatus.active,
    estate_type: EstateType = EstateType.apartment,
    offer_type: OfferType = OfferType.sale,
    price: str = "100000.00",
    price_unit: PriceUnit = PriceUnit.per_property,
    usable_area: float = 50.0,
    total_property_area: float | None = 60.0,
    region: Region = Region.kyiv_city,
    city: str = "Kyiv",
    floor_number: int | None = 3,
    balcony_area: float | None = None,
    loggia_area: float | None = None,
    terrace_area: float | None = None,
    published_at: date | None = None,
    seller_id=None,
    agent_id=None,
    vicinities: list[tuple[VicinityType, int]] | None = None,
) -> uuid.UUID:
    if published_at is None and status == ListingStatus.active:
        published_at = date.today()

    estate = Estate(
        seller_id=seller_id,
        agent_id=agent_id,
        estate_type=estate_type,
        offer_type=offer_type,
        listing=EstateListing(
            status=status,
            published_at=published_at,
            expires_at=(
                datetime.now(timezone.utc) + timedelta(days=30)
                if status == ListingStatus.active
                else None
            ),
            available_from=date.today() + timedelta(days=1),
        ),
        location=EstateLocation(
            region=region,
            city=city,
            street="Step",
            house_number="12A",
            latitude=50.4501,
            longitude=30.5234,
        ),
        pricing=EstatePricing(
            price=price,
            price_unit=price_unit,
            cost_of_living="100.00",
            commission="500.00",
            commission_paid_by_owner=True,
            refundable_deposit="1000.00",
        ),
        details=EstateDetails(
            condition=PropertyCondition.good,
            energy_class=EnergyClass.c,
            usable_area=usable_area,
            total_property_area=total_property_area,
            furnishing=Furnishing.furnished,
            easy_access=True,
        ),
        utilities=EstateUtilities(
            has_cold_water=True,
            has_hot_water=True,
            has_gas=False,
            has_sewerage=True,
        ),
        apartment=EstateApartment(
            apartment_layout=ApartmentLayout.two_plus_one,
            floor_number=floor_number,
            has_elevator=True,
            balcony_area=balcony_area,
            loggia_area=loggia_area,
            terrace_area=terrace_area,
        ),
        translations=[
            EstateTranslation(
                lang_code="en",
                title=title,
                description=f"{title} description",
            )
        ],
        media=[
            EstateMedia(
                url=f"https://example.com/{title.lower().replace(' ', '-')}.jpg",
                media_type=MediaType.image,
                alt=title,
                is_main=True,
            )
        ],
        vicinities=[
            EstateVicinity(
                type=vicinity_type,
                name=f"{vicinity_type.value} place",
                latitude=50.451,
                longitude=30.524,
                distance_m=distance_m,
            )
            for vicinity_type, distance_m in (vicinities or [])
        ],
    )

    db_session.add(estate)
    db_session.flush()

    return estate.id


def _get_ids(response) -> list[str]:
    body = response.get_json()
    return [item["id"] for item in body["data"]["items"]]


def assert_ok_filter_response(response, *, total: int):
    assert response.status_code == 200

    body = response.get_json()
    assert body["message"] == "OK"
    assert body["data"]["total"] == total
    assert "items" in body["data"]

    return body["data"]


def test_filter_estates_returns_only_active_estates(client, db_session):
    active_id = create_filter_estate(
        db_session,
        title="Active apartment",
        status=ListingStatus.active,
    )
    create_filter_estate(
        db_session,
        title="Draft apartment",
        status=ListingStatus.draft,
    )

    response = client.get(FILTER_ESTATE_PATH)

    data = assert_ok_filter_response(response, total=1)

    assert len(data["items"]) == 1
    assert data["items"][0]["id"] == str(active_id)
    assert data["items"][0]["estate_type"] == EstateType.apartment.value
    assert data["items"][0]["apartment_layout"] == (
        ApartmentLayout.two_plus_one.value
    )
    assert data["items"][0]["room_count"] is None
    assert data["items"][0]["house_type"] is None
    assert data["items"][0]["usable_area"] == pytest.approx(50.0)
    assert data["items"][0]["price"] == "100000.00"
    assert data["items"][0]["price_unit"] == PriceUnit.per_property.value
    assert data["items"][0]["main_media"]["is_main"] is True


def test_filter_estates_by_price_range(client, db_session):
    cheap_id = create_filter_estate(
        db_session,
        title="Cheap apartment",
        price="100000.00",
    )
    middle_id = create_filter_estate(
        db_session,
        title="Middle apartment",
        price="150000.00",
    )
    create_filter_estate(
        db_session,
        title="Expensive apartment",
        price="250000.00",
    )

    response = client.get(
        FILTER_ESTATE_PATH,
        query_string={
            "price_from": "90000.00",
            "price_to": "160000.00",
            "sort_by": "price",
            "order": "asc",
        },
    )

    data = assert_ok_filter_response(response, total=2)

    assert [item["id"] for item in data["items"]] == [
        str(cheap_id),
        str(middle_id),
    ]


def test_filter_estates_by_usable_area_range(client, db_session):
    create_filter_estate(
        db_session,
        title="Small apartment",
        usable_area=35.0,
    )
    matching_id = create_filter_estate(
        db_session,
        title="Matching apartment",
        usable_area=55.0,
    )
    create_filter_estate(
        db_session,
        title="Large apartment",
        usable_area=90.0,
    )

    response = client.get(
        FILTER_ESTATE_PATH,
        query_string={
            "usable_area_from": "50",
            "usable_area_to": "60",
        },
    )

    data = assert_ok_filter_response(response, total=1)

    assert data["items"][0]["id"] == str(matching_id)
    assert data["items"][0]["usable_area"] == pytest.approx(55.0)


def test_filter_estates_by_enum_list_uses_or_semantics(client, db_session):
    first_id = create_filter_estate(
        db_session,
        title="First sale apartment",
        offer_type=OfferType.sale,
        price="100000.00",
    )
    second_id = create_filter_estate(
        db_session,
        title="Second sale apartment",
        offer_type=OfferType.sale,
        price="200000.00",
    )

    response = client.get(
        FILTER_ESTATE_PATH,
        query_string=[
            ("offer_type", OfferType.sale.value),
            ("sort_by", "price"),
            ("order", "asc"),
        ],
    )

    data = assert_ok_filter_response(response, total=2)

    assert [item["id"] for item in data["items"]] == [
        str(first_id),
        str(second_id),
    ]


def test_filter_estates_by_presence_true(client, db_session):
    with_balcony_id = create_filter_estate(
        db_session,
        title="Apartment with balcony",
        balcony_area=5.5,
    )
    create_filter_estate(
        db_session,
        title="Apartment without balcony",
        balcony_area=None,
    )

    response = client.get(
        FILTER_ESTATE_PATH,
        query_string={"has_balcony": "true"},
    )

    data = assert_ok_filter_response(response, total=1)

    assert data["items"][0]["id"] == str(with_balcony_id)


def test_filter_estates_by_presence_false(client, db_session):
    create_filter_estate(
        db_session,
        title="Apartment with balcony",
        balcony_area=5.5,
    )
    without_balcony_id = create_filter_estate(
        db_session,
        title="Apartment without balcony",
        balcony_area=None,
    )

    response = client.get(
        FILTER_ESTATE_PATH,
        query_string={"has_balcony": "false"},
    )

    data = assert_ok_filter_response(response, total=1)

    assert data["items"][0]["id"] == str(without_balcony_id)


def test_filter_estates_by_vicinity_type_uses_and_semantics(
    client,
    db_session,
):
    only_bus_stop_id = create_filter_estate(
        db_session,
        title="Only bus stop",
        vicinities=[(VicinityType.bus_stop, 120)],
    )
    both_vicinities_id = create_filter_estate(
        db_session,
        title="Bus stop and closest",
        vicinities=[
            (VicinityType.bus_stop, 120),
            (VicinityType.closest, 150),
        ],
    )

    response = client.get(
        FILTER_ESTATE_PATH,
        query_string=[
            ("vicinity_type", VicinityType.bus_stop.value),
            ("vicinity_type", VicinityType.closest.value),
        ],
    )

    data = assert_ok_filter_response(response, total=1)

    assert data["items"][0]["id"] == str(both_vicinities_id)
    assert str(only_bus_stop_id) not in _get_ids(response)


def test_filter_estates_by_vicinity_distance_without_type(client, db_session):
    near_id = create_filter_estate(
        db_session,
        title="Near apartment",
        vicinities=[(VicinityType.bus_stop, 120)],
    )
    create_filter_estate(
        db_session,
        title="Far apartment",
        vicinities=[(VicinityType.bus_stop, 500)],
    )

    response = client.get(
        FILTER_ESTATE_PATH,
        query_string={"vicinity_distance_m_to": "200"},
    )

    data = assert_ok_filter_response(response, total=1)

    assert data["items"][0]["id"] == str(near_id)


def test_filter_estates_by_vicinity_type_and_distance(client, db_session):
    matching_id = create_filter_estate(
        db_session,
        title="Matching vicinity apartment",
        vicinities=[(VicinityType.bus_stop, 120)],
    )
    create_filter_estate(
        db_session,
        title="Too far apartment",
        vicinities=[(VicinityType.bus_stop, 500)],
    )
    create_filter_estate(
        db_session,
        title="Wrong vicinity apartment",
        vicinities=[(VicinityType.closest, 120)],
    )

    response = client.get(
        FILTER_ESTATE_PATH,
        query_string={
            "vicinity_type": VicinityType.bus_stop.value,
            "vicinity_distance_m_to": "200",
        },
    )

    data = assert_ok_filter_response(response, total=1)

    assert data["items"][0]["id"] == str(matching_id)


@pytest.mark.parametrize("logged_in_user", [UserRole.user], indirect=True)
def test_filter_estates_saved_by_current_user_true(
    client,
    db_session,
    logged_in_user,
):
    saved_id = create_filter_estate(
        db_session,
        title="Saved apartment",
        price="100000.00",
    )
    create_filter_estate(
        db_session,
        title="Not saved apartment",
        price="200000.00",
    )

    db_session.add(
        SavedEstate(
            user_id=logged_in_user.id,
            estate_id=saved_id,
        )
    )
    db_session.flush()

    response = client.get(
        FILTER_ESTATE_PATH,
        query_string={"saved_by_current_user": "true"},
        headers=logged_in_user.headers,
    )

    data = assert_ok_filter_response(response, total=1)

    assert data["items"][0]["id"] == str(saved_id)


@pytest.mark.parametrize("logged_in_user", [UserRole.user], indirect=True)
def test_filter_estates_saved_by_current_user_false(
    client,
    db_session,
    logged_in_user,
):
    saved_id = create_filter_estate(
        db_session,
        title="Saved apartment",
        price="100000.00",
    )
    not_saved_id = create_filter_estate(
        db_session,
        title="Not saved apartment",
        price="200000.00",
    )

    db_session.add(
        SavedEstate(
            user_id=logged_in_user.id,
            estate_id=saved_id,
        )
    )
    db_session.flush()

    response = client.get(
        FILTER_ESTATE_PATH,
        query_string={
            "saved_by_current_user": "false",
            "sort_by": "price",
            "order": "asc",
        },
        headers=logged_in_user.headers,
    )

    data = assert_ok_filter_response(response, total=1)

    assert data["items"][0]["id"] == str(not_saved_id)


def test_filter_estates_saved_by_current_user_true_without_auth_returns_empty(
    client,
    db_session,
):
    create_filter_estate(
        db_session,
        title="Public apartment",
    )

    response = client.get(
        FILTER_ESTATE_PATH,
        query_string={"saved_by_current_user": "true"},
    )

    data = assert_ok_filter_response(response, total=0)

    assert data["items"] == []


def test_filter_estates_sort_by_price_asc(client, db_session):
    cheap_id = create_filter_estate(
        db_session,
        title="Cheap apartment",
        price="100000.00",
    )
    middle_id = create_filter_estate(
        db_session,
        title="Middle apartment",
        price="150000.00",
    )
    expensive_id = create_filter_estate(
        db_session,
        title="Expensive apartment",
        price="250000.00",
    )

    response = client.get(
        FILTER_ESTATE_PATH,
        query_string={
            "sort_by": "price",
            "order": "asc",
        },
    )

    data = assert_ok_filter_response(response, total=3)

    assert [item["id"] for item in data["items"]] == [
        str(cheap_id),
        str(middle_id),
        str(expensive_id),
    ]


def test_filter_estates_sort_by_price_desc(client, db_session):
    cheap_id = create_filter_estate(
        db_session,
        title="Cheap apartment",
        price="100000.00",
    )
    middle_id = create_filter_estate(
        db_session,
        title="Middle apartment",
        price="150000.00",
    )
    expensive_id = create_filter_estate(
        db_session,
        title="Expensive apartment",
        price="250000.00",
    )

    response = client.get(
        FILTER_ESTATE_PATH,
        query_string={
            "sort_by": "price",
            "order": "desc",
        },
    )

    data = assert_ok_filter_response(response, total=3)

    assert [item["id"] for item in data["items"]] == [
        str(expensive_id),
        str(middle_id),
        str(cheap_id),
    ]


def test_filter_estates_pagination(client, db_session):
    first_id = create_filter_estate(
        db_session,
        title="First apartment",
        price="100000.00",
    )
    second_id = create_filter_estate(
        db_session,
        title="Second apartment",
        price="200000.00",
    )
    third_id = create_filter_estate(
        db_session,
        title="Third apartment",
        price="300000.00",
    )

    response = client.get(
        FILTER_ESTATE_PATH,
        query_string={
            "sort_by": "price",
            "order": "asc",
            "page": "2",
            "page_size": "1",
        },
    )

    data = assert_ok_filter_response(response, total=3)

    assert data["page"] == 2
    assert data["page_size"] == 1
    assert [item["id"] for item in data["items"]] == [str(second_id)]

    assert str(first_id) not in _get_ids(response)
    assert str(third_id) not in _get_ids(response)


@pytest.mark.parametrize(
    ("query_string", "field_name"),
    [
        (
            {
                "price_from": "200000.00",
                "price_to": "100000.00",
            },
            "price_from",
        ),
        (
            {
                "usable_area_from": "80",
                "usable_area_to": "40",
            },
            "usable_area_from",
        ),
        (
            {
                "has_balcony": "false",
                "balcony_area_from": "1",
            },
            "has_balcony",
        ),
        (
            {
                "balcony_area_from": "0",
            },
            "balcony_area_from",
        ),
    ],
)
def test_filter_estates_validation_errors(client, query_string, field_name):
    response = client.get(
        FILTER_ESTATE_PATH,
        query_string=query_string,
    )

    assert response.status_code == 400

    body = response.get_json()
    assert body["error"]["code"] == "request_validation_error"
    assert any(
        error["field"].endswith(field_name)
        for error in body["error"].get("errors", [])
    )
