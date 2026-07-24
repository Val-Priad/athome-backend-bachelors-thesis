from typing import TypeVar

from application.media.media_url_builder import MediaUrlBuilder
from schemas.parent_types import ResponseValidation

ResponseT = TypeVar("ResponseT", bound=ResponseValidation)


class UserResponseMapper:
    def __init__(self, media_url_builder: MediaUrlBuilder) -> None:
        self._media_url_builder = media_url_builder

    def to_response(
        self,
        response_type: type[ResponseT],
        user: object,
    ) -> ResponseT:
        response = response_type.from_model(user)
        avatar_url = (
            self._media_url_builder.build(response.avatar_key)
            if response.avatar_key is not None
            else None
        )
        return response.model_copy(update={"avatar_url": avatar_url})
