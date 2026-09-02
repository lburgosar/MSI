"""Movimiento lógico y telemetría para recursos aéreos simulados.

El motor no asigna tareas ni toma decisiones de misión. Recibe comandos de la
capa MSI, ejecuta el movimiento solicitado y expone el estado resultante.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from math import atan2, degrees, hypot
from typing import Any


@dataclass(frozen=True)
class DroneCommand:
    """Orden ya decidida por MSI para un recurso concreto."""

    drone_id: str
    target: tuple[float, float]
    task: str
    waypoints: tuple[tuple[float, float], ...] = ()


@dataclass
class SimulatedDrone:
    """Estado físico mínimo de un dron dentro del mundo simulado."""

    drone_id: str
    position: tuple[float, float]
    capabilities: tuple[str, ...]
    speed: float = 0.0
    orientation_degrees: float = 0.0
    battery_percent: float = 100.0
    status: str = "available"
    assigned_task: str | None = None
    target: tuple[float, float] | None = None
    trajectory: list[tuple[float, float]] = field(default_factory=list)
    route: list[tuple[float, float]] = field(default_factory=list)
    waypoint_index: int = 0

    def telemetry(self) -> dict[str, Any]:
        return {
            "id": self.drone_id,
            "position": {"x": self.position[0], "y": self.position[1]},
            "orientation_degrees": self.orientation_degrees,
            "speed": self.speed,
            "battery_percent": self.battery_percent,
            "status": self.status,
            "capabilities": list(self.capabilities),
            "assigned_task": self.assigned_task,
            "target": (
                {"x": self.target[0], "y": self.target[1]}
                if self.target is not None
                else None
            ),
            "objective": (
                {"x": self.route[-1][0], "y": self.route[-1][1]}
                if self.route
                else None
            ),
            "waypoint_index": self.waypoint_index,
            "waypoint_count": len(self.route),
            "trajectory": [
                {"x": point[0], "y": point[1]}
                for point in self.trajectory
            ],
        }


class SimulationEngine:
    """Ejecuta comandos sin contener lógica de planificación de misión."""

    def __init__(
        self,
        drones: list[SimulatedDrone],
        cruise_speed: float = 0.12,
        battery_drain_per_unit: float = 0.05,
    ) -> None:
        self.drones = {drone.drone_id: drone for drone in drones}
        self.cruise_speed = cruise_speed
        self.battery_drain_per_unit = battery_drain_per_unit

    def apply_commands(self, commands: list[DroneCommand]) -> None:
        for command in commands:
            drone = self.drones.get(command.drone_id)
            if drone is None:
                raise ValueError(f"Unknown simulated drone: {command.drone_id}")

            route = list(command.waypoints) or [command.target]
            drone.assigned_task = command.task
            drone.route = route
            drone.waypoint_index = 0
            drone.target = route[0]
            drone.trajectory = [drone.position, *route]
            drone.status = "moving"
            drone.speed = self.cruise_speed

    def update(self, delta_time: float) -> None:
        if delta_time < 0:
            raise ValueError("delta_time must be non-negative")

        for drone in self.drones.values():
            self._update_drone(drone, delta_time)

    def _update_drone(self, drone: SimulatedDrone, delta_time: float) -> None:
        if drone.target is None or drone.status != "moving":
            return

        delta_x = drone.target[0] - drone.position[0]
        delta_y = drone.target[1] - drone.position[1]
        distance = hypot(delta_x, delta_y)

        if distance == 0:
            self._arrive(drone)
            return

        drone.orientation_degrees = degrees(atan2(delta_y, delta_x))
        travelled = min(distance, self.cruise_speed * delta_time)
        ratio = travelled / distance
        drone.position = (
            drone.position[0] + delta_x * ratio,
            drone.position[1] + delta_y * ratio,
        )
        drone.battery_percent = max(
            0.0,
            drone.battery_percent - travelled * self.battery_drain_per_unit,
        )

        if travelled == distance:
            self._arrive(drone)

    @staticmethod
    def _arrive(drone: SimulatedDrone) -> None:
        drone.position = drone.target or drone.position
        if drone.waypoint_index + 1 < len(drone.route):
            drone.waypoint_index += 1
            drone.target = drone.route[drone.waypoint_index]
            drone.status = "moving"
            return
        drone.speed = 0.0
        drone.status = "on_task"

    def telemetry(self) -> list[dict[str, Any]]:
        return [drone.telemetry() for drone in self.drones.values()]
