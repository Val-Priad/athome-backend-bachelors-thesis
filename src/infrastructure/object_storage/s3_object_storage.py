from typing import Any

import boto3
from botocore.exceptions import BotoCoreError, ClientError

from application.ports.object_storage import ObjectStorageError

_NOT_FOUND_ERROR_CODES = frozenset({"404", "NoSuchKey", "NotFound"})
_MAX_DELETE_OBJECTS = 1000


class S3ObjectStorage:
    def __init__(
        self,
        *,
        bucket_name: str,
        region: str,
        access_key_id: str,
        secret_access_key: str,
        presigned_url_ttl_seconds: int = 300,
        client: Any | None = None,
    ) -> None:
        if presigned_url_ttl_seconds <= 0:
            raise ValueError("Presigned URL TTL must be greater than zero")

        self._bucket_name = bucket_name
        self._presigned_url_ttl_seconds = presigned_url_ttl_seconds
        self._client = (
            client
            if client is not None
            else boto3.client(
                "s3",
                region_name=region,
                aws_access_key_id=access_key_id,
                aws_secret_access_key=secret_access_key,
            )
        )

    def create_upload_url(
        self,
        *,
        object_key: str,
        content_type: str,
        size_bytes: int,
    ) -> str:
        try:
            return self._client.generate_presigned_url(
                "put_object",
                Params={
                    "Bucket": self._bucket_name,
                    "Key": object_key,
                    "ContentType": content_type,
                    "ContentLength": size_bytes,
                },
                ExpiresIn=self._presigned_url_ttl_seconds,
                HttpMethod="PUT",
            )
        except (BotoCoreError, ClientError) as error:
            raise ObjectStorageError(
                "Failed to create an S3 upload URL"
            ) from error

    def object_exists(self, object_key: str) -> bool:
        try:
            self._client.head_object(
                Bucket=self._bucket_name,
                Key=object_key,
            )
        except ClientError as error:
            error_code = str(error.response.get("Error", {}).get("Code", ""))
            status_code = error.response.get("ResponseMetadata", {}).get(
                "HTTPStatusCode"
            )
            if error_code in _NOT_FOUND_ERROR_CODES or status_code == 404:
                return False
            raise ObjectStorageError("Failed to check an S3 object") from error
        except BotoCoreError as error:
            raise ObjectStorageError("Failed to check an S3 object") from error

        return True

    def delete_object(self, object_key: str) -> None:
        try:
            self._client.delete_object(
                Bucket=self._bucket_name,
                Key=object_key,
            )
        except (BotoCoreError, ClientError) as error:
            raise ObjectStorageError(
                "Failed to delete an S3 object"
            ) from error

    def delete_objects(self, object_keys: list[str]) -> None:
        for offset in range(0, len(object_keys), _MAX_DELETE_OBJECTS):
            batch = object_keys[offset : offset + _MAX_DELETE_OBJECTS]
            self._delete_objects_batch(batch)

    def _delete_objects_batch(self, object_keys: list[str]) -> None:
        if not object_keys:
            return

        try:
            response = self._client.delete_objects(
                Bucket=self._bucket_name,
                Delete={
                    "Objects": [
                        {"Key": object_key} for object_key in object_keys
                    ],
                    "Quiet": True,
                },
            )
        except (BotoCoreError, ClientError) as error:
            raise ObjectStorageError("Failed to delete S3 objects") from error

        if response.get("Errors"):
            raise ObjectStorageError("S3 failed to delete one or more objects")
