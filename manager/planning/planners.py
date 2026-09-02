"""Planners por intención sobre un único contrato de misión y recursos."""

from __future__ import annotations

from math import ceil

from domain.geography import Altitude, AltitudeReference, GeoPoint
from domain.mission import MissionConfiguration, MissionIntent, MissionPlan, MissionTask
from domain.resources import Resource


class MissionPlanner:
    """Selecciona el planner de dominio sin duplicar el Mission Runtime."""

    def create_plan(
        self,
        configuration: MissionConfiguration,
        resources: list[Resource],
    ) -> MissionPlan:
        if configuration.intent is MissionIntent.PRECISION_SPRAYING:
            return self._spraying(configuration, resources)
        if configuration.intent is MissionIntent.AUTONOMOUS_PATROL:
            return self._patrol(configuration, resources)
        return self._emergency(configuration, resources)

    @staticmethod
    def eligible(resources: list[Resource], capability: str) -> list[Resource]:
        return [resource for resource in resources if resource.can(capability)]

    def _spraying(self, config: MissionConfiguration, resources: list[Resource]) -> MissionPlan:
        selected = self.eligible(resources, "precision_spraying")
        tasks: list[MissionTask] = []
        if selected:
            vertices = config.operational_area.vertices
            north = max(point.latitude for point in vertices)
            south = min(point.latitude for point in vertices)
            west = min(point.longitude for point in vertices)
            east = max(point.longitude for point in vertices)
            pass_count = 12
            passes: list[tuple[GeoPoint, GeoPoint]] = []
            altitude = Altitude(
                float(config.parameters["altitude_above_canopy_m"]),
                AltitudeReference.ABOVE_CANOPY,
            )
            for index in range(pass_count):
                latitude = north - (north - south) * (index + 0.5) / pass_count
                endpoints = (
                    GeoPoint(latitude, west, altitude),
                    GeoPoint(latitude, east, altitude),
                )
                passes.append(endpoints if index % 2 == 0 else endpoints[::-1])

            chunk_size = ceil(len(passes) / len(selected))
            for resource_index, resource in enumerate(selected):
                assigned_passes = passes[
                    resource_index * chunk_size:(resource_index + 1) * chunk_size
                ]
                if not assigned_passes:
                    continue
                route = [point for pass_points in assigned_passes for point in pass_points]
                tasks.append(
                    MissionTask(
                        f"SPRAY-{resource_index + 1:02d}",
                        "precision_spraying",
                        {"flight", "precision_spraying"},
                        route,
                        resource.resource_id,
                        sector=chr(65 + resource_index),
                    )
                )

        area = float(config.parameters.get("area_hectares", 0.0))
        dose = float(config.parameters.get("dose_l_ha", 0.0))
        return MissionPlan(
            config.mission_id,
            tasks,
            estimated_duration_minutes=18.0 if len(tasks) >= 2 else 31.0,
            estimated_consumption_l=area * dose,
            coverage_hectares=area,
            rationale=[
                f"{len(selected)} recursos compatibles con payload de aplicación",
                "Pasadas alternadas para reducir transiciones sin aplicación",
            ],
        )

    def _patrol(self, config: MissionConfiguration, resources: list[Resource]) -> MissionPlan:
        selected = self.eligible(resources, "area_patrol")[:3]
        vertices = config.operational_area.vertices
        north = max(point.latitude for point in vertices)
        south = min(point.latitude for point in vertices)
        west = min(point.longitude for point in vertices)
        east = max(point.longitude for point in vertices)
        altitude = Altitude(float(config.parameters["altitude_agl_m"]), AltitudeReference.AGL)
        tasks = []
        for index, resource in enumerate(selected):
            left = west + (east - west) * index / max(1, len(selected))
            right = west + (east - west) * (index + 1) / max(1, len(selected))
            route = [
                GeoPoint(north, left, altitude), GeoPoint(north, right, altitude),
                GeoPoint((north + south) / 2, right, altitude),
                GeoPoint((north + south) / 2, left, altitude),
                GeoPoint(south, left, altitude), GeoPoint(south, right, altitude),
            ]
            tasks.append(MissionTask(
                f"PATROL-{index + 1:02d}", "area_patrol", {"flight", "area_patrol"},
                route, resource.resource_id, sector=chr(65 + index),
            ))
        return MissionPlan(
            config.mission_id, tasks, 22.0, coverage_hectares=3.6,
            rationale=["Cobertura dividida por sectores", "Recursos elegidos por sensor y autonomía"],
        )

    def _emergency(self, config: MissionConfiguration, resources: list[Resource]) -> MissionPlan:
        selected = self.eligible(resources, "incident_assessment")
        latitude = float(config.parameters["incident_lat"])
        longitude = float(config.parameters["incident_lon"])
        altitude = Altitude(40.0, AltitudeReference.AGL)
        route_offsets = ((-0.001, 0), (0, 0.001), (0.001, 0), (0, -0.001), (-0.001, 0))
        tasks = []
        for index, resource in enumerate(selected[:2]):
            route = [GeoPoint(latitude + dy, longitude + dx, altitude) for dy, dx in route_offsets]
            tasks.append(MissionTask(
                f"RESPONSE-{index + 1:02d}", "incident_assessment",
                {"flight", "incident_assessment"}, route, resource.resource_id,
                sector="INCIDENT",
            ))
        return MissionPlan(
            config.mission_id, tasks, 12.0,
            rationale=["Prioridad alta", "Recursos complementarios para evaluación del incidente"],
        )
