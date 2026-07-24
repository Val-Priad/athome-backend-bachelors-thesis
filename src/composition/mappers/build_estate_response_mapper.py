from application.estate.mapping.estate_response_mapper import (
    EstateResponseMapper,
)
from application.media.media_url_builder import MediaUrlBuilder
from application.users.mapping.user_response_mapper import UserResponseMapper


def build_estate_response_mapper(
    media_url_builder: MediaUrlBuilder,
    user_response_mapper: UserResponseMapper,
) -> EstateResponseMapper:
    return EstateResponseMapper(
        media_url_builder=media_url_builder,
        user_response_mapper=user_response_mapper,
    )
