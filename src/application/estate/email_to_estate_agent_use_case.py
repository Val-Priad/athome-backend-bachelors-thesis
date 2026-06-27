import os

from domain.estate.estate_model import Estate
from domain.estate.estate_repository import EstateRepository
from exceptions.custom_exceptions.user_exceptions import AgentNotFoundError
from infrastructure.db import db_session
from infrastructure.email.mailer_protocol import MailerProtocol
from schemas.estate_schemas.requests.email_to_agent_request import (
    EmailToAgentRequest,
)


class EmailToAgentUseCase:
    def __init__(
        self, estate_repository: EstateRepository, mailer: MailerProtocol
    ) -> None:
        self.estate_repository = estate_repository
        self.mailer = mailer

    def execute(self, estate_id, payload: EmailToAgentRequest) -> None:
        frontend_base_url = os.getenv("FRONTEND_BASE_URL", "")
        with db_session() as session:
            estate = self.estate_repository.get_full_estate_by_id(
                session, estate_id
            )

            if estate.agent is None:
                raise AgentNotFoundError()

            estate_url = f"{frontend_base_url}/estate/{estate.id}"

            estate_translation = self.get_english_translation(estate)

            self.mailer.send_estate_contact_email(
                agent_email=estate.agent.email,
                estate_title=estate_translation.title,
                estate_url=estate_url,
                estate_address=self.get_estate_address(estate),
                sender_name=payload.sender_name,
                sender_email=payload.sender_email,
                sender_phone=payload.sender_phone,
                message=payload.message,
            )

    def get_english_translation(self, estate: Estate):
        for translation in estate.translations:
            if translation.lang_code == "en":
                return translation

        return estate.translations[0]

    def get_estate_address(self, estate: Estate) -> str:
        location = estate.location

        parts = [
            location.city,
            location.street,
            location.house_number,
        ]

        return ", ".join(part for part in parts if part)
