from datetime import datetime

from pydantic import ConfigDict, Field

from domain.user.user_model import UserRole
from schemas.parent_types import ResponseValidation
from schemas.types import (
    ID,
    E164PhoneNumberType,
    ImageKey,
    UserDescription,
    UserEmail,
    UserName,
)


class UserResponse(ResponseValidation):
    id: ID
    email: UserEmail
    role: UserRole

    name: UserName | None
    phone_number: E164PhoneNumberType | None
    avatar_key: ImageKey | None
    avatar_url: str | None = None
    description: UserDescription | None

    model_config = ConfigDict(from_attributes=True)


class UsersListItem(ResponseValidation):
    id: ID
    email: UserEmail
    role: UserRole
    name: UserName | None
    phone_number: E164PhoneNumberType | None
    avatar_key: ImageKey | None
    avatar_url: str | None = None
    is_email_verified: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UsersListResponse(ResponseValidation):
    items: list[UsersListItem]
    total: int = Field(ge=0)
    page: int = Field(ge=1)
    page_size: int = Field(ge=1, le=100)
