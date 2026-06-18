from uuid import UUID

from sqlalchemy import Select, false, func, select
from sqlalchemy.orm import Session, joinedload, selectinload

from domain.estate.enums.estate_listing_enums import ListingStatus
from domain.estate.estate_model import Estate
from domain.estate.models.estate_apartment_model import EstateApartment
from domain.estate.models.estate_details_model import EstateDetails
from domain.estate.models.estate_house_model import EstateHouse
from domain.estate.models.estate_listing_model import EstateListing
from domain.estate.models.estate_location_model import EstateLocation
from domain.estate.models.estate_pricing_model import EstatePricing
from domain.estate.models.estate_utilities_model import EstateUtilities
from domain.estate.models.estate_vicinity_model import EstateVicinity
from domain.estate.models.saved_estate_model import SavedEstate
from exceptions.custom_exceptions.estate_exceptions import EstateNotFoundError
from schemas.estate_schemas.requests.estate_filter_request import (
    EstateAdminFilterRequest,
    EstatePublicFilterRequest,
    EstateSortBy,
    SortOrder,
)


class EstateRepository:
    def add(self, session: Session, estate: Estate) -> Estate:
        session.add(estate)
        session.flush()
        return estate

    def get_estate_full_by_id(
        self,
        session: Session,
        estate_id: UUID,
    ) -> Estate:
        stmt = (
            select(Estate)
            .where(Estate.id == estate_id)
            .options(*self._full_load_options())
        )

        estate = session.scalar(stmt)

        if estate is None:
            raise EstateNotFoundError()

        return estate

    def get_public_estates_by_filters(
        self,
        session: Session,
        filters: EstatePublicFilterRequest,
        current_user_id: UUID | None = None,
    ) -> tuple[list[Estate], int]:
        stmt = select(Estate)

        stmt = stmt.where(
            Estate.listing.has(EstateListing.status == ListingStatus.active)
        )

        stmt = self._apply_filters(
            stmt=stmt,
            filters=filters,
            current_user_id=current_user_id,
            is_admin=False,
        )

        total = self._count(session, stmt)

        stmt = (
            self._apply_sorting(stmt, filters)
            .offset((filters.page - 1) * filters.page_size)
            .limit(filters.page_size)
            .options(*self._list_load_options())
        )

        estates = list(session.scalars(stmt).unique())

        return estates, total

    def get_admin_estates_by_filters(
        self,
        session: Session,
        filters: EstateAdminFilterRequest,
        current_user_id: UUID | None = None,
    ) -> tuple[list[Estate], int]:
        stmt = select(Estate)

        stmt = self._apply_filters(
            stmt=stmt,
            filters=filters,
            current_user_id=current_user_id,
            is_admin=True,
        )

        total = self._count(session, stmt)

        stmt = (
            self._apply_sorting(stmt, filters)
            .offset((filters.page - 1) * filters.page_size)
            .limit(filters.page_size)
            .options(*self._list_load_options())
        )

        estates = list(session.scalars(stmt).unique())

        return estates, total

    def _apply_filters(
        self,
        stmt: Select,
        filters: EstatePublicFilterRequest | EstateAdminFilterRequest,
        current_user_id: UUID | None,
        is_admin: bool,
    ) -> Select:
        # Estate
        stmt = self._eq(stmt, Estate.agent_id, filters.agent_id)
        stmt = self._in(stmt, Estate.estate_type, filters.estate_type)
        stmt = self._in(stmt, Estate.offer_type, filters.offer_type)
        stmt = self._range(
            stmt,
            Estate.created_at,
            filters.created_at_from,
            filters.created_at_to,
        )

        if is_admin and isinstance(filters, EstateAdminFilterRequest):
            stmt = self._eq(stmt, Estate.seller_id, filters.seller_id)
            stmt = self._has_in(
                stmt,
                Estate.listing,
                EstateListing.status,
                filters.status,
            )

        # Saved by current user
        if filters.saved_by_current_user is not None:
            if current_user_id is None:
                if filters.saved_by_current_user is True:
                    stmt = stmt.where(false())

                return stmt

            exists_saved = (
                select(1)
                .where(
                    SavedEstate.estate_id == Estate.id,
                    SavedEstate.user_id == current_user_id,
                )
                .exists()
            )

            if filters.saved_by_current_user is True:
                stmt = stmt.where(exists_saved)
            else:
                stmt = stmt.where(~exists_saved)

        # Location
        stmt = self._has_in(
            stmt,
            Estate.location,
            EstateLocation.region,
            filters.region,
        )

        # Pricing
        stmt = self._has_range(
            stmt,
            Estate.pricing,
            EstatePricing.price,
            filters.price_from,
            filters.price_to,
        )
        stmt = self._has_in(
            stmt,
            Estate.pricing,
            EstatePricing.price_unit,
            filters.price_unit,
        )
        stmt = self._has_range(
            stmt,
            Estate.pricing,
            EstatePricing.cost_of_living,
            filters.cost_of_living_from,
            filters.cost_of_living_to,
        )
        stmt = self._has_eq(
            stmt,
            Estate.pricing,
            EstatePricing.commission_paid_by_owner,
            filters.commission_paid_by_owner,
        )

        # Listing
        stmt = self._has_range(
            stmt,
            Estate.listing,
            EstateListing.published_at,
            filters.published_at_from,
            filters.published_at_to,
        )
        stmt = self._has_range(
            stmt,
            Estate.listing,
            EstateListing.expires_at,
            filters.expires_at_from,
            filters.expires_at_to,
        )
        stmt = self._has_range(
            stmt,
            Estate.listing,
            EstateListing.available_from,
            filters.available_from_from,
            filters.available_from_to,
        )

        # Utilities
        stmt = self._has_eq(
            stmt,
            Estate.utilities,
            EstateUtilities.has_cold_water,
            filters.has_cold_water,
        )
        stmt = self._has_eq(
            stmt,
            Estate.utilities,
            EstateUtilities.has_hot_water,
            filters.has_hot_water,
        )
        stmt = self._has_eq(
            stmt,
            Estate.utilities,
            EstateUtilities.has_gas,
            filters.has_gas,
        )
        stmt = self._has_eq(
            stmt,
            Estate.utilities,
            EstateUtilities.has_sewerage,
            filters.has_sewerage,
        )
        stmt = self._has_in(
            stmt,
            Estate.utilities,
            EstateUtilities.heating_source,
            filters.heating_source,
        )
        stmt = self._has_in(
            stmt,
            Estate.utilities,
            EstateUtilities.primary_internet_connection_type,
            filters.primary_internet_connection_type,
        )

        # Details
        stmt = self._has_in(
            stmt,
            Estate.details,
            EstateDetails.condition,
            filters.condition,
        )
        stmt = self._has_in(
            stmt,
            Estate.details,
            EstateDetails.energy_class,
            filters.energy_class,
        )
        stmt = self._has_in(
            stmt,
            Estate.details,
            EstateDetails.furnishing,
            filters.furnishing,
        )
        stmt = self._has_eq(
            stmt,
            Estate.details,
            EstateDetails.easy_access,
            filters.easy_access,
        )
        stmt = self._has_range(
            stmt,
            Estate.details,
            EstateDetails.usable_area,
            filters.usable_area_from,
            filters.usable_area_to,
        )
        stmt = self._has_range(
            stmt,
            Estate.details,
            EstateDetails.total_property_area,
            filters.total_property_area_from,
            filters.total_property_area_to,
        )

        # Apartment
        stmt = self._has_in(
            stmt,
            Estate.apartment,
            EstateApartment.apartment_layout,
            filters.apartment_layout,
        )
        stmt = self._has_range(
            stmt,
            Estate.apartment,
            EstateApartment.floor_number,
            filters.floor_number_from,
            filters.floor_number_to,
        )
        stmt = self._has_eq(
            stmt,
            Estate.apartment,
            EstateApartment.has_elevator,
            filters.has_elevator,
        )

        stmt = self._has_presence(
            stmt,
            Estate.apartment,
            EstateApartment.balcony_area,
            filters.has_balcony,
        )
        stmt = self._has_range(
            stmt,
            Estate.apartment,
            EstateApartment.balcony_area,
            filters.balcony_area_from,
            filters.balcony_area_to,
        )

        stmt = self._has_presence(
            stmt,
            Estate.apartment,
            EstateApartment.loggia_area,
            filters.has_loggia,
        )
        stmt = self._has_range(
            stmt,
            Estate.apartment,
            EstateApartment.loggia_area,
            filters.loggia_area_from,
            filters.loggia_area_to,
        )

        stmt = self._has_presence(
            stmt,
            Estate.apartment,
            EstateApartment.terrace_area,
            filters.has_terrace,
        )
        stmt = self._has_range(
            stmt,
            Estate.apartment,
            EstateApartment.terrace_area,
            filters.terrace_area_from,
            filters.terrace_area_to,
        )

        # House
        stmt = self._has_in(
            stmt,
            Estate.house,
            EstateHouse.room_count,
            filters.room_count,
        )
        stmt = self._has_in(
            stmt,
            Estate.house,
            EstateHouse.house_type,
            filters.house_type,
        )
        stmt = self._has_range(
            stmt,
            Estate.house,
            EstateHouse.acceptance_year,
            filters.acceptance_year_from,
            filters.acceptance_year_to,
        )
        stmt = self._has_range(
            stmt,
            Estate.house,
            EstateHouse.floors,
            filters.floors_from,
            filters.floors_to,
        )

        stmt = self._has_presence(
            stmt,
            Estate.house,
            EstateHouse.garden_area,
            filters.has_garden,
        )
        stmt = self._has_range(
            stmt,
            Estate.house,
            EstateHouse.garden_area,
            filters.garden_area_from,
            filters.garden_area_to,
        )

        stmt = self._has_range(
            stmt,
            Estate.house,
            EstateHouse.building_area,
            filters.building_area_from,
            filters.building_area_to,
        )

        stmt = self._has_presence(
            stmt,
            Estate.house,
            EstateHouse.pool_area,
            filters.has_pool,
        )
        stmt = self._has_range(
            stmt,
            Estate.house,
            EstateHouse.pool_area,
            filters.pool_area_from,
            filters.pool_area_to,
        )

        stmt = self._has_presence(
            stmt,
            Estate.house,
            EstateHouse.cellar_area,
            filters.has_cellar,
        )
        stmt = self._has_range(
            stmt,
            Estate.house,
            EstateHouse.cellar_area,
            filters.cellar_area_from,
            filters.cellar_area_to,
        )

        stmt = self._has_presence(
            stmt,
            Estate.house,
            EstateHouse.garage_area,
            filters.has_garage,
        )
        stmt = self._has_range(
            stmt,
            Estate.house,
            EstateHouse.garage_area,
            filters.garage_area_from,
            filters.garage_area_to,
        )

        # Vicinities
        if filters.vicinity_type is not None:
            stmt = stmt.where(
                Estate.vicinities.any(
                    EstateVicinity.type.in_(filters.vicinity_type)
                )
            )

        if filters.vicinity_distance_m_to is not None:
            stmt = stmt.where(
                Estate.vicinities.any(
                    EstateVicinity.distance_m <= filters.vicinity_distance_m_to
                )
            )

        return stmt

    def _apply_sorting(
        self,
        stmt: Select,
        filters: EstatePublicFilterRequest | EstateAdminFilterRequest,
    ) -> Select:
        sort_column = self._get_sort_column(filters.sort_by)

        if filters.sort_by in {
            EstateSortBy.published_at,
            EstateSortBy.expires_at,
            EstateSortBy.available_from,
        }:
            stmt = stmt.join(Estate.listing)

        elif filters.sort_by == EstateSortBy.price:
            stmt = stmt.join(Estate.pricing)

        elif filters.sort_by in {
            EstateSortBy.usable_area,
            EstateSortBy.total_property_area,
        }:
            stmt = stmt.join(Estate.details)

        elif filters.sort_by == EstateSortBy.floor_number:
            stmt = stmt.outerjoin(Estate.apartment)

        elif filters.sort_by == EstateSortBy.acceptance_year:
            stmt = stmt.outerjoin(Estate.house)

        if filters.order == SortOrder.asc:
            order_expr = sort_column.asc().nulls_last()
        else:
            order_expr = sort_column.desc().nulls_last()

        return stmt.order_by(order_expr, Estate.id.asc())

    def _get_sort_column(self, sort_by: EstateSortBy):
        return {
            EstateSortBy.created_at: Estate.created_at,
            EstateSortBy.published_at: EstateListing.published_at,
            EstateSortBy.expires_at: EstateListing.expires_at,
            EstateSortBy.available_from: EstateListing.available_from,
            EstateSortBy.price: EstatePricing.price,
            EstateSortBy.usable_area: EstateDetails.usable_area,
            EstateSortBy.total_property_area: EstateDetails.total_property_area,
            EstateSortBy.floor_number: EstateApartment.floor_number,
            EstateSortBy.acceptance_year: EstateHouse.acceptance_year,
        }[sort_by]

    def _count(self, session: Session, stmt: Select) -> int:
        count_stmt = select(func.count()).select_from(
            stmt.order_by(None).subquery()
        )

        return session.scalar(count_stmt) or 0

    def _eq(self, stmt: Select, column, value) -> Select:
        if value is None:
            return stmt

        return stmt.where(column == value)

    def _in(self, stmt: Select, column, values) -> Select:
        if values is None:
            return stmt

        return stmt.where(column.in_(values))

    def _range(self, stmt: Select, column, value_from, value_to) -> Select:
        if value_from is not None:
            stmt = stmt.where(column >= value_from)

        if value_to is not None:
            stmt = stmt.where(column <= value_to)

        return stmt

    def _has_eq(self, stmt: Select, relationship, column, value) -> Select:
        if value is None:
            return stmt

        return stmt.where(relationship.has(column == value))

    def _has_in(self, stmt: Select, relationship, column, values) -> Select:
        if values is None:
            return stmt

        return stmt.where(relationship.has(column.in_(values)))

    def _has_range(
        self,
        stmt: Select,
        relationship,
        column,
        value_from,
        value_to,
    ) -> Select:
        conditions = []

        if value_from is not None:
            conditions.append(column >= value_from)

        if value_to is not None:
            conditions.append(column <= value_to)

        if not conditions:
            return stmt

        return stmt.where(relationship.has(*conditions))

    def _has_presence(
        self,
        stmt: Select,
        relationship,
        column,
        value: bool | None,
    ) -> Select:
        if value is None:
            return stmt

        if value is True:
            return stmt.where(relationship.has(column.is_not(None)))

        return stmt.where(relationship.has(column.is_(None)))

    def _list_load_options(self):
        return (
            joinedload(Estate.location),
            joinedload(Estate.pricing),
            joinedload(Estate.listing),
            joinedload(Estate.details),
            joinedload(Estate.apartment),
            joinedload(Estate.house),
            selectinload(Estate.media),
        )

    def _full_load_options(self):
        return (
            joinedload(Estate.seller),
            joinedload(Estate.agent),
            joinedload(Estate.location),
            joinedload(Estate.pricing),
            joinedload(Estate.listing),
            joinedload(Estate.utilities),
            joinedload(Estate.details),
            joinedload(Estate.apartment),
            joinedload(Estate.house),
            selectinload(Estate.translations),
            selectinload(Estate.media),
            selectinload(Estate.vicinities),
        )
