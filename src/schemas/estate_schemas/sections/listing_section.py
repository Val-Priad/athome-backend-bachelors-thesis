from datetime import date


from schemas.parent_types import RequestValidation


class EstateListingSection(RequestValidation):
    available_from: date
