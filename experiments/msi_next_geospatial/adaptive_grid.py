"""Zoom-adaptive interaction grid whose output is geographic geometry.

Grid cells quantify human intent; their screen identifiers are never exported as
mission truth. The selection survives zoom changes as latitude/longitude polygons.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from math import cos, floor, radians


@dataclass(frozen=True)
class GeographicPoint:
    latitude: float
    longitude: float


@dataclass(frozen=True)
class GridCell:
    row: int
    column: int
    size_m: float
    polygon: tuple[GeographicPoint, ...]


@dataclass
class SpatialSelection:
    """Renderer-independent geographic selection, potentially multi-resolution."""

    polygons: dict[tuple[float, int, int], tuple[GeographicPoint, ...]] = field(default_factory=dict)

    def paint(self, cell: GridCell) -> None:
        self.polygons[(cell.size_m, cell.row, cell.column)] = cell.polygon

    def erase(self, cell: GridCell) -> None:
        self.polygons.pop((cell.size_m, cell.row, cell.column), None)

    def clear(self) -> None:
        self.polygons.clear()

    def to_geojson(self) -> dict[str, object]:
        coordinates = []
        for polygon in self.polygons.values():
            ring = [[point.longitude, point.latitude] for point in polygon]
            if ring and ring[0] != ring[-1]:
                ring.append(ring[0])
            coordinates.append([ring])
        return {"type": "MultiPolygon", "coordinates": coordinates}


class AdaptiveGrid:
    """Converts zoom and geographic points into stable metric grid footprints."""

    @staticmethod
    def resolution_m(zoom: float) -> float:
        if zoom < 12:
            return 500.0
        if zoom < 14:
            return 200.0
        if zoom < 16:
            return 50.0
        if zoom < 18:
            return 20.0
        return 5.0

    @staticmethod
    def cell_at(point: GeographicPoint, zoom: float) -> GridCell:
        size_m = AdaptiveGrid.resolution_m(zoom)
        meters_per_latitude_degree = 111_320.0
        meters_per_longitude_degree = meters_per_latitude_degree * cos(radians(point.latitude))
        row = floor(point.latitude * meters_per_latitude_degree / size_m)
        column = floor(point.longitude * meters_per_longitude_degree / size_m)
        south = row * size_m / meters_per_latitude_degree
        north = (row + 1) * size_m / meters_per_latitude_degree
        west = column * size_m / meters_per_longitude_degree
        east = (column + 1) * size_m / meters_per_longitude_degree
        return GridCell(
            row=row,
            column=column,
            size_m=size_m,
            polygon=(
                GeographicPoint(south, west),
                GeographicPoint(south, east),
                GeographicPoint(north, east),
                GeographicPoint(north, west),
            ),
        )
