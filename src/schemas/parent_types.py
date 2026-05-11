from pydantic import BaseModel, ValidationError

from exceptions.custom_exceptions.validation_exceptions import (
    RequestValidationError,
    ResponseValidationError,
)
from exceptions.exceptions_utils import wrap_with_custom_error
from infrastructure.db import Base


class RequestValidation(BaseModel):
    @classmethod
    @wrap_with_custom_error(
        wrap_with=RequestValidationError, catch=ValidationError
    )
    def from_request(cls, parsed_json):
        return cls.model_validate(parsed_json)

    @classmethod
    @wrap_with_custom_error(
        wrap_with=RequestValidationError, catch=ValidationError
    )
    def from_query(cls, query_args):
        return cls.model_validate(query_args.to_dict())


class ResponseValidation(BaseModel):
    @classmethod
    @wrap_with_custom_error(
        wrap_with=ResponseValidationError, catch=ValidationError
    )
    def from_model(cls, model: Base):
        return cls.model_validate(model)
