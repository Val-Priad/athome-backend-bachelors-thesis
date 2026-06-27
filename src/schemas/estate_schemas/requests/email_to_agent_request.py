from pydantic import Field

from schemas.parent_types import RequestValidation
from schemas.types import E164PhoneNumberType, UserEmail


class EmailToAgentRequest(RequestValidation):
    sender_name: str = Field(min_length=1, max_length=255)
    sender_email: UserEmail
    sender_phone: E164PhoneNumberType
    message: str = Field(min_length=10, max_length=510)
