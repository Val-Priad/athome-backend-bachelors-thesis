import os
from datetime import timedelta


class FlaskConfig:
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
    JWT_TOKEN_LOCATION = ["cookies"]
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    DATABASE_URL = os.getenv("DATABASE_URL")
    MEDIA_BASE_URL = os.getenv("MEDIA_BASE_URL")

    RATELIMIT_HEADERS_ENABLED = True
    RATELIMIT_STORAGE_URI = os.getenv("RATE_LIMIT_STORAGE_URI")
    RATELIMIT_STRATEGY = "sliding-window-counter"
    RATELIMIT_DEFAULT = "200/hour"
    JWT_COOKIE_SECURE = False


class DevelopmentConfig(FlaskConfig):
    RATELIMIT_ENABLED = True


class TestingConfig(DevelopmentConfig):
    TESTING = True
    RATELIMIT_ENABLED = False
    RATELIMIT_STORAGE_URI = os.getenv("RATE_LIMIT_TEST_STORAGE_URI")
    DATABASE_URL = os.getenv("TEST_DATABASE_URL")
    MEDIA_BASE_URL = os.getenv("MEDIA_BASE_URL", "https://media.test")


class ProductionConfig(FlaskConfig):
    JWT_COOKIE_SECURE = True
