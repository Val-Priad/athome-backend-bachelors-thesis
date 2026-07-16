from uuid import UUID

from application.transactions import TransactionManagerProtocol
from domain.user.services.auth_service import AuthService


class LoginUserUseCase:
    def __init__(
        self,
        transactions: TransactionManagerProtocol,
        auth_service: AuthService,
    ) -> None:
        self._transactions = transactions
        self._auth_service = auth_service

    def execute(self, email: str, password: str) -> UUID:
        with self._transactions.session() as session:
            user = self._auth_service.verify_password(session, email, password)
            return user.id
