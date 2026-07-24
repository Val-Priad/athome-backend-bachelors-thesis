from flask import Flask

from composition.application_container import ApplicationContainer
from composition.dependency_overrides import DependencyOverrides
from composition.infrastructure.build_infrastructure_container import (
    build_infrastructure_container,
)
from composition.mappers.build_estate_response_mapper import (
    build_estate_response_mapper,
)
from composition.modules.admin.build_admin_container import (
    build_admin_container,
)
from composition.modules.agents.build_agents_container import (
    build_agents_container,
)
from composition.modules.auth.build_auth_container import build_auth_container
from composition.modules.estates.build_estates_container import (
    build_estates_container,
)
from composition.modules.media.build_media_container import (
    build_media_container,
)
from composition.modules.users.build_users_container import (
    build_users_container,
)
from composition.repositories.build_repository_container import (
    build_repository_container,
)
from composition.services.build_service_container import (
    build_service_container,
)


def build_application_container(
    app: Flask,
    *,
    overrides: DependencyOverrides | None = None,
) -> ApplicationContainer:
    infrastructure = build_infrastructure_container(
        app=app,
        overrides=overrides,
    )
    repositories = build_repository_container()
    services = build_service_container(
        infrastructure=infrastructure,
        repositories=repositories,
    )
    estate_response_mapper = build_estate_response_mapper(infrastructure)

    return ApplicationContainer(
        auth=build_auth_container(
            infrastructure=infrastructure,
            repositories=repositories,
            services=services,
        ),
        users=build_users_container(
            infrastructure=infrastructure,
            repositories=repositories,
            services=services,
        ),
        admin=build_admin_container(
            infrastructure=infrastructure,
            repositories=repositories,
            services=services,
            estate_response_mapper=estate_response_mapper,
        ),
        agents=build_agents_container(
            infrastructure=infrastructure,
            services=services,
            estate_response_mapper=estate_response_mapper,
        ),
        estates=build_estates_container(
            infrastructure=infrastructure,
            repositories=repositories,
            services=services,
            estate_response_mapper=estate_response_mapper,
        ),
        media=build_media_container(
            infrastructure=infrastructure,
            services=services,
            presigned_url_ttl_seconds=app.config[
                "S3_PRESIGNED_URL_TTL_SECONDS"
            ],
        ),
    )
