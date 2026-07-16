from sqlalchemy import select

from domain.user.user_model import User
from tests.integration.conftest import ME_PATH


def test_delete_me_valid(client, logged_in_user, db_session):
    response = client.delete(ME_PATH, headers=logged_in_user.headers)
    assert response.status_code == 200
    assert (
        db_session.scalar(select(User).where(User.id == logged_in_user.id))
        is None
    )


def test_delete_me_requires_csrf_header(client, logged_in_user, db_session):
    response = client.delete(ME_PATH)

    assert response.status_code == 401
    assert (
        db_session.scalar(select(User).where(User.id == logged_in_user.id))
        is not None
    )
