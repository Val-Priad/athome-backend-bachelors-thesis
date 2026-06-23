from uuid import uuid4

import pytest
from sqlalchemy import select
from sqlalchemy.orm import Session

from domain.estate.enums.estate_enums import EstateType, OfferType
from domain.estate.estate_model import Estate
from domain.estate.models.saved_estate_model import SavedEstate
from domain.user.user_model import UserRole
from tests.integration.conftest import ESTATE_PATH


def create_test_estate(db_session: Session) -> Estate:
    estate = Estate(
        estate_type=EstateType.apartment,
        offer_type=OfferType.sale,
    )
    db_session.add(estate)
    db_session.flush()
    return estate


@pytest.mark.parametrize("logged_in_user", [UserRole.user], indirect=True)
def test_toggle_save_estate_add_success(client, logged_in_user, db_session):
    estate = create_test_estate(db_session)
    response = client.post(
        f"{ESTATE_PATH}/saved/{estate.id}",
        headers=logged_in_user.headers,
    )
    assert response.status_code == 200

    saved_record = db_session.scalar(
        select(SavedEstate).where(
            SavedEstate.user_id == logged_in_user.id,
            SavedEstate.estate_id == estate.id,
        )
    )
    assert saved_record is not None


@pytest.mark.parametrize("logged_in_user", [UserRole.user], indirect=True)
def test_toggle_save_estate_remove_success(client, logged_in_user, db_session):
    estate = create_test_estate(db_session)
    saved_estate = SavedEstate(user_id=logged_in_user.id, estate_id=estate.id)
    db_session.add(saved_estate)
    db_session.flush()

    response = client.post(
        f"{ESTATE_PATH}/saved/{estate.id}",
        headers=logged_in_user.headers,
    )
    assert response.status_code == 200

    saved_record = db_session.scalar(
        select(SavedEstate).where(
            SavedEstate.user_id == logged_in_user.id,
            SavedEstate.estate_id == estate.id,
        )
    )
    assert saved_record is None


@pytest.mark.parametrize("logged_in_user", [UserRole.user], indirect=True)
def test_toggle_save_estate_not_found(client, logged_in_user):
    non_existent_id = uuid4()
    response = client.post(
        f"{ESTATE_PATH}/saved/{non_existent_id}",
        headers=logged_in_user.headers,
    )
    assert response.status_code == 404


def test_toggle_save_estate_unauthorized(client):
    estate_id = uuid4()
    response = client.post(f"{ESTATE_PATH}/saved/{estate_id}")
    assert response.status_code == 401
