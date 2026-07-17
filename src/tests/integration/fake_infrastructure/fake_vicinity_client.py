from application.ports import VicinityFetchResult
from application.ports.vicinity_client import Place
from domain.estate.enums.estate_vicinity_enums import VicinityType


class FakeVicinityClient:
    def fetch_vicinity(self, lat, lon, radius=10000):
        return VicinityFetchResult(
            ok=True,
            data={
                VicinityType.bus_stop: [
                    Place(
                        type=VicinityType.bus_stop,
                        name="Test bus stop",
                        latitude=lat + 0.001,
                        longitude=lon + 0.001,
                        id=1,
                        distance_m=157,
                    )
                ],
                VicinityType.closest: [
                    Place(
                        type=VicinityType.bus_stop,
                        name="Test bus stop",
                        latitude=lat + 0.001,
                        longitude=lon + 0.001,
                        id=1,
                        distance_m=157,
                    )
                ],
            },
        )
