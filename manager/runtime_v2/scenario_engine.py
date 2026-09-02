"""Entrada explícita de cambios del mundo en Simulation Mode."""

from __future__ import annotations

from typing import Protocol


class ScenarioTarget(Protocol):
    def inject_condition(self, condition: str, value: object, resource_id: str | None = None) -> None: ...


class ScenarioEngine:
    """API neutral: sliders, tests o replay utilizan las mismas condiciones."""

    def __init__(self, target: ScenarioTarget) -> None:
        self.target = target

    def set_wind(self, speed_m_s: float, direction_deg: float | None = None) -> None:
        self.target.inject_condition("wind_m_s", speed_m_s)
        if direction_deg is not None:
            self.target.inject_condition("wind_direction_deg", direction_deg)

    def set_battery(self, resource_id: str, percent: float) -> None:
        self.target.inject_condition("battery_percent", percent, resource_id)

    def set_product(self, resource_id: str, remaining_l: float) -> None:
        self.target.inject_condition("product_remaining_l", remaining_l, resource_id)

    def set_link_quality(self, resource_id: str, percent: float) -> None:
        self.target.inject_condition("link_quality_percent", percent, resource_id)

    def fail_sensor(self, resource_id: str, sensor_id: str) -> None:
        self.target.inject_condition("sensor_failure", sensor_id, resource_id)

    def withdraw(self, resource_id: str) -> None:
        self.target.inject_condition("withdraw_resource", True, resource_id)

    def inject_thermal_anomaly(self, latitude: float, longitude: float) -> None:
        self.target.inject_condition("thermal_anomaly", (latitude, longitude))
