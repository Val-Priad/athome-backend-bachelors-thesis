import json
import logging
import math
from dataclasses import dataclass
from typing import Any
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from application.ports.vicinity_client import Place, VicinityFetchResult
from domain.estate.enums.estate_vicinity_enums import VicinityType

_logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class VicinityDefinition:
    osm_key: str
    osm_value: str
    type: VicinityType
    label: str


VICINITY_TYPES: tuple[VicinityDefinition, ...] = (
    VicinityDefinition(
        "highway", "bus_stop", VicinityType.bus_stop, "Bus stop"
    ),
    VicinityDefinition(
        "amenity", "post_office", VicinityType.post_office, "Post office"
    ),
    VicinityDefinition("amenity", "atm", VicinityType.atm, "ATM"),
    VicinityDefinition(
        "amenity",
        "restaurant",
        VicinityType.restaurant_pub,
        "Restaurant / Pub",
    ),
    VicinityDefinition("amenity", "school", VicinityType.school, "School"),
    VicinityDefinition(
        "amenity", "kindergarten", VicinityType.kindergarten, "Kindergarten"
    ),
    VicinityDefinition("amenity", "clinic", VicinityType.clinic, "Clinic"),
    VicinityDefinition(
        "amenity", "veterinary", VicinityType.veterinarian, "Veterinarian"
    ),
    VicinityDefinition(
        "shop", "supermarket", VicinityType.supermarket, "Supermarket"
    ),
    VicinityDefinition(
        "shop", "convenience", VicinityType.small_shop, "Small shop"
    ),
    VicinityDefinition(
        "leisure",
        "playground",
        VicinityType.playground,
        "Children's playground",
    ),
    VicinityDefinition(
        "railway", "station", VicinityType.train_station, "Train station"
    ),
    VicinityDefinition(
        "railway", "subway_entrance", VicinityType.metro, "Metro"
    ),
)


class OpenStreetMapVicinityClient:
    def __init__(
        self,
        *,
        api_url: str = "https://overpass-api.de/api/interpreter",
        timeout: float = 5.0,
    ):
        self.api_url = api_url
        self.timeout = timeout

    def fetch_vicinity(
        self,
        lat: float,
        lon: float,
        radius: int = 10000,
    ) -> VicinityFetchResult:
        try:
            self._validate_coordinates(lat, lon, radius)
            overpass_query = self._build_overpass_query(lat, lon, radius)
            payload = self._execute_query(overpass_query)
            places = self._map_response(payload, lat, lon)

            grouped_places = self._sort_groups(self._group_places(places))
            closest_places = self._get_closest_places_from_each_group(
                grouped_places
            )

            grouped_places[VicinityType.closest] = closest_places
            return VicinityFetchResult(ok=True, data=grouped_places)
        except (
            ValueError,
            OSError,
            RuntimeError,
        ) as error:
            _logger.warning(
                "Failed to fetch vicinity data from Overpass: %s", error
            )
            return VicinityFetchResult(ok=False, message=str(error))
        except Exception as error:
            _logger.exception("Unexpected error while fetching vicinity data")
            return VicinityFetchResult(ok=False, message=str(error))

    @staticmethod
    def _validate_coordinates(lat: float, lon: float, radius: int) -> None:
        if lat is None or lon is None:
            raise ValueError("Latitude and longitude are required.")

        if not -90 <= lat <= 90:
            raise ValueError("Latitude must be between -90 and 90.")

        if not -180 <= lon <= 180:
            raise ValueError("Longitude must be between -180 and 180.")

        if radius is None or radius <= 0:
            raise ValueError("Radius must be greater than zero.")

    def _build_overpass_query(
        self, lat: float, lon: float, radius: int
    ) -> str:
        queries = "\n".join(
            (
                f"node[{definition.osm_key}={definition.osm_value}]"
                f"(around:{radius},{lat},{lon});"
            )
            for definition in VICINITY_TYPES
        )

        return f"""
[out:json];
(
  {queries}
);
out body;
""".strip()

    def _execute_query(self, overpass_query: str) -> dict[str, Any]:
        request = Request(
            self.api_url,
            data=urlencode({"data": overpass_query}).encode("utf-8"),
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            method="POST",
        )

        with urlopen(request, timeout=self.timeout) as response:
            if response.status != 200:
                raise RuntimeError(
                    f"Overpass API returned an error: {response.status} {response.reason}"
                )

            return json.loads(response.read().decode("utf-8"))

    def _map_response(
        self,
        payload: dict[str, Any],
        lat: float,
        lon: float,
    ) -> list[Place]:
        elements = payload.get("elements", [])
        mapped_places: list[Place] = []

        for element in elements:
            tags = element.get("tags", {})
            definition = self._find_definition(tags)
            if definition is None:
                continue

            element_lat = element.get("lat")
            element_lon = element.get("lon")
            if element_lat is None or element_lon is None:
                continue

            mapped_places.append(
                Place(
                    type=definition.type,
                    name=tags.get("name", "").strip() or definition.label,
                    latitude=float(element_lat),
                    longitude=float(element_lon),
                    id=int(element.get("id", 0)),
                    distance_m=int(
                        round(
                            self._haversine_distance(
                                lat,
                                lon,
                                float(element_lat),
                                float(element_lon),
                            )
                        )
                    ),
                )
            )

        return mapped_places

    @staticmethod
    def _find_definition(tags: dict[str, str]) -> VicinityDefinition | None:
        for definition in VICINITY_TYPES:
            if tags.get(definition.osm_key) == definition.osm_value:
                return definition

        return None

    @staticmethod
    def _group_places(places: list[Place]) -> dict[VicinityType, list[Place]]:
        grouped_places: dict[VicinityType, list[Place]] = {}
        for place in places:
            grouped_places.setdefault(place.type, []).append(place)

        return grouped_places

    @staticmethod
    def _sort_groups(
        groups: dict[VicinityType, list[Place]],
    ) -> dict[VicinityType, list[Place]]:
        return {
            vicinity_type: sorted(places, key=lambda place: place.distance_m)
            for vicinity_type, places in groups.items()
        }

    @staticmethod
    def _get_closest_places_from_each_group(
        groups: dict[VicinityType, list[Place]],
    ) -> list[Place]:
        return [
            places[0]
            for vicinity_type, places in groups.items()
            if vicinity_type != VicinityType.closest and places
        ]

    @staticmethod
    def _haversine_distance(
        lat1: float,
        lon1: float,
        lat2: float,
        lon2: float,
    ) -> float:
        earth_radius_m = 6_371_000
        lat1_rad = math.radians(lat1)
        lon1_rad = math.radians(lon1)
        lat2_rad = math.radians(lat2)
        lon2_rad = math.radians(lon2)

        delta_lat = lat2_rad - lat1_rad
        delta_lon = lon2_rad - lon1_rad

        a = (
            math.sin(delta_lat / 2) ** 2
            + math.cos(lat1_rad)
            * math.cos(lat2_rad)
            * math.sin(delta_lon / 2) ** 2
        )
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        return earth_radius_m * c
