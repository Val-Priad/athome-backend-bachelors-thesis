from dataclasses import dataclass

from composition.modules.admin.admin_container import AdminContainer
from composition.modules.agents.agents_container import AgentsContainer
from composition.modules.auth.auth_container import AuthContainer
from composition.modules.estates.estates_container import EstatesContainer
from composition.modules.media.media_container import MediaContainer
from composition.modules.users.users_container import UsersContainer


@dataclass(frozen=True, slots=True)
class ApplicationContainer:
    auth: AuthContainer
    users: UsersContainer
    admin: AdminContainer
    agents: AgentsContainer
    estates: EstatesContainer
    media: MediaContainer
