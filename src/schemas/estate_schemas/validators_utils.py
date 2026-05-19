from typing import cast

from pydantic_core import InitErrorDetails


def make_value_error(
    loc: tuple[str, ...],
    message: str,
    input_value=None,
) -> InitErrorDetails:
    return cast(
        InitErrorDetails,
        {
            "type": "value_error",
            "loc": loc,
            "input": input_value,
            "ctx": {
                "error": ValueError(message),
            },
        },
    )
