import os

from flask import Flask

ENVIRONMENT_CONFIG_MAPPING = {
    "APP_BASE_URL": "APP_BASE_URL",
    "DATABASE_URL": "DATABASE_URL",
    "JWT_SECRET_KEY": "JWT_SECRET_KEY",
    "MEDIA_BASE_URL": "MEDIA_BASE_URL",
    "RATELIMIT_STORAGE_URI": "RATE_LIMIT_STORAGE_URI",
    "RESEND_API_KEY": "RESEND_API_KEY",
}


def load_environment_config(app: Flask) -> None:
    environment_values = {
        config_key: os.getenv(environment_key)
        for config_key, environment_key in ENVIRONMENT_CONFIG_MAPPING.items()
    }

    if app.config.get("TESTING"):
        environment_values["DATABASE_URL"] = os.getenv(
            "TEST_DATABASE_URL",
            environment_values["DATABASE_URL"],
        )
        environment_values["RATELIMIT_STORAGE_URI"] = os.getenv(
            "RATE_LIMIT_TEST_STORAGE_URI",
            environment_values["RATELIMIT_STORAGE_URI"],
        )
        environment_values["MEDIA_BASE_URL"] = (
            environment_values["MEDIA_BASE_URL"] or "https://media.test"
        )

    app.config.update(
        {
            key: value
            for key, value in environment_values.items()
            if value is not None
        }
    )
