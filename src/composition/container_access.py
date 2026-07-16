from typing import cast

from flask import current_app

from composition.application_container import ApplicationContainer

APPLICATION_CONTAINER_KEY = "application_container"


def get_application_container() -> ApplicationContainer:
    return cast(
        ApplicationContainer,
        current_app.extensions[APPLICATION_CONTAINER_KEY],
    )
