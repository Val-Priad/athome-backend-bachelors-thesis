from typing import Any

from flask import Response, jsonify, make_response
from pydantic import BaseModel

from exceptions.custom_exceptions.validation_exceptions import (
    ValidationError as DomainValidationError,
)
from exceptions.error_catalog import (
    _is_external_exception,
    get_description,
    get_description_for_exception,
    get_description_for_external_exception,
)


def construct_response(
    data: None | BaseModel = None, message: str = "OK", status: int = 200
) -> Response:
    payload: dict[str, Any] = {"message": message}
    if isinstance(data, BaseModel):
        payload["data"] = data.model_dump(mode="json")

    return make_response(jsonify(payload), status)


def construct_error(
    e: Exception | None = None, code: str | None = None
) -> Response:
    if code is not None:
        description = get_description(code)
    elif e and _is_external_exception(e):
        description = get_description_for_external_exception(e)
    elif e:
        description = get_description_for_exception(e)
    else:
        raise ValueError("Exception or code must be provided")

    payload: dict[str, Any] = {
        "error": {
            "code": description.code,
            "message": description.message,
        }
    }

    if isinstance(e, DomainValidationError) and e.errors:
        payload["error"]["errors"] = e.errors

    return make_response(jsonify(payload), description.status)
