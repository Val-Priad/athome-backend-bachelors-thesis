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
from domain.estate.enums.utilities_enums import (
    HeatingSource,
    PrimaryInternetConnectionType,
)
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
from domain.user.user_model import UserRole
from infrastructure.db import db_session
from tests.integration.conftest import ESTATE_PATH


def _create_estate(
    *,
    status: ListingStatus,
    seller_id=None,
    agent_id=None,
) -> uuid.UUID:
    estate = Estate(
        seller_id=seller_id,
        agent_id=agent_id,
        estate_type=EstateType.apartment,
        offer_type=OfferType.sale,
        listing=EstateListing(
            status=status,
            published_at=(
                datetime.now(timezone.utc)
                if status == ListingStatus.active
                else None
            ),
            expires_at=(
                datetime.now(timezone.utc) + timedelta(days=30)
                if status == ListingStatus.active
                else None
            ),
            available_from=date.today() + timedelta(days=1),
        ),
        location=EstateLocation(
            region=Region.kyiv_city,
            city="Kyiv",
            street="Step",
            house_number="12A",
            latitude=50.4501,
            longitude=30.5234,
        ),
        pricing=EstatePricing(
            price="123456.78",
            price_unit=PriceUnit.per_property,
            cost_of_living="100.00",
            commission="500.00",
            commission_paid_by_owner=True,
            refundable_deposit="1000.00",
        ),
        details=EstateDetails(
            condition=PropertyCondition.good,
            energy_class=EnergyClass.c,
            usable_area=48.5,
            total_property_area=55.0,
            furnishing=Furnishing.furnished,
            easy_access=True,
        ),
        utilities=EstateUtilities(
            has_cold_water=True,
            has_hot_water=True,
            has_gas=False,
            has_sewerage=True,
            heating_source=HeatingSource.central_heating,
            primary_internet_connection_type=(
                PrimaryInternetConnectionType.fiber
            ),
        ),
        apartment=EstateApartment(
            apartment_layout=ApartmentLayout.two_plus_one,
            floor_number=3,
            has_elevator=True,
            balcony_area=4.5,
            loggia_area=None,
            terrace_area=None,
        ),
        translations=[
            EstateTranslation(
                lang_code="en",
                title="Test apartment",
                description="Test apartment description",
            ),
            EstateTranslation(
                lang_code="uk",
                title="Тестова квартира",
                description="Опис тестової квартири",
            ),
        ],
        media=[
            EstateMedia(
                url="https://example.com/main.jpg",
                media_type=MediaType.image,
                alt="Main image",
                is_main=True,
            ),
            EstateMedia(
                url="https://example.com/second.jpg",
                media_type=MediaType.image,
                alt="Second image",
                is_main=False,
            ),
        ],
        vicinities=[
            EstateVicinity(
                type=VicinityType.bus_stop,
                name="Bus stop",
                latitude=50.451,
                longitude=30.524,
                distance_m=120,
            )
        ],
    )

    with db_session() as session:
        session.add(estate)
        session.flush()
        estate_id = estate.id

    return estate_id


@pytest.mark.parametrize("any_user", [UserRole.user], indirect=True)
@pytest.mark.parametrize(
    "logged_in_user", [UserRole.agent, UserRole.admin], indirect=True
)
def test_get_active_estate_returns_full_public_data(
    client,
    any_user,
    logged_in_user,
):
    estate_id = _create_estate(
        status=ListingStatus.active,
        seller_id=any_user.id,
        agent_id=logged_in_user.id,
    )

    response = client.get(f"{ESTATE_PATH}/{estate_id}")

    assert response.status_code == 200

    body = response.get_json()
    assert body["message"] == "OK"

    data = body["data"]

    assert data["id"] == str(estate_id)
    assert data["seller_id"] == str(any_user.id)
    assert "seller" in data

    assert data["agent_id"] == str(logged_in_user.id)
    assert data["estate_type"] == EstateType.apartment.value
    assert data["offer_type"] == OfferType.sale.value

    assert data["agent"]["id"] == str(logged_in_user.id)
    assert data["agent"]["role"] == logged_in_user.role.value

    assert data["location"] == {
        "region": Region.kyiv_city.value,
        "city": "Kyiv",
        "street": "Step",
        "house_number": "12A",
        "latitude": 50.4501,
        "longitude": 30.5234,
    }

    assert data["pricing"]["price"] == "123456.78"
    assert data["pricing"]["price_unit"] == PriceUnit.per_property.value
    assert data["pricing"]["cost_of_living"] == "100.00"
    assert data["pricing"]["commission"] == "500.00"
    assert data["pricing"]["commission_paid_by_owner"] is True
    assert data["pricing"]["refundable_deposit"] == "1000.00"

    assert data["listing"]["status"] == ListingStatus.active.value
    assert data["listing"]["published_at"] is not None
    assert data["listing"]["expires_at"] is not None
    assert (
        data["listing"]["available_from"]
        == (date.today() + timedelta(days=1)).isoformat()
    )

    assert data["utilities"]["has_cold_water"] is True
    assert data["utilities"]["has_hot_water"] is True
    assert data["utilities"]["has_gas"] is False
    assert data["utilities"]["has_sewerage"] is True
    assert (
        data["utilities"]["heating_source"]
        == HeatingSource.central_heating.value
    )
    assert (
        data["utilities"]["primary_internet_connection_type"]
        == PrimaryInternetConnectionType.fiber.value
    )

    assert data["details"]["condition"] == PropertyCondition.good.value
    assert data["details"]["energy_class"] == EnergyClass.c.value
    assert data["details"]["usable_area"] == pytest.approx(48.5)
    assert data["details"]["total_property_area"] == pytest.approx(55.0)
    assert data["details"]["furnishing"] == Furnishing.furnished.value
    assert data["details"]["easy_access"] is True

    assert data["apartment"]["apartment_layout"] == (
        ApartmentLayout.two_plus_one.value
    )
    assert data["apartment"]["floor_number"] == 3
    assert data["apartment"]["has_elevator"] is True
    assert data["apartment"]["balcony_area"] == pytest.approx(4.5)

    assert data["house"] is None

    assert len(data["translations"]) == 2
    assert {
        translation["lang_code"] for translation in data["translations"]
    } == {"en", "uk"}

    assert len(data["media"]) == 2
    assert data["media"][0]["is_main"] is True
    assert data["media"][0]["url"] == "https://example.com/main.jpg"

    assert len(data["vicinities"]) == 1
    assert data["vicinities"][0]["type"] == VicinityType.bus_stop.value
    assert data["vicinities"][0]["name"] == "Bus stop"
    assert data["vicinities"][0]["distance_m"] == 120


@pytest.mark.parametrize("any_user", [UserRole.user], indirect=True)
@pytest.mark.parametrize("logged_in_user", [UserRole.user], indirect=True)
def test_public_get_active_estate_returns_data_without_seller(
    client,
    any_user,
    logged_in_user,
):
    estate_id = _create_estate(
        status=ListingStatus.active,
        seller_id=any_user.id,
        agent_id=logged_in_user.id,
    )

    response = client.get(f"{ESTATE_PATH}/{estate_id}")

    assert response.status_code == 200

    body = response.get_json()
    assert body["message"] == "OK"

    data = body["data"]

    assert "seller" not in data
    assert "seller_id" not in data


@pytest.mark.parametrize("any_user", [UserRole.user], indirect=True)
@pytest.mark.parametrize(
    "logged_in_user",
    [UserRole.admin, UserRole.agent],
    indirect=True,
)
@pytest.mark.parametrize(
    "status",
    [
        ListingStatus.draft,
        ListingStatus.suggested,
        ListingStatus.rejected,
        ListingStatus.expired,
        ListingStatus.archived,
    ],
)
def test_staff_can_get_not_active_estate(
    client,
    logged_in_user,
    any_user,
    status,
):
    estate_id = _create_estate(
        status=status,
        seller_id=any_user.id,
    )

    response = client.get(
        f"{ESTATE_PATH}/{estate_id}",
        headers=logged_in_user.headers,
    )

    assert response.status_code == 200

    data = response.get_json()["data"]

    assert data["id"] == str(estate_id)
    assert data["listing"]["status"] == status.value
    assert "seller" in data
    assert data["seller"]["id"] == str(any_user.id)


@pytest.mark.parametrize("any_user", [UserRole.user], indirect=True)
@pytest.mark.parametrize(
    "status",
    [
        ListingStatus.draft,
        ListingStatus.suggested,
        ListingStatus.rejected,
        ListingStatus.expired,
        ListingStatus.archived,
    ],
)
def test_public_cannot_get_not_active_estate(
    client,
    any_user,
    status,
):
    estate_id = _create_estate(
        status=status,
        seller_id=any_user.id,
    )

    response = client.get(f"{ESTATE_PATH}/{estate_id}")

    assert response.status_code == 404

    body = response.get_json()
    assert body["error"]["code"] == "estate_not_found"


@pytest.mark.parametrize("any_user", [UserRole.user], indirect=True)
@pytest.mark.parametrize("logged_in_user", [UserRole.user], indirect=True)
@pytest.mark.parametrize(
    "status",
    [
        ListingStatus.draft,
        ListingStatus.suggested,
        ListingStatus.rejected,
        ListingStatus.expired,
        ListingStatus.archived,
    ],
)
def test_regular_user_cannot_get_not_active_estate(
    client,
    logged_in_user,
    any_user,
    status,
):
    estate_id = _create_estate(
        status=status,
        seller_id=any_user.id,
    )

    response = client.get(
        f"{ESTATE_PATH}/{estate_id}",
        headers=logged_in_user.headers,
    )

    assert response.status_code == 404

    body = response.get_json()
    assert body["error"]["code"] == "estate_not_found"


@pytest.mark.parametrize("logged_in_user", [UserRole.admin], indirect=True)
def test_get_missing_estate_returns_404_for_staff(
    client,
    logged_in_user,
):
    missing_estate_id = uuid.uuid4()

    response = client.get(
        f"{ESTATE_PATH}/{missing_estate_id}",
        headers=logged_in_user.headers,
    )

    assert response.status_code == 404

    body = response.get_json()
    assert body["error"]["code"] == "estate_not_found"


def test_get_missing_estate_returns_404_for_public(client):
    missing_estate_id = uuid.uuid4()

    response = client.get(f"{ESTATE_PATH}/{missing_estate_id}")

    assert response.status_code == 404

    body = response.get_json()
    assert body["error"]["code"] == "estate_not_found"
