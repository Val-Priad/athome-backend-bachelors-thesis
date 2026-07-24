import uuid

import pytest
from conftest import ADMIN_ESTATE_PATH
from flask.testing import FlaskClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from domain.estate.enums.estate_enums import EstateType, OfferType
from domain.estate.estate_model import Estate
from domain.estate.models.estate_media_model import EstateMedia
from domain.media.media_enums import MediaType
from domain.user.user_model import UserRole


def _create_test_estate(db_session: Session) -> Estate:
    estate = Estate(
        estate_type=EstateType.apartment,
        offer_type=OfferType.sale,
    )

    db_session.add(estate)
    db_session.flush()

    return estate


def _assert_ok_response(response):
    assert response.status_code == 200

    data = response.get_json()
    assert data is not None
    assert data["message"] == "OK"


def _assert_estate_exists(db_session: Session, estate_id: uuid.UUID) -> None:
    db_session.expire_all()
    estate = db_session.scalar(select(Estate).where(Estate.id == estate_id))
    assert estate is not None


def _assert_estate_deleted(db_session: Session, estate_id: uuid.UUID) -> None:
    db_session.expire_all()
    estate = db_session.scalar(select(Estate).where(Estate.id == estate_id))
    assert estate is None


def test_admin_delete_estate_unauthorized_without_token(
    client: FlaskClient,
):
    response = client.delete(f"{ADMIN_ESTATE_PATH}/{uuid.uuid4()}")
    assert response.status_code == 401


@pytest.mark.parametrize(
    "logged_in_user",
    [UserRole.user, UserRole.agent],
    indirect=True,
)
def test_admin_delete_estate_forbidden_for_non_admin(
    client: FlaskClient,
    db_session: Session,
    logged_in_user,
):
    estate = _create_test_estate(db_session)

    response = client.delete(
        f"{ADMIN_ESTATE_PATH}/{estate.id}",
        headers=logged_in_user.headers,
    )

    assert response.status_code == 403

    _assert_estate_exists(db_session, estate.id)


@pytest.mark.parametrize("logged_in_user", [UserRole.admin], indirect=True)
def test_admin_delete_estate_success(
    client: FlaskClient,
    db_session: Session,
    logged_in_user,
):
    estate = _create_test_estate(db_session)
    estate_id = estate.id

    response = client.delete(
        f"{ADMIN_ESTATE_PATH}/{estate_id}",
        headers=logged_in_user.headers,
    )

    _assert_ok_response(response)
    _assert_estate_deleted(db_session, estate_id)


@pytest.mark.parametrize("logged_in_user", [UserRole.admin], indirect=True)
def test_admin_delete_estate_deletes_related_media_records(
    client: FlaskClient,
    db_session: Session,
    logged_in_user,
):
    estate = _create_test_estate(db_session)
    object_key = f"estate-media/{logged_in_user.id}/{uuid.uuid4()}.webp"
    media = EstateMedia(
        object_key=object_key,
        media_type=MediaType.image,
        position=0,
    )
    estate.media = [media]
    db_session.flush()
    media_id = media.id
    estate_id = estate.id

    response = client.delete(
        f"{ADMIN_ESTATE_PATH}/{estate_id}",
        headers=logged_in_user.headers,
    )

    _assert_ok_response(response)
    _assert_estate_deleted(db_session, estate_id)
    assert db_session.get(EstateMedia, media_id) is None


@pytest.mark.parametrize("logged_in_user", [UserRole.admin], indirect=True)
def test_admin_delete_unknown_estate_returns_not_found(
    client: FlaskClient,
    logged_in_user,
):
    unknown_estate_id = uuid.uuid4()

    response = client.delete(
        f"{ADMIN_ESTATE_PATH}/{unknown_estate_id}",
        headers=logged_in_user.headers,
    )

    assert response.status_code == 404
