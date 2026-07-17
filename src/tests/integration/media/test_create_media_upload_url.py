from tests.integration.conftest import MEDIA_PATH

UPLOAD_URL_PATH = f"{MEDIA_PATH}/upload-url"


def _payload(**overrides):
    payload = {
        "purpose": "user_avatar",
        "filename": "avatar.webp",
        "content_type": "image/webp",
        "size_bytes": 1024,
    }
    payload.update(overrides)
    return payload


def test_user_can_create_avatar_upload_url(client, logged_in_user) -> None:
    response = client.post(
        UPLOAD_URL_PATH,
        json=_payload(),
        headers=logged_in_user.headers,
    )

    assert response.status_code == 200
    data = response.get_json()["data"]
    assert data["upload_url"] == (f"https://storage.test/{data['object_key']}")
    assert data["expires_in"] == 300


def test_user_can_create_estate_video_upload_url(
    client,
    logged_in_user,
) -> None:
    response = client.post(
        UPLOAD_URL_PATH,
        json=_payload(
            purpose="estate",
            filename="tour.mp4",
            content_type="video/mp4",
        ),
        headers=logged_in_user.headers,
    )

    assert response.status_code == 200


def test_avatar_upload_rejects_video(client, logged_in_user) -> None:
    response = client.post(
        UPLOAD_URL_PATH,
        json=_payload(content_type="video/mp4"),
        headers=logged_in_user.headers,
    )

    assert response.status_code == 400
    assert response.get_json()["error"]["errors"][0]["message"] == (
        "User avatar must be an image"
    )


def test_create_upload_url_requires_authentication(client) -> None:
    response = client.post(UPLOAD_URL_PATH, json=_payload())

    assert response.status_code == 401
