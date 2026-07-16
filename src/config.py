from datetime import timedelta


class FlaskConfig:
    JWT_TOKEN_LOCATION = ["cookies"]
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)

    RATELIMIT_HEADERS_ENABLED = True
    RATELIMIT_STRATEGY = "sliding-window-counter"
    RATELIMIT_DEFAULT = "200/hour"
    JWT_COOKIE_SECURE = False


class DevelopmentConfig(FlaskConfig):
    RATELIMIT_ENABLED = True


class TestingConfig(DevelopmentConfig):
    TESTING = True
    RATELIMIT_ENABLED = False


class ProductionConfig(FlaskConfig):
    JWT_COOKIE_SECURE = True
