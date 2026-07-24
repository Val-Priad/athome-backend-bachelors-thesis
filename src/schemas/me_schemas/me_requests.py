from schemas.parent_types import RequestValidation
from schemas.types import (
    E164PhoneNumberType,
    ImageKey,
    Password,
    UserDescription,
    UserName,
)


class PasswordRequest(RequestValidation):
    old_password: Password
    new_password: Password


class UpdateUserPersonalDataRequest(RequestValidation):
    name: UserName | None = None
    phone_number: E164PhoneNumberType | None = None
    avatar_key: ImageKey | None = None
    description: UserDescription | None = None
