from typing import Protocol


class MailerProtocol(Protocol):
    def send_verification_email(self, email_to: str, token: str): ...

    def send_reset_password_email(self, email_to: str, token: str): ...
