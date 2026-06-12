from dataclasses import dataclass
from typing import Protocol

from domain.estate.enums.estate_vicinity_enums import VicinityType


class VicinityClientProtocol(Protocol):
    def fetch_vicinity(
        self,
        lat: float,
        lon: float,
        radius: int = 10000,
    ) -> "VicinityFetchResult": ...


@dataclass(frozen=True)
class Place:
    type: VicinityType
    name: str
    latitude: float
    longitude: float
    id: int
    distance_m: int


@dataclass(frozen=True)
class VicinityFetchResult:
    ok: bool
    data: dict[VicinityType, list[Place]] | None = None
    message: str | None = None
