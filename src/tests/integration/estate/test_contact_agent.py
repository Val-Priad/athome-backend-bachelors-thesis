import uuid

import pytest
from sqlalchemy.orm import Session

from domain.estate.enums.estate_enums import EstateType, OfferType
from domain.estate.enums.estate_location_enums import Region
from domain.estate.estate_model import Estate
from domain.estate.models.estate_location_model import EstateLocation
from domain.estate.models.estate_translation_model import EstateTranslation
from domain.user.user_model import UserRole
from tests.integration.conftest import ESTATE_PATH


def create_contact_estate(
    db_session: Session,
    *,
    agent_id=None,
    translations=None,
) -> Estate:
    estate = Estate(
        agent_id=agent_id,
        estate_type=EstateType.apartment,
        offer_type=OfferType.sale,
        location=EstateLocation(
            region=Region.kyiv_city,
            city="Kyiv",
            street="Step",
            house_number="12A",
            latitude=50.4501,
            longitude=30.5234,
        ),
        translations=translations
        or [
            EstateTranslation(
                lang_code="en",
                title="Test apartment",
                description="Test apartment description",
            )
        ],
    )

    db_session.add(estate)
    db_session.flush()

    return estate


def valid_contact_payload():
    return {
        "sender_name": "John Doe",
        "sender_email": "john.doe@example.com",
        "sender_phone": "+420701234567",
        "message": "Hello, I am interested in this estate.",
    }


@pytest.fixture
def sent_estate_contact_emails(fake_mailer):
    return fake_mailer.sent_estate_contact_emails


@pytest.mark.parametrize("logged_in_user", [UserRole.agent], indirect=True)
def test_contact_estate_agent_success(
    client,
    db_session,
    logged_in_user,
    sent_estate_contact_emails,
):
    estate = create_contact_estate(
        db_session,
        agent_id=logged_in_user.id,
    )

    payload = valid_contact_payload()

    response = client.post(
        f"{ESTATE_PATH}/{estate.id}/contact",
        json=payload,
    )

    assert response.status_code == 200

    body = response.get_json()
    assert body["message"] == "OK"

    assert sent_estate_contact_emails == [
        {
            "agent_email": logged_in_user.email,
            "estate_title": "Test apartment",
            "estate_url": f"https://athome.test/estate/{estate.id}",
            "estate_address": "Kyiv, Step, 12A",
            "sender_name": payload["sender_name"],
            "sender_email": payload["sender_email"],
            "sender_phone": payload["sender_phone"],
            "message": payload["message"],
        }
    ]


@pytest.mark.parametrize("logged_in_user", [UserRole.agent], indirect=True)
def test_contact_estate_agent_uses_first_translation_when_english_missing(
    client,
    db_session,
    logged_in_user,
    sent_estate_contact_emails,
):
    estate = create_contact_estate(
        db_session,
        agent_id=logged_in_user.id,
        translations=[
            EstateTranslation(
                lang_code="uk",
                title="Тестова квартира",
                description="Опис тестової квартири",
            )
        ],
    )

    response = client.post(
        f"{ESTATE_PATH}/{estate.id}/contact",
        json=valid_contact_payload(),
    )

    assert response.status_code == 200

    assert sent_estate_contact_emails[0]["estate_title"] == "Тестова квартира"


def test_contact_estate_agent_without_agent_returns_404(
    client,
    db_session,
    sent_estate_contact_emails,
):
    estate = create_contact_estate(
        db_session,
        agent_id=None,
    )

    response = client.post(
        f"{ESTATE_PATH}/{estate.id}/contact",
        json=valid_contact_payload(),
    )

    assert response.status_code == 404

    body = response.get_json()
    assert body["error"]["code"] == "agent_not_found"

    assert sent_estate_contact_emails == []


def test_contact_estate_agent_missing_estate_returns_404(
    client,
    sent_estate_contact_emails,
):
    missing_estate_id = uuid.uuid4()

    response = client.post(
        f"{ESTATE_PATH}/{missing_estate_id}/contact",
        json=valid_contact_payload(),
    )

    assert response.status_code == 404

    body = response.get_json()
    assert body["error"]["code"] == "estate_not_found"

    assert sent_estate_contact_emails == []


@pytest.mark.parametrize("logged_in_user", [UserRole.agent], indirect=True)
def test_contact_estate_agent_validation_error_does_not_send_email(
    client,
    db_session,
    logged_in_user,
    sent_estate_contact_emails,
):
    estate = create_contact_estate(
        db_session,
        agent_id=logged_in_user.id,
    )

    payload = valid_contact_payload()
    payload["message"] = "short"

    response = client.post(
        f"{ESTATE_PATH}/{estate.id}/contact",
        json=payload,
    )

    assert response.status_code == 400

    body = response.get_json()
    assert body["error"]["code"] == "request_validation_error"

    assert any(
        error["field"] == "message"
        for error in body["error"].get("errors", [])
    )

    assert sent_estate_contact_emails == []
