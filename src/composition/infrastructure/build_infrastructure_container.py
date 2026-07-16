from flask import Flask

from composition.dependency_overrides import DependencyOverrides
from composition.infrastructure.infrastructure_container import (
    InfrastructureContainer,
)
from configuration.application_urls import ApplicationUrls
from infrastructure.db import db
from infrastructure.email.mailer import Mailer
from infrastructure.object_storage.noop_object_storage import (
    NoOpObjectStorage,
)
from infrastructure.sqlalchemy_transaction_manager import (
    SqlAlchemyTransactionManager,
)
from infrastructure.vicinity.retry_vicinity_client import (
    RetryingVicinityClient,
)
from infrastructure.vicinity.vicinity_client import (
    OpenStreetMapVicinityClient,
)


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
        else RetryingVicinityClient(
            client=OpenStreetMapVicinityClient(),
        )
    )

    return InfrastructureContainer(
        transactions=SqlAlchemyTransactionManager(
            session_factory=session_factory
        ),
        mailer=mailer,
        object_storage=object_storage,
        vicinity_client=vicinity_client,
        urls=ApplicationUrls(
            app_base_url=app.config["APP_BASE_URL"],
            media_base_url=app.config["MEDIA_BASE_URL"],
        ),
    )
