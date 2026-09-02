"""Intención, plan, preflight y trazabilidad de una misión MSI."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from uuid import uuid4

from .geography import GeoPoint, GeoPolygon


class MissionIntent(str, Enum):
    PRECISION_SPRAYING = "precision_spraying"
    AUTONOMOUS_PATROL = "autonomous_patrol"
    EMERGENCY_RESPONSE = "emergency_response"


class PreflightStatus(str, Enum):
    READY = "ready"
    BLOCKED = "blocked"
    REQUIRES_DATA = "requires_data"


@dataclass(frozen=True)
class MissionConfiguration:
    intent: MissionIntent
    name: str
    operational_area: GeoPolygon
    geofence: GeoPolygon
    parameters: dict[str, object]
    mission_id: str = field(default_factory=lambda: uuid4().hex[:12])


@dataclass
class MissionTask:
    task_id: str
    task_type: str
    required_capabilities: set[str]
    route: list[GeoPoint]
    assigned_resource_id: str | None = None
    sector: str = ""
    progress_percent: float = 0.0
    status: str = "planned"


@dataclass
class MissionPlan:
    mission_id: str
    tasks: list[MissionTask]
    estimated_duration_minutes: float
    estimated_consumption_l: float = 0.0
    coverage_hectares: float = 0.0
    version: int = 1
    rationale: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class PreflightFinding:
    code: str
    severity: str
    summary: str
    detail: str


@dataclass
class PreflightResult:
    status: PreflightStatus
    findings: list[PreflightFinding]
    checked_at: str = field(default_factory=lambda: datetime.now().isoformat(timespec="seconds"))


@dataclass(frozen=True)
class OperationalEvent:
    event_type: str
    summary: str
    resource_id: str | None = None
    data: dict[str, object] = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat(timespec="seconds"))


@dataclass(frozen=True)
class DecisionRecord:
    trigger: str
    evaluation: str
    alternatives: tuple[str, ...]
    selected_action: str
    reason: str
    impact: str
    commands: tuple[str, ...] = ()
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat(timespec="seconds"))
