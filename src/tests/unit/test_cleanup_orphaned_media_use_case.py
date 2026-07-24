from collections.abc import Iterator
from contextlib import contextmanager
from datetime import datetime, timedelta, timezone
from logging import LogRecord
from unittest.mock import ANY, Mock, call, patch

import pytest

from application.media.cleanup_orphaned_media_use_case import (
    CleanupOrphanedMediaUseCase,
    OrphanCleanupResult,
)
from application.ports.object_storage import ObjectStorageError, StoredObject
from domain.media.media_enums import MediaPurpose

NOW = datetime(2026, 7, 24, 12, tzinfo=timezone.utc)
OLD = datetime(2000, 1, 1, tzinfo=timezone.utc)


@pytest.mark.parametrize(
    ("min_object_age", "batch_size", "message"),
    [
        (timedelta(0), 500, "Minimum object age"),
        (timedelta(hours=24), 0, "Batch size"),
    ],
)
def test_rejects_invalid_cleanup_limits(
    min_object_age: timedelta,
    batch_size: int,
    message: str,
) -> None:
    with pytest.raises(ValueError, match=message):
        CleanupOrphanedMediaUseCase(
            transactions=Mock(),
            media_usage_service=Mock(),
            object_storage=Mock(),
            min_object_age=min_object_age,
            batch_size=batch_size,
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
    assert result == OrphanCleanupResult(
        scanned=1,
        eligible=1,
        used=1,
        deleted=0,
        failed=0,
    )


def test_processes_each_configured_media_purpose() -> None:
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
    assert usage_service.get_used_object_keys.call_args_list == [
        call(
            session=ANY,
            purpose=MediaPurpose.estate,
            object_keys=[estate_key],
        ),
        call(
            session=ANY,
            purpose=MediaPurpose.user_avatar,
            object_keys=[avatar_key],
        ),
    ]


def test_cutoff_includes_boundary_and_skips_fresh_objects() -> None:
    old_key = "estate-media/user/old.webp"
    boundary_key = "estate-media/user/boundary.webp"
    fresh_key = "estate-media/user/fresh.webp"
    use_case, storage, usage_service, transactions = _use_case(
        objects_by_prefix={
            "estate-media/": [
                StoredObject(old_key, OLD),
                StoredObject(
                    boundary_key,
                    NOW - timedelta(hours=24),
                ),
                StoredObject(
                    fresh_key,
                    NOW - timedelta(hours=24) + timedelta(microseconds=1),
                ),
            ],
        }
    )

    with patch(
        "application.media.cleanup_orphaned_media_use_case.datetime"
    ) as mocked_datetime:
        mocked_datetime.now.return_value = NOW
        result = use_case.execute()

    usage_service.get_used_object_keys.assert_called_once()
    transactions.session.assert_called_once()
    storage.delete_objects.assert_called_once_with([old_key, boundary_key])
    assert result == OrphanCleanupResult(
        scanned=3,
        eligible=2,
        used=0,
        deleted=2,
        failed=0,
    )


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
    assert result == OrphanCleanupResult(
        scanned=5,
        eligible=5,
        used=0,
        deleted=5,
        failed=0,
    )


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
    assert result == OrphanCleanupResult(
        scanned=12,
        eligible=12,
        used=0,
        deleted=1,
        failed=11,
    )

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


def test_listing_failure_propagates_without_deleting_objects() -> None:
    storage = Mock()

    def iter_objects(*, prefix: str) -> Iterator[StoredObject]:
        raise ObjectStorageError(f"Cannot list {prefix}")
        yield

    storage.iter_objects.side_effect = iter_objects
    use_case, storage, _, _ = _use_case(storage=storage)

    with pytest.raises(ObjectStorageError, match="Cannot list"):
        use_case.execute()

    storage.delete_objects.assert_not_called()


def test_deletes_objects_after_database_transaction_is_closed() -> None:
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
