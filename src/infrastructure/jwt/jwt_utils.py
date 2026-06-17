from uuid import UUID

from flask_jwt_extended import get_jwt_identity


def get_jwt_user_uuid():
    identity = get_jwt_identity()
    if identity is None:
        raise RuntimeError("Missing jwt identity")
    return UUID(identity)


def get_optional_jwt_user_uuid() -> UUID | None:
    identity = get_jwt_identity()
    if identity is None:
        return None
    return UUID(identity)
