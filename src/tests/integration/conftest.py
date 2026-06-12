from types import SimpleNamespace

from dotenv import load_dotenv
from flask import Flask
from flask.testing import FlaskClient
from pytest import FixtureRequest, fixture
from sqlalchemy import event, select
from sqlalchemy.orm import Session, sessionmaker

from domain.estate.enums.estate_vicinity_enums import VicinityType
from domain.user.user_model import User, UserRole
from infrastructure import db as db_module
from infrastructure.vicinity.vicinity_client import (
    Place,
    VicinityFetchResult,
)
from security.password_crypto import PasswordCrypto

API_PREFIX = "/api"
AUTH_ENDPOINT_PATH = "/auth"
ME_ENDPOINT_PATH = "/users/me"
ADMIN_USERS_PATH = "/admin/users"
AGENT_PATH = "/agents"
ESTATE_PATH = "/estate"


@fixture
def app() -> Flask:
    load_dotenv()

    from app import create_app
    from config import TestingConfig

    return create_app(TestingConfig)


@fixture
def client(app) -> FlaskClient:
    return app.test_client()


@fixture(autouse=True)
def noop_send_verification_email(monkeypatch):
    monkeypatch.setattr(
        "infrastructure.email.Mailer.Mailer.send_verification_email",
        lambda *args, **kwargs: None,
    )


@fixture(autouse=True)
def noop_fetch_vicinity(monkeypatch):
    def fetch_vicinity(lat, lon, radius=10000):
        return VicinityFetchResult(
            ok=True,
            data={
                VicinityType.bus_stop: [
                    Place(
                        type=VicinityType.bus_stop,
                        name="Test bus stop",
                        latitude=lat + 0.001,
                        longitude=lon + 0.001,
                        id=1,
                        distance_m=157,
                    )
                ],
                VicinityType.closest: [
                    Place(
                        type=VicinityType.bus_stop,
                        name="Test bus stop",
                        latitude=lat + 0.001,
                        longitude=lon + 0.001,
                        id=1,
                        distance_m=157,
                    )
                ],
            },
        )

    monkeypatch.setattr(
        "composition_root.estate_service.vicinity_client.fetch_vicinity",
        fetch_vicinity,
    )


@fixture(autouse=True)
def db_session(app: Flask, monkeypatch):
    with app.app_context():
        engine = db_module.get_engine()
        connection = engine.connect()
        transaction = connection.begin()

        testing_session_factory = sessionmaker(bind=connection)
        session = testing_session_factory()
        session.begin_nested()

        monkeypatch.setattr(
            db_module, "_session_factory", testing_session_factory
        )

        @event.listens_for(session, "after_transaction_end")
        def restart_savepoint(session, transaction_):
            if transaction_.nested:
                session.begin_nested()

        yield session

        session.close()
        transaction.rollback()
        connection.close()


@fixture
def logged_in_user(
    request: FixtureRequest, client: FlaskClient, db_session: Session
):
    user_role = getattr(request, "param", UserRole.user)

    email = "logged_in_user@example.com"
    password = "12345678"  # NOSONAR test-only password for integration tests
    payload = {"email": email, "password": password}

    register_response = client.post("/api/auth/register", json=payload)
    assert register_response.status_code == 202

    user = db_session.scalar(select(User).where(User.email == email))
    assert user is not None

    user.is_email_verified = True
    user.phone_number = "+420701234567"
    user.name = "Val Priad"
    user.avatar_key = "avatars/default/user_1.png"
    user.description = "Test user account for integration tests"
    user.role = user_role
    db_session.flush()

    login_response = client.post("/api/auth/login", json=payload)
    assert login_response.status_code == 200

    cookie = client.get_cookie("csrf_access_token")
    assert cookie is not None

    return SimpleNamespace(
        id=user.id,
        email=email,
        password=password,
        headers={"X-CSRF-TOKEN": cookie.value},
    )


@fixture
def any_user(request: FixtureRequest, db_session: Session):
    user_role = getattr(request, "param", UserRole.user)

    user = User(
        email="any_user@example.com",
        password_hash=PasswordCrypto.hash_password("any_password"),
        is_email_verified=True,
        role=user_role,
    )
    db_session.add(user)
    db_session.flush()
    return user
