from exceptions.error_catalog import DomainError, register_custom_error


class MediaUploadError(DomainError):
    pass


class MediaObjectNotFoundError(DomainError):
    pass


class InvalidMediaObjectKeyError(DomainError):
    pass


class MediaObjectAlreadyUsedError(DomainError):
    pass


def register_media_errors() -> None:
    register_custom_error(
        MediaUploadError,
        "media_upload_failed",
        503,
        "Media upload is temporarily unavailable",
    )
    register_custom_error(
        MediaObjectNotFoundError,
        "media_object_not_found",
        400,
        "Media object not found",
    )
    register_custom_error(
        InvalidMediaObjectKeyError,
        "invalid_media_object_key",
        400,
        "Invalid media object key",
    )
    register_custom_error(
        MediaObjectAlreadyUsedError,
        "media_object_already_used",
        409,
        "Media object is already used",
    )
