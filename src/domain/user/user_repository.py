from collections.abc import Sequence
from uuid import UUID

from sqlalchemy import RowMapping, asc, desc, exists, func, select
from sqlalchemy.orm import Session

from domain.estate.enums.estate_listing_enums import ListingStatus
from domain.estate.estate_model import Estate
from domain.estate.models.estate_listing_model import EstateListing
from domain.user.user_model import User, UserRole
from exceptions.custom_exceptions.media_exceptions import (
    MediaObjectAlreadyUsedError,
)
from exceptions.custom_exceptions.user_exceptions import UserNotFoundError
from schemas.admin_schemas.admin_users_schemas.admin_agents_request import (
    AgentListRequest,
)
from schemas.admin_schemas.admin_users_schemas.admin_users_requests import (
    UsersListRequest,
)


class UserRepository:
    def ensure_avatar_keys_unused(
        self,
        session: Session,
        object_keys: Sequence[str],
    ) -> None:
        if not object_keys:
            return

        avatar_key_used = session.execute(
            select(exists().where(User.avatar_key.in_(object_keys)))
        ).scalar_one()
        if avatar_key_used:
            raise MediaObjectAlreadyUsedError()

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
        self, session: Session, query: UsersListRequest
    ) -> tuple[list[User], int]:
        stmt = select(User)
        if query.role is not None:
            stmt = stmt.where(User.role == query.role)

        if query.is_email_verified is not None:
            stmt = stmt.where(
                User.is_email_verified == query.is_email_verified
            )

        if query.email:
            stmt = stmt.where(User.email.ilike(f"%{query.email}%"))

        if query.name:
            stmt = stmt.where(User.name.ilike(f"%{query.name}%"))

        if query.phone_number:
            stmt = stmt.where(
                User.phone_number.ilike(f"%{query.phone_number}%")
            )

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

        sort_column = sort_columns[query.sort_by]

        if query.sort_order == "asc":
            stmt = stmt.order_by(asc(sort_column), asc(User.id))
        else:
            stmt = stmt.order_by(desc(sort_column), asc(User.id))

        offset = (query.page - 1) * query.page_size

        users = session.scalars(
            stmt.offset(offset).limit(query.page_size)
        ).all()

        return list(users), total

    def list_agents(
        self, session: Session, request: AgentListRequest
    ) -> tuple[list[RowMapping], int]:
        estate_qty = (
            func.count(func.distinct(Estate.id))
            .filter(EstateListing.status == ListingStatus.active)
            .label("estate_qty")
        )

        base_stmt = (
            select(
                User.id.label("id"),
                User.email.label("email"),
                User.name.label("name"),
                User.phone_number.label("phone_number"),
                User.avatar_key.label("avatar_key"),
                User.created_at.label("created_at"),
                estate_qty,
            )
            .outerjoin(Estate, Estate.agent_id == User.id)
            .outerjoin(EstateListing, EstateListing.estate_id == Estate.id)
            .where(User.role == UserRole.agent)
            .group_by(
                User.id,
                User.email,
                User.name,
                User.phone_number,
                User.avatar_key,
                User.created_at,
            )
        )

        if request.email:
            base_stmt = base_stmt.where(User.email.ilike(f"%{request.email}%"))

        if request.name:
            base_stmt = base_stmt.where(User.name.ilike(f"%{request.name}%"))

        if request.phone_number:
            base_stmt = base_stmt.where(
                User.phone_number.ilike(f"%{request.phone_number}%")
            )

        total = (
            session.scalar(
                select(func.count()).select_from(base_stmt.subquery())
            )
            or 0
        )

        sort_map = {
            "email": User.email,
            "name": User.name,
            "phone_number": User.phone_number,
            "created_at": User.created_at,
            "estate_qty": estate_qty,
        }

        order_column = sort_map[request.sort_by]

        if request.sort_order == "desc":
            base_stmt = base_stmt.order_by(
                desc(order_column),
                asc(User.id),
            )
        else:
            base_stmt = base_stmt.order_by(
                asc(order_column),
                asc(User.id),
            )

        offset = (request.page - 1) * request.page_size

        rows = list(
            session.execute(base_stmt.offset(offset).limit(request.page_size))
            .mappings()
            .all()
        )

        return rows, total
