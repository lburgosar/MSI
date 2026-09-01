"""
===============================================================================
MSI Core - Mission State
===============================================================================

Representa el estado vivo y compartido de una misión.

Mission Studio modifica este objeto según la conversación con el operador.
MissionState publica los cambios para que Mission Monitor, el simulador y
futuros componentes puedan observar la misma verdad operacional.

===============================================================================
"""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from core.live_state_publisher import LiveStatePublisher


class MissionState:
    """
    Fuente de verdad del estado operativo de una misión.
    """

    def __init__(self) -> None:
        self.publisher = LiveStatePublisher()

        self.data: dict[str, Any] = {
            "status": "idle",
            "phase": "waiting",
            "action": "",
            "location": "",
            "progress_percent": 0,
            "drones": [],
            "active_drones": 0,
            "latest_event": "Esperando misión",

            # Valores simulados para la primera demo.
            # Luego vendrán del Capability Manager.
            "connected_nodes": 4,
            "assigned_nodes": 0,
            "operational_nodes": 3,

            "wind_m_s": 2.7,
            "temperature_c": 21,
            "link_quality_percent": 96,

            "latest_decision": {
                "summary": "Esperando planificación",
                "reason": "",
                "impact": "",
                "intervention_required": False,
            },
        }

        self.publish()

    def publish(self) -> None:
        """
        Publica una copia del estado actual.
        """

        self.publisher.publish(
            deepcopy(self.data)
        )

    def update(
        self,
        **changes: Any,
    ) -> None:
        """
        Aplica varios cambios y publica una sola vez.
        """

        self.data.update(changes)
        self.publish()

    def set_decision(
        self,
        summary: str,
        reason: str = "",
        impact: str = "",
        intervention_required: bool = False,
    ) -> None:
        """
        Actualiza la última explicación o decisión de MSI.
        """

        self.data["latest_decision"] = {
            "summary": summary,
            "reason": reason,
            "impact": impact,
            "intervention_required": intervention_required,
        }

        self.publish()

    def start_interview(self) -> None:
        """
        Indica que MSI comenzó a entrevistar al operador.
        """

        self.data.update(
            {
                "status": "interviewing",
                "phase": "interview",
                "progress_percent": 0,
            }
        )

        self.data["latest_decision"] = {
            "summary": "Recopilando intención",
            "reason": "MSI necesita conocer el objetivo de la misión",
            "impact": "La misión todavía no puede planificarse",
            "intervention_required": True,
        }

        self.publish()

    def set_action(
        self,
        action: str,
    ) -> None:
        """
        Registra la acción interpretada por el HMI.
        """

        self.data["action"] = action
        self.data["status"] = "interviewing"
        self.data["phase"] = "interview"

        self.data["latest_decision"] = {
            "summary": "Acción reconocida",
            "reason": f"El operador solicitó una misión de {action.lower()}",
            "impact": "Falta definir la ubicación",
            "intervention_required": True,
        }

        self.publish()

    def set_location(
        self,
        location: str,
    ) -> None:
        """
        Registra la ubicación y comienza el análisis.
        """

        self.data["location"] = location
        self.data["status"] = "analyzing"
        self.data["phase"] = "capability_check"

        self.data["latest_decision"] = {
            "summary": "Validando capacidades disponibles",
            "reason": (
                "MSI debe comprobar que el hardware puede realizar "
                "la misión solicitada"
            ),
            "impact": "Preparando evaluación de nodos",
            "intervention_required": False,
        }

        self.publish()

    def begin_planning(self) -> None:
        """
        Inicia la planificación preliminar.
        """

        self.data.update(
            {
                "status": "planning",
                "phase": "planning",
                "assigned_nodes": 2,
                "progress_percent": 0,
            }
        )

        self.data["latest_decision"] = {
            "summary": "Se recomiendan 2 nodos",
            "reason": (
                "Son los nodos simulados que declaran capacidad "
                "de pulverización"
            ),
            "impact": "Plan preliminar en preparación",
            "intervention_required": False,
        }

        self.publish()

    def begin_execution(self) -> None:
        """
        Marca la misión como aceptada y en ejecución.
        """

        self.data.update(
            {
                "status": "running",
                "phase": "execution",
                "progress_percent": 0,
                "latest_event": "Ejecución iniciada",
            }
        )

        self.data["latest_decision"] = {
            "summary": "Misión iniciada",
            "reason": "El plan fue aceptado por el operador",
            "impact": "Los nodos comienzan la ejecución",
            "intervention_required": False,
        }

        self.publish()

    def complete(self) -> None:
        """
        Marca la misión como finalizada correctamente.
        """

        self.data.update(
            {
                "status": "completed",
                "phase": "finished",
                "progress_percent": 100,
                "active_drones": 0,
                "latest_event": "Objetivos alcanzados",
            }
        )

        self.data["latest_decision"] = {
            "summary": "Misión completada",
            "reason": "Se alcanzó el objetivo planificado",
            "impact": "Reporte final disponible",
            "intervention_required": False,
        }

        self.publish()

    def cancel(self) -> None:
        """
        Marca la misión como cancelada.
        """

        self.data.update(
            {
                "status": "cancelled",
                "phase": "finished",
            }
        )

        self.data["latest_decision"] = {
            "summary": "Misión cancelada",
            "reason": "El operador finalizó la misión antes de completarla",
            "impact": "Se generará un registro de cancelación",
            "intervention_required": False,
        }

        self.publish()
