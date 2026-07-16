from flask import Flask

from application.transactions import TransactionManager
from composition.dependency_overrides import DependencyOverrides
from composition.infrastructure.infrastructure_container import (
    ApplicationUrls,
    InfrastructureContainer,
)
from infrastructure.db import db
from infrastructure.email.Mailer import Mailer
from infrastructure.object_storage.noop_object_storage import (
    NoOpObjectStorage,
)
from infrastructure.vicinity.retry_vicinity_client import (
    RetryingVicinityClient,
)
from infrastructure.vicinity.vicinity_client import (
    OpenStreetMapVicinityClient,
)
from security.password_crypto import PasswordCrypto
from security.token_crypto import TokenCrypto


def build_infrastructure_container(
    app: Flask,
    overrides: DependencyOverrides | None = None,
) -> InfrastructureContainer:
    session_factory = (
        overrides.session_factory
        if overrides and overrides.session_factory is not None
        else db.get_session_factory(app)
    )
    mailer = (
        overrides.mailer
        if overrides and overrides.mailer is not None
        else Mailer(
            api_key=app.config["RESEND_API_KEY"],
            app_base_url=app.config["APP_BASE_URL"],
        )
    )
    object_storage = (
        overrides.object_storage
        if overrides and overrides.object_storage is not None
        else NoOpObjectStorage()
    )
    vicinity_client = (
        overrides.vicinity_client
        if overrides and overrides.vicinity_client is not None
        else RetryingVicinityClient(OpenStreetMapVicinityClient())
    )

    return InfrastructureContainer(
        transactions=TransactionManager(session_factory),
        mailer=mailer,
        object_storage=object_storage,
        vicinity_client=vicinity_client,
        password_hasher=PasswordCrypto(),
        token_hasher=TokenCrypto(),
        urls=ApplicationUrls(
            app_base_url=app.config["APP_BASE_URL"],
            media_base_url=app.config["MEDIA_BASE_URL"],
        ),
    )
