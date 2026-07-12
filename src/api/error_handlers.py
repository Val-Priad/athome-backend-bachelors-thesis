from flask import Flask, Response

from api.responses import construct_error


def register_error_handler(app: Flask) -> None:
    @app.errorhandler(Exception)
    def handle_exception(error: Exception) -> Response:
        return construct_error(error)
