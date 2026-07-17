from datetime import date
from decimal import Decimal
from typing import Annotated, TypeAlias
from uuid import UUID

from pydantic import AfterValidator, BeforeValidator, EmailStr, Field
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


def _validate_acceptance_year(value: int) -> int:
    if not 1800 <= value <= date.today().year + 10:
        raise ValueError(
            "acceptance_year must be between 1800 and current year + 10"
        )

    return value


ID = Annotated[UUID, Field()]
AcceptanceYear: TypeAlias = Annotated[
    int,
    AfterValidator(_validate_acceptance_year),
]
UserName = Annotated[
    str,
    Field(min_length=1, max_length=255),
    BeforeValidator(strip_string),
]
E164PhoneNumberType = Annotated[
    PydanticPhoneNumber, PhoneNumberValidator(number_format="E164")
]
ImageKey = Annotated[str, Field(min_length=1, max_length=1024)]
UserDescription = Annotated[str, Field(min_length=1, max_length=510)]
UserEmail: TypeAlias = Annotated[EmailStr, Field(min_length=1, max_length=255)]
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
