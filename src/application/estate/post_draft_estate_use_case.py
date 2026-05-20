from uuid import UUID

from schemas.estate_schemas.draft_request import EstateDraftRequest


class PostDraftEstateUseCase:
    def __init__(self, estate_service):
        self.estate_service = estate_service

    def execute(self, data: EstateDraftRequest, requester_id: UUID): ...
