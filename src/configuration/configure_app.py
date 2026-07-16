from collections.abc import Mapping

from flask import Flask

from config import FlaskConfig
from configuration.environment_mapping import load_environment_config
from configuration.validation import validate_required_config


def configure_app(
    app: Flask,
    config: type[FlaskConfig],
    overrides: Mapping[str, object] | None = None,
) -> None:
    app.config.from_object(config)
    load_environment_config(app)

    if overrides:
        app.config.update(overrides)

    validate_required_config(app)
