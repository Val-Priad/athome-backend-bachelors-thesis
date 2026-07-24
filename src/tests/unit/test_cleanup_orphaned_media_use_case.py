from collections.abc import Iterator
from contextlib import contextmanager
from datetime import datetime, timedelta, timezone
from logging import LogRecord
from unittest.mock import Mock, call

import pytest

from application.media.cleanup_orphaned_media_use_case import (
    CleanupOrphanedMediaUseCase,
)
from application.ports.object_storage import ObjectStorageError, StoredObject
from domain.media.media_enums import MediaPurpose

NOW = datetime.now(timezone.utc)
OLD = NOW - timedelta(days=2)
FRESH = NOW - timedelta(hours=1)


def test_rejects_non_positive_min_object_age() -> None:
    with pytest.raises(ValueError, match="Minimum object age"):
        CleanupOrphanedMediaUseCase(
            transactions=Mock(),
            media_usage_service=Mock(),
            object_storage=Mock(),
            min_object_age=timedelta(0),
        )


def test_rejects_non_positive_batch_size() -> None:
    with pytest.raises(ValueError, match="Batch size"):
        CleanupOrphanedMediaUseCase(
            transactions=Mock(),
            media_usage_service=Mock(),
            object_storage=Mock(),
            min_object_age=timedelta(hours=24),
            batch_size=0,
        )


def _transactions() -> Mock:
    transactions = Mock()

    @contextmanager
    def session() -> Iterator[Mock]:
        yield Mock()

    transactions.session.side_effect = session
    return transactions


def _use_case(
    *,
    objects_by_prefix: dict[str, list[StoredObject]] | None = None,
    storage: Mock | None = None,
    usage_service: Mock | None = None,
    transactions: Mock | None = None,
    batch_size: int = 500,
) -> tuple[CleanupOrphanedMediaUseCase, Mock, Mock, Mock]:
    if storage is None:
        storage = Mock()
    if usage_service is None:
        usage_service = Mock()
        usage_service.get_used_object_keys.return_value = set()
    if transactions is None:
        transactions = _transactions()
    if objects_by_prefix is not None:
        storage.iter_objects.side_effect = lambda *, prefix: iter(
            objects_by_prefix.get(prefix, [])
        )
    elif storage.iter_objects.side_effect is None:
        storage.iter_objects.side_effect = lambda *, prefix: iter(())

    return (
        CleanupOrphanedMediaUseCase(
            transactions=transactions,
            media_usage_service=usage_service,
            object_storage=storage,
            min_object_age=timedelta(hours=24),
            batch_size=batch_size,
        ),
        storage,
        usage_service,
        transactions,
    )


def test_deletes_old_unused_object() -> None:
    key = "estate-media/user/old.webp"
    use_case, storage, _, _ = _use_case(
        objects_by_prefix={
            "estate-media/": [StoredObject(key, OLD)],
        }
    )

    result = use_case.execute()

    storage.delete_objects.assert_called_once_with([key])
    assert result.scanned == 1
    assert result.eligible == 1
    assert result.used == 0
    assert result.deleted == 1
    assert result.failed == 0


def test_does_not_delete_used_object() -> None:
    key = "estate-media/user/used.webp"
    usage_service = Mock()
    usage_service.get_used_object_keys.return_value = {key}
    use_case, storage, _, _ = _use_case(
        objects_by_prefix={
            "estate-media/": [StoredObject(key, OLD)],
        },
        usage_service=usage_service,
    )

    result = use_case.execute()

    storage.delete_objects.assert_not_called()
    assert result.used == 1
    assert result.deleted == 0


def test_ignores_fresh_object_without_database_lookup() -> None:
    key = "estate-media/user/fresh.webp"
    use_case, storage, usage_service, transactions = _use_case(
        objects_by_prefix={
            "estate-media/": [StoredObject(key, FRESH)],
        }
    )

    result = use_case.execute()

    usage_service.get_used_object_keys.assert_not_called()
    transactions.session.assert_not_called()
    storage.delete_objects.assert_not_called()
    assert result.scanned == 1
    assert result.eligible == 0


def test_checks_each_purpose_through_media_usage_service() -> None:
    estate_key = "estate-media/user/estate.webp"
    avatar_key = "user-avatars/user/avatar.webp"
    use_case, storage, usage_service, _ = _use_case(
        objects_by_prefix={
            "estate-media/": [StoredObject(estate_key, OLD)],
            "user-avatars/": [StoredObject(avatar_key, OLD)],
        }
    )

    use_case.execute()

    assert storage.iter_objects.call_args_list == [
        call(prefix="estate-media/"),
        call(prefix="user-avatars/"),
    ]
    assert [
        item.kwargs["purpose"]
        for item in usage_service.get_used_object_keys.call_args_list
    ] == [
        MediaPurpose.estate,
        MediaPurpose.user_avatar,
    ]
    assert [
        item.kwargs["object_keys"]
        for item in usage_service.get_used_object_keys.call_args_list
    ] == [[estate_key], [avatar_key]]


def test_processes_eligible_objects_in_batches() -> None:
    keys = [f"estate-media/user/{index}.webp" for index in range(5)]
    use_case, storage, usage_service, _ = _use_case(
        objects_by_prefix={
            "estate-media/": [StoredObject(key, OLD) for key in keys],
        },
        batch_size=2,
    )

    result = use_case.execute()

    assert usage_service.get_used_object_keys.call_count == 3
    assert storage.delete_objects.call_args_list == [
        call(keys[:2]),
        call(keys[2:4]),
        call(keys[4:]),
    ]
    assert result.deleted == 5


def test_delete_failure_does_not_stop_later_batches(caplog) -> None:
    keys = [f"estate-media/user/{index}.webp" for index in range(12)]
    storage = Mock()
    storage.delete_objects.side_effect = [
        ObjectStorageError("S3 unavailable"),
        None,
    ]
    use_case, storage, _, _ = _use_case(
        objects_by_prefix={
            "estate-media/": [StoredObject(key, OLD) for key in keys],
        },
        storage=storage,
        batch_size=11,
    )

    result = use_case.execute()

    assert storage.delete_objects.call_args_list == [
        call(keys[:11]),
        call(keys[11:]),
    ]
    assert result.deleted == 1
    assert result.failed == 11

    error_record = next(
        record
        for record in caplog.records
        if record.message == "Failed to delete orphaned media objects"
    )
    assert isinstance(error_record, LogRecord)
    assert getattr(error_record, "object_key_count") == 11
    assert getattr(error_record, "object_keys_sample") == keys[:10]
    assert not hasattr(error_record, "object_keys")


def test_database_failure_does_not_delete_objects() -> None:
    key = "estate-media/user/old.webp"
    usage_service = Mock()
    usage_service.get_used_object_keys.side_effect = RuntimeError(
        "PostgreSQL unavailable"
    )
    use_case, storage, _, _ = _use_case(
        objects_by_prefix={
            "estate-media/": [StoredObject(key, OLD)],
        },
        usage_service=usage_service,
    )

    with pytest.raises(RuntimeError, match="PostgreSQL unavailable"):
        use_case.execute()

    storage.delete_objects.assert_not_called()


def test_empty_prefixes_return_zero_counts() -> None:
    use_case, storage, _, _ = _use_case()

    result = use_case.execute()

    assert result.scanned == 0
    assert result.eligible == 0
    assert result.used == 0
    assert result.deleted == 0
    assert result.failed == 0
    storage.delete_objects.assert_not_called()


def test_listing_failure_is_not_treated_as_empty_prefix() -> None:
    storage = Mock()

    def iter_objects(*, prefix: str) -> Iterator[StoredObject]:
        raise ObjectStorageError(f"Cannot list {prefix}")
        yield

    storage.iter_objects.side_effect = iter_objects
    use_case, storage, _, _ = _use_case(storage=storage)

    with pytest.raises(ObjectStorageError):
        use_case.execute()

    storage.delete_objects.assert_not_called()


def test_database_session_is_closed_before_deleting() -> None:
    key = "estate-media/user/old.webp"
    session_is_open = False
    transactions = Mock()
    storage = Mock()

    @contextmanager
    def session() -> Iterator[Mock]:
        nonlocal session_is_open
        session_is_open = True
        try:
            yield Mock()
        finally:
            session_is_open = False

    transactions.session.side_effect = session

    def delete_objects(object_keys: list[str]) -> None:
        assert object_keys == [key]
        assert session_is_open is False

    storage.delete_objects.side_effect = delete_objects
    use_case, _, _, _ = _use_case(
        objects_by_prefix={
            "estate-media/": [StoredObject(key, OLD)],
        },
        storage=storage,
        transactions=transactions,
    )

    use_case.execute()
