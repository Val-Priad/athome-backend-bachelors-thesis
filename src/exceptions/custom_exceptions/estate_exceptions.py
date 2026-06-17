from exceptions.error_catalog import DomainError, register_custom_error


class EstateNotFoundError(DomainError):
    pass


def register_estate_errors():
    register_custom_error(
        EstateNotFoundError, "estate_not_found", 404, "Estate not found"
    )
