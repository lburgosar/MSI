"""Orquesta una misión normal entre planificación, simulación y estado."""

from __future__ import annotations

from math import hypot
from typing import Callable

from simulation.engine import DroneCommand, SimulationEngine, SimulatedDrone

from core.mission_state import MissionState


class MissionRuntime:
    """Decide el plan demo y ordena su ejecución al Simulation Engine.

    Esta primera misión es deliberadamente determinista. La asignación vive
    aquí —no en la escena ni en el motor físico— para que posteriormente pueda
    sustituirse por el Decision Engine sin modificar las interfaces.
    """

    def __init__(
        self,
        mission_state: MissionState,
        action: str,
        on_event: Callable[[str, str], None] | None = None,
    ) -> None:
        self.mission_state = mission_state
        self.action = action
        self.on_event = on_event
        self.running = False
        self.completed = False
        self.publish_timer = 0.0
        self.publish_interval = 0.10

        starts = [(0.10, 0.22), (0.10, 0.50), (0.10, 0.78)]
        targets = [(0.86, 0.22), (0.86, 0.50), (0.86, 0.78)]
        self.commands: list[DroneCommand] = []
        drones: list[SimulatedDrone] = []

        for index, (start, target) in enumerate(zip(starts, targets), start=1):
            drone_id = f"MSI-DRONE-{index:02d}"
            task = f"{self.action} · Hilera {index:02d}"
            drone = SimulatedDrone(
                drone_id=drone_id,
                position=start,
                capabilities=("flight", "mission_payload"),
                status="assigned",
                assigned_task=task,
                target=target,
                trajectory=[start, target],
            )
            drones.append(drone)
            self.commands.append(DroneCommand(drone_id, target, task))

        self.engine = SimulationEngine(drones, cruise_speed=0.085)
        self.initial_distances = {
            drone.drone_id: self._distance(drone.position, drone.target)
            for drone in drones
        }
        self._publish("Plan válido: 3 drones asignados")

    @staticmethod
    def _distance(
        position: tuple[float, float],
        target: tuple[float, float] | None,
    ) -> float:
        if target is None:
            return 0.0
        return hypot(target[0] - position[0], target[1] - position[1])

    @property
    def plan_valid(self) -> bool:
        return bool(self.commands) and not self.running and not self.completed

    def start(self) -> None:
        if not self.plan_valid:
            return

        self.engine.apply_commands(self.commands)
        self.running = True
        self.mission_state.begin_execution()
        self._emit_event("execution_started", "Los 3 drones iniciaron la misión.")
        self._publish("3 drones desplazándose hacia sus objetivos")

    def update(self, delta_time: float) -> None:
        if not self.running:
            return

        self.engine.update(delta_time)
        self.publish_timer += delta_time

        if self.publish_timer >= self.publish_interval:
            self._publish("Drones ejecutando el plan")
            self.publish_timer = 0.0

        if all(drone.status == "on_task" for drone in self.engine.drones.values()):
            self.running = False
            self.completed = True
            self._publish("Objetivos alcanzados")
            self.mission_state.complete()
            self._emit_event("execution_completed", "Los 3 drones alcanzaron sus objetivos.")

    def progress_percent(self) -> int:
        progress_values = []
        for drone in self.engine.drones.values():
            initial = self.initial_distances[drone.drone_id]
            remaining = self._distance(drone.position, drone.target)
            progress_values.append(1.0 if initial == 0 else 1.0 - remaining / initial)
        return round(sum(progress_values) / len(progress_values) * 100)

    def _publish(self, event_summary: str) -> None:
        telemetry = self.engine.telemetry()
        active = sum(item["status"] == "moving" for item in telemetry)
        self.mission_state.update(
            drones=telemetry,
            assigned_nodes=len(telemetry),
            active_drones=active,
            progress_percent=self.progress_percent(),
            latest_event=event_summary,
        )

    def _emit_event(self, event_type: str, message: str) -> None:
        if self.on_event is not None:
            self.on_event(event_type, message)
