from pydantic import ConfigDict

from schemas.parent_types import ResponseValidation
from schemas.types import ID


class EstateCreateResponse(ResponseValidation):
    id: ID

    model_config = ConfigDict(from_attributes=True)
