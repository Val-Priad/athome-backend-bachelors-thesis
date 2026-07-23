from dataclasses import dataclass

from domain.media.media_enums import MediaPurpose, MediaType


@dataclass(frozen=True, slots=True)
class MediaPurposeConfig:
    prefix: str
    extensions_by_media_type: dict[MediaType, frozenset[str]]


MEDIA_CONFIG_BY_PURPOSE = {
    MediaPurpose.estate: MediaPurposeConfig(
        prefix="estate-media",
        extensions_by_media_type={
            MediaType.image: frozenset({"jpg", "png", "webp"}),
            MediaType.video: frozenset({"mp4"}),
        },
    ),
    MediaPurpose.user_avatar: MediaPurposeConfig(
        prefix="user-avatars",
        extensions_by_media_type={
            MediaType.image: frozenset({"jpg", "png", "webp"}),
        },
    ),
}
