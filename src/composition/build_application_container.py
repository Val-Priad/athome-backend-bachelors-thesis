from flask import Flask

from composition.application_container import ApplicationContainer
from composition.dependency_overrides import DependencyOverrides
from composition.infrastructure.build_infrastructure_container import (
    build_infrastructure_container,
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
    infrastructure = build_infrastructure_container(app, overrides)
    repositories = build_repository_container()
    services = build_service_container(infrastructure, repositories)

    return ApplicationContainer(
        auth=build_auth_container(infrastructure, repositories, services),
        users=build_users_container(infrastructure, repositories, services),
        admin=build_admin_container(infrastructure, repositories, services),
        agents=build_agents_container(
            infrastructure,
            services,
        ),
        estates=build_estates_container(
            infrastructure,
            repositories,
            services,
        ),
    )
