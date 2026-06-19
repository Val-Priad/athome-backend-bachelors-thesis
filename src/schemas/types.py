from decimal import Decimal
from typing import Annotated, Union
from uuid import UUID

from pydantic import BeforeValidator, EmailStr, Field
from pydantic_extra_types.phone_numbers import (
    PhoneNumber as PydanticPhoneNumber,
)
from pydantic_extra_types.phone_numbers import (
    PhoneNumberValidator,
)

from .validators.user_validators import (
    reject_string_with_whitespaces,
    strip_string,
)

ID = Annotated[UUID, Field()]
UserName = Annotated[
    str,
    Field(min_length=1, max_length=255),
    BeforeValidator(strip_string),
]
E164PhoneNumberType = Annotated[
    Union[PydanticPhoneNumber], PhoneNumberValidator(number_format="E164")
]
ImageKey = Annotated[str, Field(min_length=1, max_length=1024)]
UserDescription = Annotated[str, Field(min_length=1, max_length=510)]
UserEmail = Annotated[EmailStr, Field(min_length=1, max_length=255)]
Password = Annotated[
    str,
    Field(min_length=8, max_length=255),
    BeforeValidator(reject_string_with_whitespaces),
]

Token = Annotated[str, Field(min_length=40, max_length=50)]

NonNegativeMoneyAmount = Annotated[
    Decimal,
    Field(
        ge=0,
        max_digits=12,
        decimal_places=2,
    ),
]

PositiveMoneyAmount = Annotated[
    Decimal,
    Field(
        gt=0,
        max_digits=12,
        decimal_places=2,
    ),
]

PositiveArea = Annotated[
    float,
    Field(gt=0, le=100_000),
]

NonNegativeArea = Annotated[
    float,
    Field(ge=0, le=100_000),
]

Latitude = Annotated[
    float,
    Field(ge=-90, le=90),
]

Longitude = Annotated[
    float,
    Field(ge=-180, le=180),
]
