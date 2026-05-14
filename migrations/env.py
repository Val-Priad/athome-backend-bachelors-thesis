import os
import sys
from logging.config import fileConfig

from alembic import context
from dotenv import load_dotenv
from sqlalchemy import engine_from_config, pool

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
src_path = os.path.join(project_root, "src")

if src_path not in sys.path:
    sys.path.insert(0, src_path)

from domain.email_verification.email_verification_model import (  # noqa: E402, F401
    EmailVerification,
)
from domain.estate.estate_model import Estate  # noqa: E402, F401
from domain.estate.models.estate_apartment_model import (  # noqa: E402, F401
    EstateApartment,
)
from domain.estate.models.estate_details_model import (  # noqa: E402, F401
    EstateDetails,
)
from domain.estate.models.estate_house_model import (  # noqa: E402, F401
    EstateHouse,
)
from domain.estate.models.estate_listing_model import (  # noqa: E402, F401
    EstateListing,
)
from domain.estate.models.estate_location_model import (  # noqa: E402, F401
    EstateLocation,
)
from domain.estate.models.estate_pricing_model import (  # noqa: E402, F401
    EstatePricing,
)
from domain.estate.models.estate_utilities_model import (  # noqa: E402, F401
    EstateUtilities,
)
from domain.password_reset.password_reset_model import (  # noqa: E402, F401
    PasswordReset,
)
from domain.user.user_model import User  # noqa: E402, F401
from infrastructure.db import Base  # noqa: E402

config = context.config

load_dotenv(os.path.join(project_root, ".env"))

env_db_url = os.getenv("DATABASE_URL")
if env_db_url:
    config.set_main_option("sqlalchemy.url", env_db_url)

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
