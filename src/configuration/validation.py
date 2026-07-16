from flask import Flask

REQUIRED_CONFIG_KEYS = (
    "APP_BASE_URL",
    "DATABASE_URL",
    "JWT_SECRET_KEY",
    "MEDIA_BASE_URL",
    "RATELIMIT_STORAGE_URI",
    "RESEND_API_KEY",
)


def validate_required_config(app: Flask) -> None:
    missing_keys = [
        key for key in REQUIRED_CONFIG_KEYS if not app.config.get(key)
    ]

    if missing_keys:
        joined_keys = ", ".join(missing_keys)
        raise RuntimeError(
            f"Missing required application config: {joined_keys}"
        )
