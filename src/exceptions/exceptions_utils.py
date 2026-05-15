from functools import wraps
from typing import Callable, cast

from .error_catalog import DomainError


def wrap_with_custom_error(
    *,
    wrap_with: type[DomainError],
    catch: type[Exception] | tuple[type[Exception], ...],
):
    def decorator(fn: Callable):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            try:
                return fn(*args, **kwargs)
            except catch as e:
                from_exception = getattr(wrap_with, "from_exception", None)
                if callable(from_exception):
                    typed_from_exception = cast(
                        Callable[[Exception], DomainError], from_exception
                    )
                    raise typed_from_exception(e) from e
                raise wrap_with from e

        return wrapper

    return decorator
