from typing import Literal
from uuid import UUID

from sqlalchemy.orm import Session

from domain.user.user_model import UserRole
from domain.user.user_repository import UserRepository
from exceptions.custom_exceptions.user_exceptions import (
    ForbiddenError,
    UserStateConflictError,
)


class AdminUsersService:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    def delete_user(self, session: Session, user_id: UUID):
        user = self.user_repository.get_user_by_id(session, user_id)
        if user.role == UserRole.admin:
            raise ForbiddenError()

        session.delete(self.user_repository.get_user_by_id(session, user_id))

    def change_user_role(
        self,
        session: Session,
        user_id: UUID,
        role: UserRole,
    ):
        user = self.user_repository.get_user_by_id(session, user_id)

        if user.role == UserRole.admin:
            raise ForbiddenError()
        elif role == user.role:
            raise UserStateConflictError()

        user.role = role

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
    ):
        return self.user_repository.list_users(
            session,
            role=role,
            email=email,
            name=name,
            phone_number=phone_number,
            is_email_verified=is_email_verified,
            sort_by=sort_by,
            sort_order=sort_order,
            page=page,
            page_size=page_size,
        )
