class FakeMailer:
    def __init__(self) -> None:
        self.verification_emails: list[tuple[str, str]] = []
        self.reset_emails: list[tuple[str, str]] = []
        self.sent_estate_contact_emails: list[dict[str, str]] = []

    def reset(self) -> None:
        self.verification_emails.clear()
        self.reset_emails.clear()
        self.sent_estate_contact_emails.clear()

    def send_verification_email(self, email_to: str, token: str) -> None:
        self.verification_emails.append((email_to, token))

    def send_reset_password_email(self, email_to: str, token: str) -> None:
        self.reset_emails.append((email_to, token))

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
    ) -> None:
        self.sent_estate_contact_emails.append(
            {
                "agent_email": agent_email,
                "estate_title": estate_title,
                "estate_url": estate_url,
                "estate_address": estate_address,
                "sender_name": sender_name,
                "sender_email": sender_email,
                "sender_phone": sender_phone,
                "message": message,
            }
        )
