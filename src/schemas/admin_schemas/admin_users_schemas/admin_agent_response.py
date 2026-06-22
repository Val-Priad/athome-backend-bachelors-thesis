from datetime import datetime

from pydantic import ConfigDict, Field

from schemas.parent_types import ResponseValidation
from schemas.types import ID, E164PhoneNumberType, UserEmail, UserName


class AgentsListItem(ResponseValidation):
    id: ID
    email: UserEmail
    name: UserName | None
    phone_number: E164PhoneNumberType | None
    avatar_key: str | None
    estate_qty: int = 0
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AgentListResponse(ResponseValidation):
    items: list[AgentsListItem]
    total: int = Field(ge=0)
    page: int = Field(ge=1)
    page_size: int = Field(ge=1, le=100)
