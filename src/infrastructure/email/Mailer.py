import os

import resend
from jinja2 import Environment, FileSystemLoader, select_autoescape


class Mailer:
    FROM_EMAIL = "noreply@valpriad.online"

    def __init__(self) -> None:
        resend.api_key = os.getenv("RESEND_API_KEY")

        templates_dir = os.path.join(
            os.path.dirname(__file__), "templates", "html"
        )

        self.env = Environment(
            loader=FileSystemLoader(templates_dir),
            autoescape=select_autoescape(["html"]),
        )

    def send_verification_email(self, email_to: str, token: str) -> None:
        verification_url = f"{os.getenv('APP_BASE_URL')}/verify?token={token}"

        template = self.env.get_template("email_verification.html")
        html = template.render(verification_url=verification_url)

        params = {
            "from": self.FROM_EMAIL,
            "to": [email_to],
            "subject": "AtHome: Verify your email!",
            "html": html,
            "text": (
                "Welcome to our website,\n"
                "Verify your email by following the link:\n"
                f"{verification_url}"
            ),
        }

        resend.Emails.send(params)  # type: ignore

    def send_reset_password_email(self, email_to: str, token: str) -> None:
        reset_password_url = (
            f"{os.getenv('APP_BASE_URL')}/reset-password?token={token}"
        )

        template = self.env.get_template("password_reset.html")
        html = template.render(verification_url=reset_password_url)

        params = {
            "from": self.FROM_EMAIL,
            "to": [email_to],
            "subject": "AtHome: Reset your password!",
            "html": html,
            "text": (
                "Reset your password by following the link:\n"
                f"{reset_password_url}"
            ),
        }

        resend.Emails.send(params)  # type: ignore

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
        template = self.env.get_template("agent_contact.html")

        html = template.render(
            estate_title=estate_title,
            estate_address=estate_address,
            estate_url=estate_url,
            sender_name=sender_name,
            sender_email=sender_email,
            sender_phone=sender_phone,
            message=message,
        )

        text = (
            "New message about your estate\n\n"
            f"Estate: {estate_title}\n"
            f"Address: {estate_address}\n"
            f"Estate page: {estate_url}\n\n"
            "Sender:\n"
            f"Name: {sender_name}\n"
            f"Email: {sender_email}\n"
            f"Phone: {sender_phone}\n\n"
            "Message:\n"
            f"{message}"
        )

        params = {
            "from": self.FROM_EMAIL,
            "to": [agent_email],
            "reply_to": sender_email,
            "subject": f"AtHome: New message about {estate_title}",
            "html": html,
            "text": text,
        }

        resend.Emails.send(params)  # type: ignore
