from pydantic import Field

from schemas.parent_types import RequestValidation


class EstateTranslationSection(RequestValidation):
    lang_code: str = Field(min_length=2, max_length=10)
    title: str = Field(min_length=1, max_length=255)
    description: str = Field(min_length=1)
