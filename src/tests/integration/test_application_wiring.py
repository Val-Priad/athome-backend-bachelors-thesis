from app import create_app
from composition.application_container import ApplicationContainer
from composition.container_access import APPLICATION_CONTAINER_KEY
from composition.dependency_overrides import DependencyOverrides
from config import TestingConfig
from infrastructure.db import db


def _create_additional_app(
    app, fake_mailer, fake_vicinity_client, fake_object_storage
):
    return create_app(
        TestingConfig,
        config_overrides={
            key: app.config[key]
            for key in (
                "APP_BASE_URL",
                "DATABASE_URL",
                "JWT_SECRET_KEY",
                "MEDIA_BASE_URL",
                "RATELIMIT_STORAGE_URI",
                "RESEND_API_KEY",
            )
        },
        dependency_overrides=DependencyOverrides(
            mailer=fake_mailer,
            vicinity_client=fake_vicinity_client,
            object_storage=fake_object_storage,
        ),
    )


def test_application_container_is_created(app):
    assert isinstance(
        app.extensions[APPLICATION_CONTAINER_KEY],
        ApplicationContainer,
    )


def test_two_apps_have_independent_containers_and_database_states(
    app,
    fake_mailer,
    fake_vicinity_client,
    fake_object_storage,
):
    second_app = _create_additional_app(
        app,
        fake_mailer,
        fake_vicinity_client,
        fake_object_storage,
    )

    try:
        assert (
            app.extensions[APPLICATION_CONTAINER_KEY]
            is not second_app.extensions[APPLICATION_CONTAINER_KEY]
        )
        assert db.get_state(app) is not db.get_state(second_app)
        assert db.get_engine(app) is not db.get_engine(second_app)
    finally:
        db.dispose(second_app)

    assert db.extension_key not in second_app.extensions
