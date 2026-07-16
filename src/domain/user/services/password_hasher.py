import bcrypt

from exceptions.custom_exceptions.user_exceptions import (
    PasswordVerificationError,
)


class PasswordHasher:
    @staticmethod
    def hash_password(raw_password: str) -> bytes:
        return bcrypt.hashpw(raw_password.encode(), bcrypt.gensalt())

    @staticmethod
    def verify_password(raw_password: str, hashed_password: bytes) -> None:
        if not bcrypt.checkpw(raw_password.encode(), hashed_password):
            raise PasswordVerificationError(
                "The provided password does not match the stored password"
            )
