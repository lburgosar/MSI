"""Barrera operacional previa a autorización y ejecución."""

from __future__ import annotations

from domain.mission import (
    MissionConfiguration,
    MissionIntent,
    MissionPlan,
    PreflightFinding,
    PreflightResult,
    PreflightStatus,
)
from domain.resources import Resource


class PreflightService:
    def validate(
        self,
        configuration: MissionConfiguration,
        plan: MissionPlan,
        resources: list[Resource],
    ) -> PreflightResult:
        findings: list[PreflightFinding] = []

        if not plan.tasks:
            findings.append(PreflightFinding(
                "NO_COMPATIBLE_RESOURCE", "critical", "Sin recurso compatible",
                "Ningún recurso disponible declara las capacidades requeridas.",
            ))

        assigned_ids = {task.assigned_resource_id for task in plan.tasks}
        assigned = [resource for resource in resources if resource.resource_id in assigned_ids]
        for resource in assigned:
            if resource.energy.percent <= resource.energy.reserve_percent + 8:
                findings.append(PreflightFinding(
                    "ENERGY_RESERVE", "critical", f"{resource.resource_id} sin reserva suficiente",
                    "La batería disponible no mantiene el margen operacional configurado.",
                ))

        if configuration.intent is MissionIntent.PRECISION_SPRAYING:
            required = plan.estimated_consumption_l
            available = sum(
                resource.consumable.remaining_l
                for resource in assigned
                if resource.consumable is not None
            )
            if available < required:
                findings.append(PreflightFinding(
                    "INSUFFICIENT_PRODUCT", "critical", "Producto insuficiente",
                    f"Requerido {required:.1f} L; disponible {available:.1f} L.",
                ))

            wind = float(configuration.parameters.get("wind_m_s", 0.0))
            limit = configuration.parameters.get("max_wind_m_s")
            if limit is None:
                findings.append(PreflightFinding(
                    "WIND_LIMIT_MISSING", "data", "Falta límite de viento",
                    "MSI requiere una restricción explícita antes de autorizar.",
                ))
            elif wind > float(limit):
                findings.append(PreflightFinding(
                    "WIND_LIMIT", "critical", "Viento fuera de restricción",
                    f"Viento {wind:.1f} m/s; máximo autorizado {float(limit):.1f} m/s.",
                ))

        status = PreflightStatus.READY
        if any(item.severity == "critical" for item in findings):
            status = PreflightStatus.BLOCKED
        elif any(item.severity == "data" for item in findings):
            status = PreflightStatus.REQUIRES_DATA
        else:
            findings.append(PreflightFinding(
                "PREFLIGHT_READY", "info", "Misión lista para autorización",
                "Recursos, energía, restricciones y parámetros mínimos verificados.",
            ))

        return PreflightResult(status, findings)
