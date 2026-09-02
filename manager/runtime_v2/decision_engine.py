"""Políticas explícitas, trazables y reemplazables de MSI Simulator V2."""

from __future__ import annotations

from domain.mission import DecisionRecord, OperationalEvent


class DecisionEngine:
    """Produce decisiones explicables; no modifica recursos ni simulación."""

    def wind_decision(self, event: OperationalEvent, limit_m_s: float) -> DecisionRecord:
        wind = float(event.data["wind_m_s"])
        return DecisionRecord(
            trigger=event.summary,
            evaluation=f"El viento de {wind:.1f} m/s supera el límite de {limit_m_s:.1f} m/s.",
            alternatives=("continuar fuera de restricción", "modificar parámetros", "pausar aplicación"),
            selected_action="pause_mission",
            reason="No existe una regla validada que garantice una aplicación segura cambiando altura o velocidad.",
            impact="Aplicación pausada; los recursos mantienen posición hasta nueva condición válida.",
            commands=("PAUSE_ASSIGNED_RESOURCES",),
        )

    def resource_reassignment(
        self,
        event: OperationalEvent,
        replacement_id: str | None,
        remaining_waypoints: int,
    ) -> DecisionRecord:
        if replacement_id:
            return DecisionRecord(
                trigger=event.summary,
                evaluation=f"El recurso afectado no puede completar {remaining_waypoints} waypoints pendientes.",
                alternatives=("abortar sector", "pausar misión", f"reasignar a {replacement_id}"),
                selected_action="reassign_remaining_route",
                reason=f"{replacement_id} conserva capacidad, disponibilidad y reserva operacional.",
                impact=f"Ruta pendiente transferida a {replacement_id}; aumenta la estimación de finalización.",
                commands=(f"ASSIGN_REMAINING_ROUTE:{replacement_id}",),
            )
        return DecisionRecord(
            trigger=event.summary,
            evaluation="No existe otro recurso compatible y disponible para completar la ruta pendiente.",
            alternatives=("continuar de forma insegura", "degradar cobertura", "pausar misión"),
            selected_action="pause_mission",
            reason="MSI preserva restricciones de energía, consumible y capacidad.",
            impact="Misión pausada y requiere intervención del operador.",
            commands=("PAUSE_ASSIGNED_RESOURCES",),
        )

    def patrol_anomaly(self, event: OperationalEvent, resource_id: str | None) -> DecisionRecord:
        if resource_id:
            return DecisionRecord(
                trigger=event.summary,
                evaluation="La anomalía requiere confirmación térmica y modifica la prioridad de cobertura.",
                alternatives=("ignorar", "esperar fin de patrulla", f"desviar {resource_id}"),
                selected_action="prioritize_anomaly",
                reason=f"{resource_id} declara thermal_imaging y está disponible.",
                impact="Cobertura del sector se demora; comienza órbita de confirmación.",
                commands=(f"DIVERT_TO_ANOMALY:{resource_id}",),
            )
        return DecisionRecord(
            trigger=event.summary,
            evaluation="No hay sensor térmico operativo disponible.",
            alternatives=("confirmar sólo con RGB", "esperar recurso", "solicitar intervención"),
            selected_action="request_intervention",
            reason="La política exige confirmación térmica para clasificar el evento.",
            impact="Anomalía abierta sin confirmar.",
        )
