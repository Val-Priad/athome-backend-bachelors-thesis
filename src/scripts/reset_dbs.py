import os
import sys
from importlib import import_module
from pathlib import Path
from pkgutil import walk_packages

from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.engine import make_url


def add_src_to_path() -> None:
    project_root = Path(__file__).resolve().parents[2]
    src_path = project_root / "src"

    if str(src_path) not in sys.path:
        sys.path.insert(0, str(src_path))


def load_model_modules() -> None:
    import domain

    for module_info in walk_packages(domain.__path__, domain.__name__ + "."):
        if module_info.ispkg:
            continue

        if not module_info.name.endswith("_model"):
            continue

        import_module(module_info.name)


def create_database_if_not_exists(database_url: str) -> None:
    url = make_url(database_url)
    database_name = url.database

    if not database_name:
        raise RuntimeError("Database name is missing in database URL")

    maintenance_url = url.set(database="postgres")

    engine = create_engine(
        maintenance_url,
        isolation_level="AUTOCOMMIT",
    )

    try:
        with engine.connect() as connection:
            exists = connection.execute(
                text(
                    "SELECT 1 FROM pg_database WHERE datname = :database_name"
                ),
                {"database_name": database_name},
            ).scalar()

            if exists:
                return

            quoted_database_name = database_name.replace('"', '""')
            connection.execute(
                text(f'CREATE DATABASE "{quoted_database_name}"')
            )

            print(f"Database created: {database_name}")

    finally:
        engine.dispose()


def reset_and_create_schema(database_url: str) -> None:
    from infrastructure.db import Base

    create_database_if_not_exists(database_url)

    engine = create_engine(database_url)

    try:
        Base.metadata.drop_all(bind=engine)
        Base.metadata.create_all(bind=engine)

    finally:
        engine.dispose()


def get_database_url(env_var_name: str) -> str:
    database_url = os.getenv(env_var_name)

    if not database_url:
        raise RuntimeError(f"{env_var_name} is not set")

    return database_url


def main() -> None:
    add_src_to_path()

    load_dotenv(Path(__file__).resolve().parents[2] / ".env")

    load_model_modules()

    reset_and_create_schema(get_database_url("DATABASE_URL"))
    reset_and_create_schema(get_database_url("TEST_DATABASE_URL"))

    print("Database schemas created")


if __name__ == "__main__":
    main()
