import os
from collections.abc import Collection, Iterator
from types import SimpleNamespace

from dotenv import load_dotenv
from flask import Flask
from flask.testing import FlaskClient
from flask_jwt_extended import create_access_token, decode_token
from pytest import FixtureRequest, fixture
from sqlalchemy.orm import Session, sessionmaker

from app import create_app
from application.ports.vicinity_client import (
    Place,
    VicinityFetchResult,
)
from composition.application_container import ApplicationContainer
from composition.build_application_container import build_application_container
from composition.container_access import APPLICATION_CONTAINER_KEY
from composition.dependency_overrides import DependencyOverrides
from config import TestingConfig
from domain.estate.enums.estate_vicinity_enums import VicinityType
from domain.user.services.password_hasher import PasswordHasher
from domain.user.user_model import User, UserRole
from infrastructure.db import db

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
        self.verification_emails: list[tuple[str, str]] = []
        self.reset_emails: list[tuple[str, str]] = []
        self.sent_estate_contact_emails: list[dict[str, str]] = []

    def send_verification_email(self, email_to: str, token: str) -> None:
        self.verification_emails.append((email_to, token))

    def send_reset_password_email(self, email_to: str, token: str) -> None:
        self.reset_emails.append((email_to, token))

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
        db.dispose(app)


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
    return PasswordHasher.hash_password(TEST_PASSWORD)


@fixture
def logged_in_user(
    request: FixtureRequest,
    app: Flask,
    client: FlaskClient,
    db_session: Session,
    test_password_hash: bytes,
):
    user_role = getattr(request, "param", UserRole.user)

    user = User(
        email="logged_in_user@example.com",
        password_hash=test_password_hash,
        is_email_verified=True,
        phone_number="+420701234567",
        name="Val Priad",
        avatar_key="avatars/default/user_1.png",
        description="Test user account for integration tests",
        role=user_role,
    )
    db_session.add(user)
    db_session.flush()

    access_token = create_access_token(identity=str(user.id), fresh=True)
    csrf_token = decode_token(access_token)["csrf"]

    client.set_cookie(
        key=app.config["JWT_ACCESS_COOKIE_NAME"],
        value=access_token,
        path=app.config["JWT_ACCESS_COOKIE_PATH"],
    )
    client.set_cookie(
        key=app.config["JWT_ACCESS_CSRF_COOKIE_NAME"],
        value=csrf_token,
        path=app.config["JWT_ACCESS_CSRF_COOKIE_PATH"],
    )

    return SimpleNamespace(
        id=user.id,
        role=user.role,
        email=user.email,
        password=TEST_PASSWORD,
        headers={app.config["JWT_ACCESS_CSRF_HEADER_NAME"]: csrf_token},
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
