from typing import Protocol

import resend


class EmailClientProtocol(Protocol):
    def send(self, payload: dict[str, object]) -> None: ...


class ResendClient:
    def __init__(self, api_key: str) -> None:
        self._api_key = api_key

    def send(self, payload: dict[str, object]) -> None:
        resend.api_key = self._api_key
        resend.Emails.send(payload)  # type: ignore[arg-type]
