"""
===============================================================================
MSI Mission Studio - Mission Log
===============================================================================

Registra el ciclo de vida completo de una misión.

Cada misión genera:

1. Un archivo JSON estructurado.
2. Un archivo TXT legible como reporte final.

El registro incluye:

- creación;
- ubicación;
- acción;
- comandos del usuario;
- decisiones futuras de MSI;
- cambios de estado;
- finalización.

===============================================================================
"""

from __future__ import annotations

import json

from datetime import datetime
from pathlib import Path
from uuid import uuid4


class MissionLog:
    """
    Registro persistente de una misión individual.
    """

    def __init__(
        self,
        action: str,
        location: str,
    ) -> None:
        self.action = action
        self.location = location

        self.mission_id = (
            datetime.now().strftime("%Y%m%d-%H%M%S")
            + "-"
            + uuid4().hex[:6]
        )

        mission_studio_root = (
            Path(__file__).resolve().parent.parent
        )

        self.logs_directory = (
            mission_studio_root
            / "data"
            / "mission_logs"
        )

        self.logs_directory.mkdir(
            parents=True,
            exist_ok=True,
        )

        self.json_file = (
            self.logs_directory
            / f"{self.mission_id}.json"
        )

        self.report_file = (
            self.logs_directory
            / f"{self.mission_id}-report.txt"
        )

        self.started_at = datetime.now()
        self.status = "preparing"
        self.events: list[dict[str, str]] = []

        self.add_event(
            event_type="mission_created",
            message=(
                f"Misión de {self.action} creada "
                f"para {self.location}."
            ),
        )

    @staticmethod
    def current_timestamp() -> str:
        """
        Genera una marca temporal legible.
        """

        return datetime.now().isoformat(
            timespec="seconds"
        )

    def add_event(
        self,
        event_type: str,
        message: str,
    ) -> None:
        """
        Añade un evento al registro y guarda inmediatamente.
        """

        event = {
            "timestamp": self.current_timestamp(),
            "type": event_type,
            "message": message,
        }

        self.events.append(event)
        self.save_json()

    def set_status(
        self,
        status: str,
        message: str,
    ) -> None:
        """
        Cambia el estado de la misión y registra la transición.
        """

        self.status = status

        self.add_event(
            event_type="status_changed",
            message=message,
        )

    def save_json(self) -> None:
        """
        Guarda el estado completo de la misión.
        """

        data = {
            "mission_id": self.mission_id,
            "action": self.action,
            "location": self.location,
            "status": self.status,
            "started_at": self.started_at.isoformat(
                timespec="seconds"
            ),
            "events": self.events,
        }

        with self.json_file.open(
            "w",
            encoding="utf-8",
        ) as file:
            json.dump(
                data,
                file,
                ensure_ascii=False,
                indent=4,
            )

    def finalize(
        self,
        result: str = "completed",
    ) -> None:
        """
        Finaliza la misión y genera un reporte legible.
        """

        finished_at = datetime.now()
        duration = finished_at - self.started_at

        self.status = result

        self.add_event(
            event_type="mission_finished",
            message=(
                f"Misión finalizada con estado: {result}."
            ),
        )

        lines = [
            "MSI MISSION REPORT",
            "=" * 72,
            "",
            f"Mission ID: {self.mission_id}",
            f"Acción: {self.action}",
            f"Ubicación: {self.location}",
            f"Estado final: {self.status}",
            f"Inicio: {self.started_at.isoformat(timespec='seconds')}",
            f"Finalización: {finished_at.isoformat(timespec='seconds')}",
            f"Duración: {duration}",
            "",
            "EVENTOS",
            "-" * 72,
        ]

        for event in self.events:
            lines.append(
                f"[{event['timestamp']}] "
                f"{event['type']}: "
                f"{event['message']}"
            )

        lines.extend(
            [
                "",
                "=" * 72,
                "Reporte generado automáticamente por MSI Mission Studio.",
            ]
        )

        self.report_file.write_text(
            "\n".join(lines),
            encoding="utf-8",
        )