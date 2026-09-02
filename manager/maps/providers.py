"""Contrato cartográfico separado del renderer y del modelo de misión."""

from __future__ import annotations

from typing import Protocol

from domain.geography import GeoPoint, MapBounds


class MapProvider(Protocol):
    provider_id: str
    bounds: MapBounds

    def world_to_map(self, point: GeoPoint) -> tuple[float, float]: ...
    def descriptor(self) -> dict[str, object]: ...


class LocalMapProvider:
    """Mapa local sin red ni costo; no pretende ser cartografía certificada."""

    provider_id = "local_demo_map"

    def __init__(self, bounds: MapBounds, label: str = "Las Marías") -> None:
        self.bounds = bounds
        self.label = label

    def world_to_map(self, point: GeoPoint) -> tuple[float, float]:
        return self.bounds.to_normalized(point)

    def descriptor(self) -> dict[str, object]:
        return {
            "provider_id": self.provider_id,
            "label": self.label,
            "cartography_status": "demo_local_not_certified",
        }
