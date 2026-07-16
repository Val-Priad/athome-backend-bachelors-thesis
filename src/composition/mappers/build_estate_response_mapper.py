from application.estate.mapping.estate_response_mapper import (
    EstateResponseMapper,
)
from application.estate.mapping.media_url_builder import MediaUrlBuilder
from composition.infrastructure.infrastructure_container import (
    InfrastructureContainer,
)


def build_estate_response_mapper(
    infrastructure: InfrastructureContainer,
) -> EstateResponseMapper:
    return EstateResponseMapper(
        media_url_builder=MediaUrlBuilder(
            infrastructure.urls.media_base_url,
        ),
    )
