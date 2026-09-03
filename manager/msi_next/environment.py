"""Minimal persistent environment knowledge with explicit evidence quality."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any


class PersistenceClass(str, Enum):
    PERSISTENT = "persistent"
    SEMIPERSISTENT = "semipersistent"
    DYNAMIC = "dynamic"


@dataclass(frozen=True)
class Evidence:
    source: str
    observed_at: str
    confidence: float
    freshness_seconds: float | None = None
    accuracy_m: float | None = None

    def __post_init__(self) -> None:
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("confidence must be between 0 and 1")


@dataclass(frozen=True)
class EnvironmentFeature:
    feature_id: str
    kind: str
    geometry: dict[str, Any]
    persistence: PersistenceClass
    evidence: Evidence
    properties: dict[str, Any] = field(default_factory=dict)


@dataclass
class EnvironmentModel:
    environment_id: str
    name: str
    coordinate_reference_system: str = "EPSG:4326"
    features: dict[str, EnvironmentFeature] = field(default_factory=dict)

    def upsert(self, feature: EnvironmentFeature) -> None:
        self.features[feature.feature_id] = feature

    def remove_dynamic(self) -> None:
        self.features = {
            key: feature for key, feature in self.features.items()
            if feature.persistence is not PersistenceClass.DYNAMIC
        }

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": 1,
            "environment_id": self.environment_id,
            "name": self.name,
            "coordinate_reference_system": self.coordinate_reference_system,
            "features": [
                {
                    **asdict(feature),
                    "persistence": feature.persistence.value,
                }
                for feature in self.features.values()
            ],
        }


class JsonEnvironmentRepository:
    """Prototype repository; persistence is outside Mission Runtime."""

    def __init__(self, directory: Path) -> None:
        self.directory = directory

    def save(self, model: EnvironmentModel) -> Path:
        self.directory.mkdir(parents=True, exist_ok=True)
        path = self.directory / f"{model.environment_id}.json"
        path.write_text(json.dumps(model.to_dict(), ensure_ascii=False, indent=2), encoding="utf-8")
        return path
