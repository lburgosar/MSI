"""Modelo extensible de recursos físicos o simulados gobernados por MSI."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

from .geography import GeoPoint


class ResourceType(str, Enum):
    AERIAL = "aerial"
    GROUND = "ground"
    WEATHER_STATION = "weather_station"
    COMMUNICATION_RELAY = "communication_relay"
    INFRASTRUCTURE = "infrastructure"


class Availability(str, Enum):
    AVAILABLE = "available"
    ASSIGNED = "assigned"
    ACTIVE = "active"
    DISABLED = "disabled"
    WITHDRAWN = "withdrawn"


class Health(str, Enum):
    NOMINAL = "nominal"
    DEGRADED = "degraded"
    FAILED = "failed"


@dataclass
class EnergyState:
    percent: float
    capacity_wh: float
    reserve_percent: float = 20.0


@dataclass
class ConsumableState:
    kind: str
    remaining_l: float
    capacity_l: float

    @property
    def percent(self) -> float:
        return 0.0 if self.capacity_l <= 0 else self.remaining_l / self.capacity_l * 100.0


@dataclass
class CommunicationState:
    link_quality_percent: float = 100.0
    latency_ms: float = 25.0
    connected: bool = True


@dataclass(frozen=True)
class Sensor:
    sensor_id: str
    sensor_type: str
    operational: bool = True
    data_kind: str = "telemetry"


@dataclass
class Resource:
    resource_id: str
    display_name: str
    resource_type: ResourceType
    position: GeoPoint
    capabilities: set[str] = field(default_factory=set)
    sensors: list[Sensor] = field(default_factory=list)
    payloads: set[str] = field(default_factory=set)
    energy: EnergyState = field(default_factory=lambda: EnergyState(100.0, 500.0))
    consumable: ConsumableState | None = None
    communication: CommunicationState = field(default_factory=CommunicationState)
    availability: Availability = Availability.AVAILABLE
    health: Health = Health.NOMINAL
    endurance_minutes: float = 30.0
    max_speed_m_s: float = 10.0
    selected: bool = True

    def can(self, capability: str) -> bool:
        return (
            self.selected
            and self.availability not in {Availability.DISABLED, Availability.WITHDRAWN}
            and self.health is not Health.FAILED
            and capability in self.capabilities
        )
