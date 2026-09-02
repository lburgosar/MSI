"""Runtime compartido que gobierna misión, simulación, eventos y decisiones."""

from __future__ import annotations

from copy import deepcopy
from typing import Callable

from application.demo_catalog import DEMO_BOUNDS
from domain.geography import Altitude, AltitudeReference, GeoPoint
from domain.mission import (
    DecisionRecord,
    MissionConfiguration,
    MissionIntent,
    MissionPlan,
    OperationalEvent,
    PreflightResult,
    PreflightStatus,
)
from domain.resources import Availability, Health, Resource
from domain.serialization import to_primitive
from planning.planners import MissionPlanner
from planning.preflight import PreflightService
from providers.resources import ResourceProvider
from simulation.engine import DroneCommand, SimulatedDrone, SimulationEngine
from maps.providers import LocalMapProvider, MapProvider
from traceability.recorder import OperationalTraceRecorder
from transport.channels import OperationalStatePublisher

from .decision_engine import DecisionEngine


class MissionRuntimeV2:
    """Fuente de verdad operacional; ninguna interfaz decide ni mueve recursos."""

    def __init__(
        self,
        configuration: MissionConfiguration,
        resource_provider: ResourceProvider,
        state_publisher: OperationalStatePublisher | None = None,
        trace_recorder: OperationalTraceRecorder | None = None,
        map_provider: MapProvider | None = None,
    ) -> None:
        self.configuration = configuration
        self.resource_provider = resource_provider
        self.state_publisher = state_publisher
        self.trace_recorder = trace_recorder
        self.map_provider = map_provider or LocalMapProvider(DEMO_BOUNDS)
        self.planner_service = MissionPlanner()
        self.preflight_service = PreflightService()
        self.decision_engine = DecisionEngine()
        self.environment = {
            "wind_m_s": float(configuration.parameters.get("wind_m_s", 0.0)),
            "wind_direction_deg": float(configuration.parameters.get("wind_direction_deg", 0.0)),
            "temperature_c": float(configuration.parameters.get("temperature_c", 0.0)),
        }
        self.phase = "configuration"
        self.status = "configuring"
        self.plan: MissionPlan | None = None
        self.preflight: PreflightResult | None = None
        self.events: list[OperationalEvent] = []
        self.decisions: list[DecisionRecord] = []
        self.simulation: SimulationEngine | None = None
        self.authorized = False
        self.paused = False
        self.publish_timer = 0.0
        self.execution_elapsed_seconds = 0.0
        self._outcome_recorded = False
        self.initial_product: dict[str, float] = {}
        if self.trace_recorder:
            self.trace_recorder.record("mission_configuration", configuration)
            self.trace_recorder.record("resource_snapshot", resource_provider.list_resources())
        self.plan_mission()

    def plan_mission(self) -> None:
        resources = self.resource_provider.list_resources()
        previous_version = self.plan.version if self.plan else 0
        self.plan = self.planner_service.create_plan(self.configuration, resources)
        self.plan.version = previous_version + 1
        self.preflight = self.preflight_service.validate(self.configuration, self.plan, resources)
        self.phase = "preview"
        self.status = "ready" if self.preflight.status is PreflightStatus.READY else "blocked"
        self.authorized = False
        self._prepare_simulation(resources)
        self._event("plan", f"Plan V{self.plan.version} generado: {len(self.plan.tasks)} tareas")
        if self.trace_recorder:
            self.trace_recorder.record("plan", self.plan)
            self.trace_recorder.record("preflight", self.preflight)
        self.publish()

    def _prepare_simulation(self, resources: list[Resource]) -> None:
        assigned_ids = {task.assigned_resource_id for task in self.plan.tasks} if self.plan else set()
        drones = []
        for resource in resources:
            if resource.resource_id not in assigned_ids:
                continue
            position = self.map_provider.world_to_map(resource.position)
            drones.append(SimulatedDrone(
                drone_id=resource.resource_id,
                position=position,
                capabilities=tuple(sorted(resource.capabilities)),
                battery_percent=resource.energy.percent,
                status="assigned",
            ))
            if resource.consumable:
                self.initial_product[resource.resource_id] = resource.consumable.remaining_l
        self.simulation = SimulationEngine(drones, cruise_speed=0.075, battery_drain_per_unit=1.8)
        for task in self.plan.tasks if self.plan else []:
            drone = self.simulation.drones.get(task.assigned_resource_id or "")
            if drone is None or not task.route:
                continue
            route = [self.map_provider.world_to_map(point) for point in task.route]
            drone.assigned_task = task.task_id
            drone.route = route
            drone.target = route[0]
            drone.trajectory = [drone.position, *route]

    def authorize(self) -> bool:
        if self.preflight is None or self.preflight.status is not PreflightStatus.READY:
            self._event("authorization_blocked", "Autorización rechazada por preflight")
            self.publish()
            return False
        self.authorized = True
        self.status = "authorized"
        self.phase = "authorization"
        self._event("authorization", "Operador autorizó el plan operacional")
        self.publish()
        return True

    def start(self) -> bool:
        if not self.authorized or self.simulation is None or self.plan is None:
            return False
        commands = []
        for task in self.plan.tasks:
            route = tuple(self.map_provider.world_to_map(point) for point in task.route)
            if task.assigned_resource_id and route:
                commands.append(DroneCommand(task.assigned_resource_id, route[0], task.task_id, route))
                task.status = "executing"
        self.simulation.apply_commands(commands)
        self.phase = "execution"
        self.status = "running"
        self._event("execution", f"Ejecución iniciada con {len(commands)} recursos")
        self.publish()
        return True

    def update(self, delta_time: float) -> None:
        if self.status != "running" or self.paused or self.simulation is None:
            return
        self.simulation.update(delta_time)
        self.execution_elapsed_seconds += delta_time
        self._sync_operational_resources()
        self.publish_timer += delta_time
        if self.publish_timer >= 0.10:
            self.publish()
            self.publish_timer = 0.0
        assigned_ids = {
            task.assigned_resource_id for task in self.plan.tasks if task.assigned_resource_id
        } if self.plan else set()
        if assigned_ids and all(
            self.simulation.drones[resource_id].status == "on_task"
            for resource_id in assigned_ids
        ):
            self.status = "completed"
            self.phase = "finished"
            for task in self.plan.tasks if self.plan else []:
                task.status = "completed"
                task.progress_percent = 100.0
            self._event("result", "Todos los objetivos del plan fueron completados")
            self.publish()
            if self.trace_recorder and not self._outcome_recorded:
                self.trace_recorder.record("outcome", self.mission_summary())
                self._outcome_recorded = True

    def _sync_operational_resources(self) -> None:
        if self.simulation is None or self.plan is None:
            return
        for task in self.plan.tasks:
            resource_id = task.assigned_resource_id
            if not resource_id or resource_id not in self.simulation.drones:
                continue
            drone = self.simulation.drones[resource_id]
            telemetry = drone.telemetry()
            partial = float(telemetry["route_progress_percent"]) / 100.0
            task.progress_percent = min(100.0, partial * 100.0)
            try:
                resource = self.resource_provider.get_resource(resource_id)
            except ValueError:
                continue
            resource.energy.percent = drone.battery_percent
            resource.availability = Availability.ACTIVE
            if resource.consumable and self.configuration.intent is MissionIntent.PRECISION_SPRAYING:
                assigned_tasks = max(1, len(self.plan.tasks))
                used = self.plan.estimated_consumption_l / assigned_tasks * partial
                baseline = self.initial_product.get(resource_id, resource.consumable.remaining_l)
                resource.consumable.remaining_l = max(0.0, baseline - used)
            self.resource_provider.update_resource(resource)

    def inject_condition(
        self,
        condition: str,
        value: object,
        resource_id: str | None = None,
    ) -> None:
        if condition in {"wind_m_s", "wind_direction_deg"}:
            self.environment[condition] = float(value)
            self.configuration.parameters[condition] = float(value)
            event = self._event("condition", f"{condition} cambió a {value}", data={condition: value})
            if self.status not in {"running", "paused"}:
                self.plan_mission()
                return
            if condition == "wind_m_s" and self.configuration.intent is MissionIntent.PRECISION_SPRAYING:
                limit = float(self.configuration.parameters.get("max_wind_m_s", 0.0))
                if float(value) > limit:
                    self._apply_decision(self.decision_engine.wind_decision(event, limit))
                elif self.paused:
                    self._event(
                        "conditions_restored",
                        f"Condiciones restablecidas: viento {float(value):.1f} m/s; "
                        f"límite {limit:.1f} m/s. Reanudación disponible.",
                        data={"wind_m_s": float(value), "limit_m_s": limit},
                    )
            self.publish()
            return

        if condition == "thermal_anomaly":
            latitude, longitude = value  # type: ignore[misc]
            event = self._event(
                "detection", "Anomalía térmica detectada",
                data={"latitude": latitude, "longitude": longitude},
            )
            thermal = next(
                (item for item in self.resource_provider.list_resources() if item.can("thermal_imaging")),
                None,
            )
            decision = self.decision_engine.patrol_anomaly(event, thermal.resource_id if thermal else None)
            self._apply_decision(decision)
            if thermal and self.configuration.intent in {
                MissionIntent.AUTONOMOUS_PATROL,
                MissionIntent.EMERGENCY_RESPONSE,
            }:
                self._divert_to_anomaly(thermal.resource_id, float(latitude), float(longitude))
            self.publish()
            return

        if resource_id is None:
            raise ValueError(f"{condition} requires resource_id")
        resource = self.resource_provider.get_resource(resource_id)
        if condition == "battery_percent":
            resource.energy.percent = float(value)
            summary = f"{resource_id} batería {float(value):.0f}%"
        elif condition == "product_remaining_l":
            if resource.consumable is None:
                raise ValueError(f"{resource_id} has no consumable")
            resource.consumable.remaining_l = float(value)
            self.initial_product[resource_id] = float(value)
            summary = f"{resource_id} producto restante {float(value):.1f} L"
        elif condition == "link_quality_percent":
            resource.communication.link_quality_percent = float(value)
            summary = f"{resource_id} enlace {float(value):.0f}%"
        elif condition == "sensor_failure":
            resource.sensors = [
                type(sensor)(sensor.sensor_id, sensor.sensor_type, False, sensor.data_kind)
                if sensor.sensor_id == value else sensor
                for sensor in resource.sensors
            ]
            resource.health = Health.DEGRADED
            summary = f"{resource_id} perdió sensor {value}"
        elif condition == "withdraw_resource":
            self.resource_provider.withdraw_resource(resource_id)
            summary = f"Operador retiró {resource_id}"
            resource = self.resource_provider.get_resource(resource_id)
        else:
            raise ValueError(f"Unsupported condition: {condition}")
        self.resource_provider.update_resource(resource)
        event = self._event("condition", summary, resource_id)
        if self.status not in {"running", "paused"}:
            self.plan_mission()
            return
        if condition in {"battery_percent", "product_remaining_l", "withdraw_resource"}:
            threshold_hit = (
                condition == "withdraw_resource"
                or (condition == "battery_percent" and float(value) <= resource.energy.reserve_percent + 5)
                or (condition == "product_remaining_l" and float(value) <= 2.0)
            )
            if threshold_hit:
                self._reassign_resource(resource_id, event)
        self.publish()

    def _reassign_resource(self, resource_id: str, event: OperationalEvent) -> None:
        if self.plan is None or self.simulation is None:
            return
        task = next((item for item in self.plan.tasks if item.assigned_resource_id == resource_id), None)
        drone = self.simulation.drones.get(resource_id)
        if task is None or drone is None:
            return
        remaining = drone.route[drone.waypoint_index:]
        candidates = [
            item for item in self.resource_provider.list_resources()
            if item.resource_id != resource_id and item.can(task.task_type)
            and item.energy.percent > item.energy.reserve_percent + 10
        ]
        replacement = max(candidates, key=lambda item: item.energy.percent, default=None)
        decision = self.decision_engine.resource_reassignment(
            event, replacement.resource_id if replacement else None, len(remaining)
        )
        self._apply_decision(decision)
        drone.status = "withdrawn" if "retiró" in event.summary else "returning"
        drone.speed = 0.0
        if replacement and remaining:
            replacement_drone = self.simulation.drones.get(replacement.resource_id)
            if replacement_drone is None:
                replacement_drone = SimulatedDrone(
                    replacement.resource_id,
                    self.map_provider.world_to_map(replacement.position),
                    tuple(sorted(replacement.capabilities)),
                    battery_percent=replacement.energy.percent,
                )
                self.simulation.drones[replacement.resource_id] = replacement_drone
            existing_remaining = (
                replacement_drone.route[replacement_drone.waypoint_index:]
                if replacement_drone.status == "moving"
                else []
            )
            combined_route = [*existing_remaining, *remaining]
            task.assigned_resource_id = replacement.resource_id
            task.status = "replanned"
            self.simulation.apply_commands([
                DroneCommand(
                    replacement.resource_id,
                    combined_route[0],
                    f"{replacement_drone.assigned_task} + {task.task_id}",
                    tuple(combined_route),
                )
            ])
            self.plan.version += 1
            self.plan.estimated_duration_minutes += 3.2
            self._event("replan", f"Plan V{self.plan.version}: {task.task_id} reasignada a {replacement.resource_id}")

    def _divert_to_anomaly(self, resource_id: str, latitude: float, longitude: float) -> None:
        if self.simulation is None:
            return
        center = GeoPoint(latitude, longitude, Altitude(35, AltitudeReference.AGL))
        offsets = ((0, -0.0007), (0.0007, 0), (0, 0.0007), (-0.0007, 0), (0, -0.0007))
        route = tuple(self.map_provider.world_to_map(GeoPoint(
            center.latitude + dy, center.longitude + dx, center.altitude
        )) for dy, dx in offsets)
        if resource_id in self.simulation.drones:
            self.simulation.apply_commands([
                DroneCommand(resource_id, route[0], "THERMAL-CONFIRM", route)
            ])
            self._event("replan", f"{resource_id} desviado a órbita de confirmación térmica")

    def _apply_decision(self, decision: DecisionRecord) -> None:
        self.decisions.append(decision)
        if self.trace_recorder:
            self.trace_recorder.record("decision", decision)
        self._event("decision", decision.selected_action, data={
            "reason": decision.reason,
            "impact": decision.impact,
            "alternatives": list(decision.alternatives),
        })
        if decision.selected_action == "pause_mission":
            self.paused = True
            self.status = "paused"
            self.phase = "intervention"

    def resume_if_valid(self) -> bool:
        if not self.paused:
            return False
        limit = float(self.configuration.parameters.get("max_wind_m_s", 999.0))
        if self.environment["wind_m_s"] > limit:
            wind = self.environment["wind_m_s"]
            self._event(
                "resume_rejected",
                f"Reanudación rechazada: viento actual {wind:.1f} m/s; límite {limit:.1f} m/s.",
                data={"wind_m_s": wind, "limit_m_s": limit, "reason": "wind_above_limit"},
            )
            self.publish()
            return False
        self.paused = False
        self.status = "running"
        self.phase = "execution"
        self._event("decision", "Condiciones válidas; misión reanudada")
        self.publish()
        return True

    def _event(
        self,
        event_type: str,
        summary: str,
        resource_id: str | None = None,
        data: dict[str, object] | None = None,
    ) -> OperationalEvent:
        event = OperationalEvent(event_type, summary, resource_id, data or {})
        self.events.append(event)
        if self.trace_recorder:
            self.trace_recorder.record("event", event)
        return event

    def progress_percent(self) -> int:
        if not self.plan or not self.plan.tasks:
            return 0
        return round(sum(task.progress_percent for task in self.plan.tasks) / len(self.plan.tasks))

    def preflight_explanation(self, resources: list[Resource]) -> dict[str, object]:
        """Structured, interface-neutral explanation of the current viability check."""
        assigned_ids = {
            task.assigned_resource_id for task in self.plan.tasks if task.assigned_resource_id
        } if self.plan else set()
        capability = {
            MissionIntent.PRECISION_SPRAYING: "precision_spraying",
            MissionIntent.AUTONOMOUS_PATROL: "area_patrol",
            MissionIntent.EMERGENCY_RESPONSE: "incident_assessment",
        }[self.configuration.intent]
        compatible = [item for item in resources if item.can(capability)]
        assigned = [item for item in resources if item.resource_id in assigned_ids]
        checks: list[dict[str, object]] = [
            {
                "label": "Recursos compatibles",
                "actual": ", ".join(item.resource_id for item in compatible) or "ninguno",
                "required": capability,
                "ok": bool(compatible),
            },
            {
                "label": "Reserva energética",
                "actual": ", ".join(
                    f"{item.resource_id} {item.energy.percent:.0f}%" for item in assigned
                ) or "sin asignación",
                "required": "reserva + 8%",
                "ok": bool(assigned) and all(
                    item.energy.percent > item.energy.reserve_percent + 8 for item in assigned
                ),
            },
        ]
        if self.configuration.intent is MissionIntent.PRECISION_SPRAYING:
            required = float(self.plan.estimated_consumption_l if self.plan else 0.0)
            available = sum(
                item.consumable.remaining_l for item in assigned if item.consumable
            )
            wind = self.environment["wind_m_s"]
            limit = self.configuration.parameters.get("max_wind_m_s")
            checks.extend([
                {
                    "label": "Producto compatible",
                    "actual": f"{available:.1f} L",
                    "required": f"{required:.1f} L",
                    "ok": available >= required,
                },
                {
                    "label": "Viento",
                    "actual": f"{wind:.1f} m/s",
                    "required": "límite no definido" if limit is None else f"≤ {float(limit):.1f} m/s",
                    "ok": limit is not None and wind <= float(limit),
                },
            ])
        alternatives_by_code = {
            "NO_COMPATIBLE_RESOURCE": ("incorporar un recurso compatible", "modificar el objetivo"),
            "ENERGY_RESERVE": ("recargar o sustituir el recurso", "reducir el alcance"),
            "INSUFFICIENT_PRODUCT": ("recargar producto", "incorporar recurso compatible", "reducir área o dividir misión"),
            "WIND_LIMIT_MISSING": ("definir un límite operacional validado",),
            "WIND_LIMIT": ("esperar condiciones válidas", "modificar la misión dentro de reglas autorizadas"),
        }
        findings = []
        for finding in self.preflight.findings if self.preflight else []:
            findings.append({
                **to_primitive(finding),
                "alternatives": list(alternatives_by_code.get(finding.code, ())),
            })
        return {
            "status": self.preflight.status.value if self.preflight else "unknown",
            "available_count": len(resources),
            "compatible_ids": [item.resource_id for item in compatible],
            "assigned_ids": sorted(assigned_ids),
            "area_hectares": self.configuration.parameters.get("area_hectares"),
            "checks": checks,
            "findings": findings,
            "result": "MISIÓN VIABLE" if self.preflight and self.preflight.status is PreflightStatus.READY else "INTERVENCIÓN REQUERIDA",
        }

    def mission_summary(self) -> dict[str, object]:
        """Outcome metrics derived only from the current simplified model."""
        progress = self.progress_percent()
        active_resources = self.resource_provider.list_resources()
        catalog = (
            self.resource_provider.list_catalog()
            if hasattr(self.resource_provider, "list_catalog") else active_resources
        )
        current_product = sum(
            item.consumable.remaining_l for item in catalog if item.consumable is not None
        )
        initial_product = sum(self.initial_product.values())
        resource_ids = sorted({
            drone.drone_id for drone in self.simulation.drones.values()
            if drone.assigned_task
        }) if self.simulation else []
        return {
            "result": "COMPLETADA" if self.status == "completed" else self.status.upper(),
            "model": "SIMULACIÓN OPERACIONAL SIMPLIFICADA",
            "duration_seconds": round(self.execution_elapsed_seconds, 1),
            "progress_percent": progress,
            "coverage_hectares": round((self.plan.coverage_hectares if self.plan else 0.0) * progress / 100.0, 2),
            "product_used_l": round(max(0.0, initial_product - current_product), 2),
            "product_remaining_l": round(current_product, 2),
            "resources_used": resource_ids,
            "decision_count": len(self.decisions),
            "replan_count": sum(event.event_type == "replan" for event in self.events),
            "pause_count": sum(item.selected_action == "pause_mission" for item in self.decisions),
            "incident_count": sum(event.event_type == "detection" for event in self.events),
            "trace_available": self.trace_recorder is not None,
        }

    def snapshot(self) -> dict[str, object]:
        resources = self.resource_provider.list_resources()
        resource_snapshots = to_primitive(resources)
        task_by_resource = {
            task.assigned_resource_id: task for task in self.plan.tasks if task.assigned_resource_id
        } if self.plan else {}
        capability = {
            MissionIntent.PRECISION_SPRAYING: "precision_spraying",
            MissionIntent.AUTONOMOUS_PATROL: "area_patrol",
            MissionIntent.EMERGENCY_RESPONSE: "incident_assessment",
        }[self.configuration.intent]
        for resource, resource_snapshot in zip(resources, resource_snapshots):
            x, y = self.map_provider.world_to_map(resource.position)
            resource_snapshot["map_position"] = {"x": x, "y": y}
            task = task_by_resource.get(resource.resource_id)
            resource_snapshot["mission_role"] = (
                "APLICACIÓN" if resource.can("precision_spraying") else
                "RECONOCIMIENTO TÉRMICO" if resource.can("thermal_imaging") else
                "PATRULLA / RELAY" if resource.can("area_patrol") else
                "NO COMPATIBLE"
            )
            resource_snapshot["compatible"] = resource.can(capability)
            resource_snapshot["assigned"] = task is not None
            resource_snapshot["assignment"] = (
                {"task_id": task.task_id, "sector": task.sector, "status": task.status}
                if task else None
            )
        drones = self.simulation.telemetry() if self.simulation else []
        wind_limit = float(self.configuration.parameters.get("max_wind_m_s", 999.0))
        resume_allowed = self.paused and self.environment["wind_m_s"] <= wind_limit
        return {
            "schema_version": 2,
            "mode": self.resource_provider.mode,
            "mission_id": self.configuration.mission_id,
            "scenario": self.configuration.intent.value,
            "action": self.configuration.name,
            "location": "Las Marías",
            "status": self.status,
            "phase": self.phase,
            "progress_percent": self.progress_percent(),
            "authorized": self.authorized,
            "resume_allowed": resume_allowed,
            "resume_block_reason": (
                "" if resume_allowed or not self.paused else
                f"Viento {self.environment['wind_m_s']:.1f} m/s > límite {wind_limit:.1f} m/s"
            ),
            "preflight": to_primitive(self.preflight),
            "preflight_explanation": self.preflight_explanation(resources),
            "plan": to_primitive(self.plan),
            "resources": resource_snapshots,
            "drones": drones,
            "active_drones": sum(item.get("status") == "moving" for item in drones),
            "assigned_nodes": len({task.assigned_resource_id for task in self.plan.tasks}) if self.plan else 0,
            "connected_nodes": sum(item.communication.connected for item in resources),
            "operational_nodes": sum(item.health is not Health.FAILED for item in resources),
            "environment": deepcopy(self.environment),
            "wind_m_s": self.environment["wind_m_s"],
            "temperature_c": self.environment["temperature_c"],
            "link_quality_percent": round(
                sum(item.communication.link_quality_percent for item in resources) / max(1, len(resources))
            ),
            "map": {
                "bounds": to_primitive(self.map_provider.bounds),
                **self.map_provider.descriptor(),
                "operational_area": to_primitive(self.configuration.operational_area),
                "geofence": to_primitive(self.configuration.geofence),
            },
            "events": to_primitive(self.events[-30:]),
            "decisions": to_primitive(self.decisions[-20:]),
            "latest_event": self.events[-1].summary if self.events else "",
            "latest_decision": (
                {
                    "summary": self.decisions[-1].selected_action,
                    "reason": self.decisions[-1].reason,
                    "impact": self.decisions[-1].impact,
                    "intervention_required": self.paused,
                }
                if self.decisions
                else {
                    "summary": "Plan operacional generado",
                    "reason": self.plan.rationale[0] if self.plan and self.plan.rationale else "",
                    "impact": "Pendiente de autorización",
                    "intervention_required": False,
                }
            ),
            "decision_narrative": (
                {
                    "condition": self.decisions[-1].trigger,
                    "evaluation": self.decisions[-1].evaluation,
                    "decision": self.decisions[-1].selected_action,
                    "impact": self.decisions[-1].impact,
                    "action": ", ".join(self.decisions[-1].commands) or "Intervención requerida",
                }
                if self.decisions else None
            ),
            "mission_summary": self.mission_summary(),
        }

    def publish(self) -> None:
        snapshot = self.snapshot()
        if self.state_publisher is not None:
            self.state_publisher.publish(snapshot)
        if self.trace_recorder and self.status in {"running", "paused", "completed"}:
            self.trace_recorder.record("telemetry", {
                "mission_id": self.configuration.mission_id,
                "status": self.status,
                "progress_percent": snapshot["progress_percent"],
                "drones": snapshot["drones"],
            })
