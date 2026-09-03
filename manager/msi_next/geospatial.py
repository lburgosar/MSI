"""Provider-neutral geospatial contracts for MSI Next."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Protocol


class BasemapKind(str, Enum):
    MAP = "map"
    SATELLITE = "satellite"
    HYBRID = "hybrid"
    ORTHOMOSAIC = "orthomosaic"
    CUSTOM_GIS = "custom_gis"
    DIGITAL_TWIN = "digital_twin"


class SourceMode(str, Enum):
    ONLINE = "online"
    OFFLINE = "offline"
    LOCAL = "local"


class LayerKind(str, Enum):
    BASEMAP = "basemap"
    ENVIRONMENT = "environment"
    OPERATOR_SELECTION = "operator_selection"
    MSI_INTERPRETATION = "msi_interpretation"
    VERIFIED_GEOMETRY = "verified_geometry"
    RESTRICTION = "restriction"
    WORK_STATE = "work_state"
    RESOURCE = "resource"
    OBSERVATION = "observation"
    ENGINEERING_ROUTE = "engineering_route"


@dataclass(frozen=True)
class BasemapDescriptor:
    provider_id: str
    label: str
    kind: BasemapKind
    source_mode: SourceMode
    attribution: str
    minimum_zoom: float
    maximum_zoom: float
    supports_touch: bool = True

    def __post_init__(self) -> None:
        if self.minimum_zoom > self.maximum_zoom:
            raise ValueError("minimum_zoom must not exceed maximum_zoom")
        if not self.attribution.strip():
            raise ValueError("basemap attribution must be explicit")


class BasemapProvider(Protocol):
    def descriptor(self) -> BasemapDescriptor: ...


@dataclass(frozen=True)
class SpatialIntent:
    """What/where requested by a human, explicitly not a flight route."""

    intent: str
    geometry: dict[str, Any]
    coordinate_reference_system: str = "EPSG:4326"
    interaction_resolution_m: float | None = None
    source: str = "operator"

    def __post_init__(self) -> None:
        if self.geometry.get("type") not in {
            "Point", "LineString", "Polygon", "MultiPolygon"
        }:
            raise ValueError("unsupported spatial-intent geometry")
        if "coordinates" not in self.geometry:
            raise ValueError("spatial intent requires coordinates")

