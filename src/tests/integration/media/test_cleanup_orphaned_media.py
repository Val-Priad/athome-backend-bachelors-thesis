from datetime import datetime, timedelta, timezone
from uuid import uuid4

from application.ports.object_storage import StoredObject
from domain.estate.enums.estate_listing_enums import ListingStatus
from domain.estate.models.estate_media_model import EstateMedia
from domain.media.media_enums import MediaType
from tests.integration.estate.test_filter_estate import create_filter_estate


def _object_key(uploader_id) -> str:
    return f"estate-media/{uploader_id}/{uuid4()}.webp"


def _avatar_key(uploader_id) -> str:
    return f"user-avatars/{uploader_id}/{uuid4()}.webp"


def test_orphan_cleanup_preserves_real_database_references(
    application_container,
    db_session,
    any_user,
    fake_object_storage,
):
    used_estate_key = _object_key(any_user.id)
    orphan_estate_key = _object_key(any_user.id)
    used_avatar_key = _avatar_key(any_user.id)
    orphan_avatar_key = _avatar_key(any_user.id)

    create_filter_estate(
        db_session,
        title="Orphan cleanup protected estate",
        status=ListingStatus.draft,
        media=[
            EstateMedia(
                object_key=used_estate_key,
                media_type=MediaType.image,
                position=0,
            )
        ],
    )
    any_user.avatar_key = used_avatar_key
    db_session.flush()

    old = datetime.now(timezone.utc) - timedelta(days=2)
    fake_object_storage.stored_objects = [
        StoredObject(used_estate_key, old),
        StoredObject(orphan_estate_key, old),
        StoredObject(used_avatar_key, old),
        StoredObject(orphan_avatar_key, old),
    ]

    result = application_container.media.cleanup_orphans.execute()

    assert fake_object_storage.deleted_object_keys == [
        orphan_estate_key,
        orphan_avatar_key,
    ]
    assert result.used == 2
    assert result.deleted == 2
