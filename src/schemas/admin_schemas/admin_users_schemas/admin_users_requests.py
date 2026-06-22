from typing import Literal

from pydantic import Field

from domain.user.user_model import UserRole
from schemas.parent_types import RequestValidation


class RoleRequest(RequestValidation):
    role: UserRole


class UsersListRequest(RequestValidation):
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=50)

    email: str | None = None
    name: str | None = None
    role: UserRole | None = None
    phone_number: str | None = None
    is_email_verified: bool | None = None

    sort_by: Literal[
        "email", "name", "phone_number", "is_email_verified", "created_at"
    ] = "created_at"
    sort_order: Literal["asc", "desc"] = "desc"
