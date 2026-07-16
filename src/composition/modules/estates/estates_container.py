from dataclasses import dataclass

from application.estate.create_estate_use_case import CreateEstateUseCase
from application.estate.delete_estate_use_case import DeleteEstateUseCase
from application.estate.email_to_estate_agent_use_case import (
    EmailToAgentUseCase,
)
from application.estate.get_estate_use_case import GetEstateUseCase
from application.estate.get_filtered_estate_use_case import (
    GetFilteredEstateUseCase,
)
from application.estate.suggest_estate_use_case import SuggestEstateUseCase
from application.estate.toggle_saved_estate_use_case import (
    ToggleSavedEstateUseCase,
)
from application.estate.update_estate_use_case import UpdateEstateUseCase


@dataclass(frozen=True, slots=True)
class EstatesContainer:
    create: CreateEstateUseCase
    update: UpdateEstateUseCase
    delete: DeleteEstateUseCase
    suggest: SuggestEstateUseCase
    get_one: GetEstateUseCase
    get_filtered: GetFilteredEstateUseCase
    toggle_saved: ToggleSavedEstateUseCase
    email_agent: EmailToAgentUseCase
