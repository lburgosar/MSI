"""Perception observations report evidence; they never decide a mission."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from .environment import Evidence


class ObservationKind(str, Enum):
    OBSTACLE = "obstacle"
    PERSON = "person"
    VEHICLE = "vehicle"
    ANIMAL = "animal"
    THERMAL_ANOMALY = "thermal_anomaly"
    CROP_ANOMALY = "crop_anomaly"
    TERRAIN_CHANGE = "terrain_change"
    UNKNOWN_OBJECT = "unknown_object"


@dataclass(frozen=True)
class Observation:
    observation_id: str
    kind: ObservationKind
    geometry: dict[str, Any]
    evidence: Evidence
    resource_id: str | None = None
    attributes: dict[str, Any] = field(default_factory=dict)

