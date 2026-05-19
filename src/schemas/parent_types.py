from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ValidationError

from exceptions.custom_exceptions.validation_exceptions import (
    RequestValidationError,
    ResponseValidationError,
)
from exceptions.exceptions_utils import wrap_with_custom_error
from infrastructure.db import Base


def _clean_input(value: Any) -> Any:
    """Recursively trim strings and convert all-whitespace strings to None."""
    if isinstance(value, str):
        s = value.strip()
        return None if s == "" else s
    if isinstance(value, dict):
        return {k: _clean_input(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_clean_input(v) for v in value]
    return value


class RequestValidation(BaseModel):
    @classmethod
    @wrap_with_custom_error(
        wrap_with=RequestValidationError, catch=ValidationError
    )
    def from_request(cls, parsed_json):
        cleaned = _clean_input(parsed_json)
        return cls.model_validate(cleaned)

    @classmethod
    @wrap_with_custom_error(
        wrap_with=RequestValidationError, catch=ValidationError
    )
    def from_query(cls, query_args):
        cleaned = _clean_input(query_args.to_dict())
        return cls.model_validate(cleaned)


class ResponseValidation(BaseModel):
    @classmethod
    @wrap_with_custom_error(
        wrap_with=ResponseValidationError, catch=ValidationError
    )
    def from_model(cls, model: Base):
        return cls.model_validate(model)
