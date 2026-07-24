from datetime import timedelta


class FlaskConfig:
    CONFIG_PROFILE = "development"
    JWT_TOKEN_LOCATION = ["cookies"]
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)

    S3_BUCKET_NAME: str | None = None
    S3_REGION: str | None = None
    S3_ACCESS_KEY_ID: str | None = None
    S3_SECRET_ACCESS_KEY: str | None = None
    S3_PRESIGNED_URL_TTL_SECONDS = 300
    MEDIA_ORPHAN_MIN_AGE_HOURS = 24

    RATELIMIT_HEADERS_ENABLED = True
    RATELIMIT_STRATEGY = "sliding-window-counter"
    RATELIMIT_DEFAULT = "200/hour"
    JWT_COOKIE_SECURE = False


class DevelopmentConfig(FlaskConfig):
    RATELIMIT_ENABLED = True


class TestingConfig(DevelopmentConfig):
    CONFIG_PROFILE = "testing"
    TESTING = True
    RATELIMIT_ENABLED = False


class ProductionConfig(FlaskConfig):
    CONFIG_PROFILE = "production"
    JWT_COOKIE_SECURE = True
