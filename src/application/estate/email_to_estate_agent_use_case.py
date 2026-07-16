from application.transactions import TransactionManagerProtocol
from domain.estate.estate_model import Estate
from domain.estate.estate_repository import EstateRepository
from exceptions.custom_exceptions.user_exceptions import AgentNotFoundError
from infrastructure.email.mailer_protocol import MailerProtocol
from schemas.estate_schemas.requests.email_to_agent_request import (
    EmailToAgentRequest,
)


class EmailToAgentUseCase:
    def __init__(
        self,
        transactions: TransactionManagerProtocol,
        estate_repository: EstateRepository,
        mailer: MailerProtocol,
        app_base_url: str,
    ) -> None:
        self._transactions = transactions
        self._estate_repository = estate_repository
        self._mailer = mailer
        self._app_base_url = app_base_url.rstrip("/")

    def execute(self, estate_id, payload: EmailToAgentRequest) -> None:
        with self._transactions.session() as session:
            estate = self._estate_repository.get_full_estate_by_id(
                session, estate_id
            )

            if estate.agent is None:
                raise AgentNotFoundError()

            estate_url = f"{self._app_base_url}/estate/{estate.id}"

            estate_translation = self._get_english_translation(estate)

            agent_email = estate.agent.email
            estate_title = estate_translation.title
            estate_address = self._get_estate_address(estate)

        self._mailer.send_estate_contact_email(
            agent_email=agent_email,
            estate_title=estate_title,
            estate_url=estate_url,
            estate_address=estate_address,
            sender_name=payload.sender_name,
            sender_email=payload.sender_email,
            sender_phone=payload.sender_phone,
            message=payload.message,
        )

    def _get_english_translation(self, estate: Estate):
        for translation in estate.translations:
            if translation.lang_code == "en":
                return translation

        return estate.translations[0]

    def _get_estate_address(self, estate: Estate) -> str:
        location = estate.location

        parts = [
            location.city,
            location.street,
            location.house_number,
        ]

        return ", ".join(part for part in parts if part)
