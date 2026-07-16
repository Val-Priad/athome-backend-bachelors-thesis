import os
from collections.abc import Collection, Iterator
from types import SimpleNamespace

from dotenv import load_dotenv
from flask import Flask
from flask.testing import FlaskClient
from pytest import FixtureRequest, fixture
from sqlalchemy import select
from sqlalchemy.orm import Session, sessionmaker

from app import create_app
from composition.application_container import ApplicationContainer
from composition.build_application_container import build_application_container
from composition.container_access import APPLICATION_CONTAINER_KEY
from composition.dependency_overrides import DependencyOverrides
from config import TestingConfig
from domain.estate.enums.estate_vicinity_enums import VicinityType
from domain.user.user_model import User, UserRole
from infrastructure.db import db
from infrastructure.vicinity.vicinity_protocol import (
    Place,
    VicinityFetchResult,
)
from security.password_crypto import PasswordCrypto

ME_PATH = "/api/users/me"
AGENTS_PATH = "/api/agents"
ESTATE_PATH = "/api/estate"
AUTH_PATH = "/api/auth"
ADMIN_USERS_PATH = "/api/admin/users"
ADMIN_AGENTS_PATH = "/api/admin/agents"
ADMIN_ESTATE_PATH = "/api/admin/estate"
TEST_PASSWORD = "any_password"


class FakeMailer:
    def __init__(self) -> None:
        self.sent_estate_contact_emails: list[dict[str, str]] = []

    def send_verification_email(self, email_to: str, token: str) -> None:
        pass

    def send_reset_password_email(self, email_to: str, token: str) -> None:
        pass

    def send_estate_contact_email(
        self,
        agent_email: str,
        estate_title: str,
        estate_url: str,
        estate_address: str,
        sender_name: str,
        sender_email: str,
        sender_phone: str,
        message: str,
    ) -> None:
        self.sent_estate_contact_emails.append(
            {
                "agent_email": agent_email,
                "estate_title": estate_title,
                "estate_url": estate_url,
                "estate_address": estate_address,
                "sender_name": sender_name,
                "sender_email": sender_email,
                "sender_phone": sender_phone,
                "message": message,
            }
        )


class FakeObjectStorage:
    def delete_objects(self, object_keys: Collection[str]) -> None:
        pass


class FakeVicinityClient:
    def fetch_vicinity(self, lat, lon, radius=10000):
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


@fixture
def fake_mailer() -> FakeMailer:
    return FakeMailer()


@fixture
def fake_vicinity_client() -> FakeVicinityClient:
    return FakeVicinityClient()


@fixture
def fake_object_storage() -> FakeObjectStorage:
    return FakeObjectStorage()


@fixture
def app(
    fake_mailer: FakeMailer,
    fake_vicinity_client: FakeVicinityClient,
    fake_object_storage: FakeObjectStorage,
) -> Iterator[Flask]:
    load_dotenv()
    test_database_url = os.environ["TEST_DATABASE_URL"]

    app = create_app(
        TestingConfig,
        config_overrides={
            "DATABASE_URL": test_database_url,
            "JWT_SECRET_KEY": "test-secret-key-at-least-32-bytes-long",
            "APP_BASE_URL": "https://athome.test",
            "MEDIA_BASE_URL": "https://media.test",
        },
        dependency_overrides=DependencyOverrides(
            mailer=fake_mailer,
            vicinity_client=fake_vicinity_client,
            object_storage=fake_object_storage,
        ),
    )

    try:
        yield app
    finally:
        db.get_engine(app).dispose()


@fixture
def client(app) -> FlaskClient:
    return app.test_client()


@fixture(autouse=True)
def db_session(
    app: Flask,
    fake_mailer: FakeMailer,
    fake_vicinity_client: FakeVicinityClient,
    fake_object_storage: FakeObjectStorage,
) -> Iterator[Session]:
    with app.app_context():
        engine = db.get_engine(app)
        connection = engine.connect()
        transaction = connection.begin()

        testing_session_factory = sessionmaker(
            bind=connection,
            expire_on_commit=False,
            join_transaction_mode="create_savepoint",
        )
        original_container = app.extensions[APPLICATION_CONTAINER_KEY]
        app.extensions[APPLICATION_CONTAINER_KEY] = (
            build_application_container(
                app,
                overrides=DependencyOverrides(
                    session_factory=testing_session_factory,
                    mailer=fake_mailer,
                    vicinity_client=fake_vicinity_client,
                    object_storage=fake_object_storage,
                ),
            )
        )

        session = testing_session_factory()

        try:
            yield session
        finally:
            session.close()
            app.extensions[APPLICATION_CONTAINER_KEY] = original_container
            transaction.rollback()
            connection.close()


@fixture
def application_container(app: Flask) -> ApplicationContainer:
    return app.extensions[APPLICATION_CONTAINER_KEY]


@fixture(scope="session")
def test_password_hash() -> bytes:
    return PasswordCrypto.hash_password(TEST_PASSWORD)


@fixture
def logged_in_user(
    request: FixtureRequest, client: FlaskClient, db_session: Session
):
    user_role = getattr(request, "param", UserRole.user)

    email = "logged_in_user@example.com"
    password = TEST_PASSWORD
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
        role=user.role,
        email=email,
        password=password,
        headers={"X-CSRF-TOKEN": cookie.value},
    )


@fixture
def any_user(
    request: FixtureRequest,
    db_session: Session,
    test_password_hash: bytes,
):
    user_role = getattr(request, "param", UserRole.user)

    user = User(
        email="any_user@example.com",
        password_hash=test_password_hash,
        is_email_verified=True,
        role=user_role,
    )
    db_session.add(user)
    db_session.flush()
    return user
