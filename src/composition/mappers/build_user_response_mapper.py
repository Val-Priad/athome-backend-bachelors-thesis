from application.media.media_url_builder import MediaUrlBuilder
from application.users.mapping.user_response_mapper import UserResponseMapper


def build_user_response_mapper(
    media_url_builder: MediaUrlBuilder,
) -> UserResponseMapper:
    return UserResponseMapper(
        media_url_builder=media_url_builder,
    )
