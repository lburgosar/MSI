"""
===============================================================================
MSI Mission Monitor - Live State Reader
===============================================================================

Lee el estado compartido publicado por MSI Mission Studio.

Al iniciar el monitor, comienza siempre desde un estado seguro de espera.
Después adopta los cambios publicados por Mission Studio.

===============================================================================
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class LiveStateReader:
    """
    Recupera el estado vivo desde el archivo JSON compartido.
    """

    def __init__(self) -> None:
        manager_directory = Path(__file__).resolve().parent.parent

        self.state_file = (
            manager_directory
            / "shared"
            / "live_mission_state.json"
        )

        self.last_valid_state = self.get_default_state()

        # Ignora el contenido viejo hasta que el archivo vuelva a cambiar.
        self.last_modified_time = (
            self.state_file.stat().st_mtime
            if self.state_file.exists()
            else None
        )

    @staticmethod
    def get_default_state() -> dict[str, Any]:
        """
        Estado seguro mostrado cuando todavía no hay una misión nueva.
        """

        return {
            "status": "idle",
            "phase": "waiting",
            "action": "",
            "location": "",
            "progress_percent": 0,
            "connected_nodes": 0,
            "assigned_nodes": 0,
            "operational_nodes": 0,
            "wind_m_s": None,
            "temperature_c": None,
            "link_quality_percent": None,
            "latest_decision": {
                "summary": "Esperando planificación",
                "reason": "",
                "impact": "",
                "intervention_required": False,
            },
        }

    def read(self) -> dict[str, Any]:
        """
        Lee solamente estados publicados después de iniciar el monitor.
        """

        if not self.state_file.exists():
            return self.last_valid_state

        try:
            modified_time = self.state_file.stat().st_mtime

            # El archivo todavía conserva el estado de una ejecución anterior.
            if modified_time == self.last_modified_time:
                return self.last_valid_state

            with self.state_file.open(
                "r",
                encoding="utf-8",
            ) as file:
                state = json.load(file)

            if isinstance(state, dict):
                self.last_valid_state = state
                self.last_modified_time = modified_time

        except (json.JSONDecodeError, OSError):
            pass

        return self.last_valid_state