from enum import Enum


class MediaPurpose(str, Enum):
    estate = "estate"
    user_avatar = "user_avatar"


class MediaType(str, Enum):
    image = "image"
    video = "video"
