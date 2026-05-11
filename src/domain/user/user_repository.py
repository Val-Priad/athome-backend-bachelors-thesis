from typing import Literal
from uuid import UUID

from sqlalchemy import asc, desc, exists, func, select
from sqlalchemy.orm import Session

from domain.user.user_model import User, UserRole
from exceptions.custom_exceptions.user_exceptions import UserNotFoundError


class UserRepository:
    def exists_by_email(self, session: Session, email: str) -> bool:
        return session.execute(
            select(exists().where(User.email == email))
        ).scalar_one()

    def get_user_by_email(self, session: Session, email: str) -> User:
        result = session.scalar(select(User).where(User.email == email))
        if result is None:
            raise UserNotFoundError()
        return result

    def get_user_by_id(self, session: Session, user_id: UUID) -> User:
        result = session.scalar(select(User).where(User.id == user_id))
        if result is None:
            raise UserNotFoundError()
        return result

    def list_users(
        self,
        session: Session,
        *,
        role: UserRole | None = None,
        email: str | None = None,
        name: str | None = None,
        phone_number: str | None = None,
        is_email_verified: bool | None = None,
        sort_by: str,
        sort_order: Literal["asc", "desc"],
        page: int,
        page_size: int,
    ) -> tuple[list[User], int]:
        stmt = select(User)
        if role is not None:
            stmt = stmt.where(User.role == role)

        if is_email_verified is not None:
            stmt = stmt.where(User.is_email_verified == is_email_verified)

        if email:
            stmt = stmt.where(User.email.ilike(f"%{email}%"))

        if name:
            stmt = stmt.where(User.name.ilike(f"%{name}%"))

        if phone_number:
            stmt = stmt.where(User.phone_number.ilike(f"%{phone_number}%"))

        total = (
            session.scalar(select(func.count()).select_from(stmt.subquery()))
            or 0
        )

        sort_columns = {
            "email": User.email,
            "name": User.name,
            "phone_number": User.phone_number,
            "is_email_verified": User.is_email_verified,
            "created_at": User.created_at,
        }

        sort_column = sort_columns[sort_by]

        if sort_order == "asc":
            stmt = stmt.order_by(asc(sort_column), asc(User.id))
        else:
            stmt = stmt.order_by(desc(sort_column), asc(User.id))

        offset = (page - 1) * page_size

        users = session.scalars(stmt.offset(offset).limit(page_size)).all()

        return list(users), total
