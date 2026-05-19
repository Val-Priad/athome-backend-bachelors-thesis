import os
import sys
from importlib import import_module
from pathlib import Path
from pkgutil import walk_packages

from dotenv import load_dotenv
from sqlalchemy import create_engine


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


def reset_and_create_schema(database_url: str) -> None:
    from infrastructure.db import Base

    engine = create_engine(database_url)

    load_model_modules()
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


def get_database_url(env_var_name: str) -> str:
    database_url = os.getenv(env_var_name)
    if not database_url:
        raise RuntimeError(f"{env_var_name} is not set")

    return database_url


def main() -> None:
    add_src_to_path()

    load_dotenv(Path(__file__).resolve().parents[2] / ".env")

    reset_and_create_schema(get_database_url("DATABASE_URL"))
    reset_and_create_schema(get_database_url("TEST_DATABASE_URL"))

    print("Database schema created")


if __name__ == "__main__":
    main()
