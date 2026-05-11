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

    def delete_user(self, session, requester_id, user_id):
        self.ensure_has_rights(session, requester_id, UserRole.admin)

        user = self.user_repository.get_user_by_id(session, user_id)
        if user.role == UserRole.admin:
            raise ForbiddenError()

        self.delete_user_by_id(session, user_id)

    def get_user_by_id(self, session, user_id):
        return self.user_repository.get_user_by_id(session, user_id)

    def change_user_role(
        self,
        session: Session,
        requester_id: UUID,
        user_id: UUID,
        role: UserRole,
    ):
        self.ensure_has_rights(session, requester_id, UserRole.admin)

        user = self.user_repository.get_user_by_id(session, user_id)

        if user.role == UserRole.admin:
            raise ForbiddenError()
        elif role == user.role:
            raise UserStateConflictError()

        user.role = role

    def delete_user_by_id(self, session: Session, user_id: UUID) -> None:
        session.delete(self.user_repository.get_user_by_id(session, user_id))

    def ensure_has_rights(
        self, session: Session, requester_id: UUID, *roles: UserRole
    ) -> None:
        requester = self.get_user_by_id(session, requester_id)
        if requester.role not in roles:
            raise ForbiddenError()

    def list_users(
        self,
        session: Session,
        requester_id: UUID,
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
        self.ensure_has_rights(session, requester_id, UserRole.admin)

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
