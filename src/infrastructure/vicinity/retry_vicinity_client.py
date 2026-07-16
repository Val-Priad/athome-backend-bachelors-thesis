import logging
import time

from application.ports.vicinity_client import (
    VicinityClientProtocol,
    VicinityFetchResult,
)

_logger = logging.getLogger(__name__)


class RetryingVicinityClient:
    def __init__(
        self,
        client: VicinityClientProtocol,
        *,
        attempts: int = 3,
        delay_seconds: float = 0.5,
    ):
        self.client = client
        self.attempts = attempts
        self.delay_seconds = delay_seconds

    def fetch_vicinity(
        self,
        lat: float,
        lon: float,
        radius: int = 10000,
    ) -> VicinityFetchResult:
        last_result: VicinityFetchResult | None = None

        for attempt in range(1, self.attempts + 1):
            result = self.client.fetch_vicinity(lat, lon, radius)

            if result.ok:
                return result

            last_result = result

            _logger.warning(
                "Failed to fetch vicinity data. Attempt %s/%s. Reason: %s",
                attempt,
                self.attempts,
                result.message,
            )

            if attempt < self.attempts:
                time.sleep(self.delay_seconds)

        return VicinityFetchResult(
            ok=False,
            message=(
                last_result.message
                if last_result is not None
                else "Failed to fetch vicinity data"
            ),
        )
