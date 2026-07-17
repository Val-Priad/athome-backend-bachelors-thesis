from schemas.parent_types import ResponseValidation


class PresignedUploadResponse(ResponseValidation):
    upload_url: str
    object_key: str
    expires_in: int
