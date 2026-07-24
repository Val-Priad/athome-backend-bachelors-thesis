import logging

import click
from flask import Flask
from flask.cli import with_appcontext

from composition.container_access import get_application_container

_logger = logging.getLogger(__name__)


@click.group("users")
def users_cli() -> None:
    """Run internal user maintenance commands."""


@users_cli.command("cleanup-unverified")
@with_appcontext
def cleanup_unverified() -> None:
    """Delete unverified users older than the verification period."""
    try:
        deleted = (
            get_application_container().users.cleanup_unverified.execute()
        )
    except Exception as error:
        _logger.exception("Unverified user cleanup failed")
        raise click.ClickException("Unverified user cleanup failed") from error

    click.echo(f"Cleanup completed: deleted={deleted}")


def register_user_commands(app: Flask) -> None:
    app.cli.add_command(users_cli)
