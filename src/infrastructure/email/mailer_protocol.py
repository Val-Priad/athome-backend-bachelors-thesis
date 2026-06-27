from typing import Protocol


class MailerProtocol(Protocol):
    def send_verification_email(self, email_to: str, token: str) -> None: ...

    def send_reset_password_email(self, email_to: str, token: str) -> None: ...

    def send_estate_contact_email(
        self,
        agent_email: str,
        estate_title: str,
        estate_url: str,
        estate_address: str,
        sender_name: str,
        sender_email: str,
        sender_phone: str,
        message: str,
    ) -> None: ...
