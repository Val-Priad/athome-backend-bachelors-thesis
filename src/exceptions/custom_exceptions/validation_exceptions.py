from typing import Any

from pydantic import ValidationError as PydanticValidationError

from ..error_catalog import DomainError, register_custom_error


class ValidationError(DomainError):
    def __init__(
        self,
        message: str | None = None,
        errors: list[dict[str, Any]] | None = None,
    ):
        super().__init__(message)
        self.errors = errors or []

    @classmethod
    def from_exception(cls, exc: Exception):
        if isinstance(exc, PydanticValidationError):
            return cls(errors=cls._normalize_pydantic_errors(exc))

        message = str(exc) if str(exc) else None
        return cls(message=message)

    @staticmethod
    def _normalize_error_params(ctx: Any) -> dict[str, Any]:
        if not isinstance(ctx, dict):
            return {}

        result: dict[str, Any] = {}

        for key, value in ctx.items():
            if key == "error":
                continue

            if isinstance(value, (str, int, float, bool)) or value is None:
                result[key] = value
            else:
                result[key] = str(value)

        return result

    @classmethod
    def _normalize_pydantic_errors(
        cls,
        exc: PydanticValidationError,
    ) -> list[dict[str, Any]]:
        normalized: list[dict[str, Any]] = []

        for err in exc.errors():
            loc = err.get("loc", ())

            if isinstance(loc, (list, tuple)):
                filtered = [
                    str(p)
                    for p in loc
                    if p not in ("body", "model", "__root__")
                ]
                field = ".".join(filtered) if filtered else ""
            else:
                field = str(loc)

            raw_msg: Any = err.get("msg", "Validation error")
            msg = str(raw_msg)

            if msg.startswith("Value error, "):
                msg = msg.removeprefix("Value error, ")

            normalized.append(
                {
                    "field": field,
                    "code": str(err.get("type", "validation_error")),
                    "message": msg,
                    "params": cls._normalize_error_params(err.get("ctx")),
                }
            )

        return normalized


class RequestValidationError(ValidationError):
    pass


class ResponseValidationError(ValidationError):
    pass


def register_validation_errors():
    register_custom_error(
        RequestValidationError,
        "request_validation_error",
        400,
        "Invalid input",
    )

    register_custom_error(
        ResponseValidationError,
        "response_validation_error",
        500,
        "Internal server error",
    )
