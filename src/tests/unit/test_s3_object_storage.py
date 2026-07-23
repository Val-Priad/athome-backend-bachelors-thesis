from unittest.mock import Mock, call

import pytest
from botocore.exceptions import ClientError, EndpointConnectionError

from application.ports.object_storage import ObjectStorageError
from infrastructure.object_storage.s3_object_storage import (
    S3ObjectStorage,
)


def _storage(client: Mock, *, ttl: int = 300) -> S3ObjectStorage:
    return S3ObjectStorage(
        bucket_name="test-bucket",
        region="eu-north-1",
        access_key_id="test-access-key",
        secret_access_key="test-secret-key",
        presigned_url_ttl_seconds=ttl,
        client=client,
    )


def _client_error(
    code: str,
    *,
    operation: str = "HeadObject",
    status: int = 400,
) -> ClientError:
    return ClientError(
        {
            "Error": {"Code": code, "Message": "S3 error"},
            "ResponseMetadata": {"HTTPStatusCode": status},
        },
        operation,
    )


def test_create_upload_url() -> None:
    client = Mock()
    client.generate_presigned_url.return_value = "https://upload.test/url"
    storage = _storage(client, ttl=600)

    result = storage.create_upload_url(
        object_key="estate-media/image.webp",
        content_type="image/webp",
        size_bytes=5242880,
    )

    assert result == "https://upload.test/url"
    client.generate_presigned_url.assert_called_once_with(
        "put_object",
        Params={
            "Bucket": "test-bucket",
            "Key": "estate-media/image.webp",
            "ContentType": "image/webp",
            "ContentLength": 5242880,
        },
        ExpiresIn=600,
        HttpMethod="PUT",
    )


def test_create_upload_url_wraps_sdk_errors() -> None:
    client = Mock()
    error = EndpointConnectionError(endpoint_url="https://s3.test")
    client.generate_presigned_url.side_effect = error

    with pytest.raises(ObjectStorageError) as raised:
        _storage(client).create_upload_url(
            object_key="estate-media/image.webp",
            content_type="image/webp",
            size_bytes=5242880,
        )

    assert raised.value.__cause__ is error


def test_object_exists_returns_true() -> None:
    client = Mock()

    assert _storage(client).object_exists("estate-media/image.webp") is True

    client.head_object.assert_called_once_with(
        Bucket="test-bucket",
        Key="estate-media/image.webp",
    )


@pytest.mark.parametrize("error_code", ["404", "NotFound", "NoSuchKey"])
def test_object_exists_returns_false_only_for_missing_object(
    error_code: str,
) -> None:
    client = Mock()
    client.head_object.side_effect = _client_error(error_code, status=404)

    assert _storage(client).object_exists("missing.webp") is False


@pytest.mark.parametrize(
    ("error_code", "status"),
    [("AccessDenied", 403), ("InternalError", 500)],
)
def test_object_exists_raises_for_non_not_found_errors(
    error_code: str,
    status: int,
) -> None:
    client = Mock()
    error = _client_error(error_code, status=status)
    client.head_object.side_effect = error

    with pytest.raises(ObjectStorageError) as raised:
        _storage(client).object_exists("estate-media/image.webp")

    assert raised.value.__cause__ is error


def test_delete_object_wraps_sdk_errors() -> None:
    client = Mock()
    error = _client_error("AccessDenied", operation="DeleteObject", status=403)
    client.delete_object.side_effect = error

    with pytest.raises(ObjectStorageError) as raised:
        _storage(client).delete_object("estate-media/image.webp")

    assert raised.value.__cause__ is error


def test_delete_objects_uses_batches_of_at_most_1000() -> None:
    client = Mock()
    client.delete_objects.return_value = {}
    object_keys = [f"estate-media/{index}.webp" for index in range(1001)]

    _storage(client).delete_objects(object_keys)

    assert client.delete_objects.call_count == 2
    assert client.delete_objects.call_args_list == [
        call(
            Bucket="test-bucket",
            Delete={
                "Objects": [
                    {"Key": object_key} for object_key in object_keys[:1000]
                ],
                "Quiet": True,
            },
        ),
        call(
            Bucket="test-bucket",
            Delete={
                "Objects": [{"Key": object_keys[1000]}],
                "Quiet": True,
            },
        ),
    ]


def test_delete_objects_checks_errors_in_successful_response() -> None:
    client = Mock()
    client.delete_objects.return_value = {
        "Errors": [{"Key": "image.webp", "Code": "AccessDenied"}]
    }

    with pytest.raises(ObjectStorageError):
        _storage(client).delete_objects(["image.webp"])
