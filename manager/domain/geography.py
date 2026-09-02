"""Coordenadas y geometría operacional con semántica de altitud explícita."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class AltitudeReference(str, Enum):
    MSL = "msl"
    AGL = "agl"
    ABOVE_CANOPY = "above_canopy"


@dataclass(frozen=True)
class Altitude:
    meters: float
    reference: AltitudeReference
    uncertainty_m: float = 0.5


@dataclass(frozen=True)
class GeoPoint:
    latitude: float
    longitude: float
    altitude: Altitude
    horizontal_accuracy_m: float = 1.5

    def __post_init__(self) -> None:
        if not -90 <= self.latitude <= 90:
            raise ValueError("latitude must be between -90 and 90")
        if not -180 <= self.longitude <= 180:
            raise ValueError("longitude must be between -180 and 180")


@dataclass(frozen=True)
class GeoPolygon:
    vertices: tuple[GeoPoint, ...]

    def __post_init__(self) -> None:
        if len(self.vertices) < 3:
            raise ValueError("a polygon requires at least three vertices")


@dataclass(frozen=True)
class MapBounds:
    south: float
    west: float
    north: float
    east: float

    def to_normalized(self, point: GeoPoint) -> tuple[float, float]:
        longitude_span = self.east - self.west
        latitude_span = self.north - self.south
        if longitude_span <= 0 or latitude_span <= 0:
            raise ValueError("invalid map bounds")
        x = (point.longitude - self.west) / longitude_span
        y = (self.north - point.latitude) / latitude_span
        return x, y

    def from_normalized(
        self,
        x: float,
        y: float,
        altitude: Altitude,
    ) -> GeoPoint:
        return GeoPoint(
            latitude=self.north - y * (self.north - self.south),
            longitude=self.west + x * (self.east - self.west),
            altitude=altitude,
        )
