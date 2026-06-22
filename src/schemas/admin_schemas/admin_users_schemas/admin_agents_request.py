from typing import Literal

from pydantic import Field

from schemas.parent_types import RequestValidation


class AgentListRequest(RequestValidation):
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=50)

    email: str | None = None
    name: str | None = None
    phone_number: str | None = None

    sort_by: Literal[
        "email", "name", "phone_number", "created_at", "estate_qty"
    ] = "created_at"
    sort_order: Literal["asc", "desc"] = "desc"
