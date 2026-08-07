"""
===============================================================================
MSI Core - Live State Publisher
===============================================================================

Publica el estado vivo de una misión en el canal compartido utilizado por
MSI Mission Monitor.

El archivo JSON es un transporte temporal para la demostración. La lógica
superior trabaja con MissionState y no necesita conocer cómo se intercambian
los datos.

===============================================================================
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class LiveStatePublisher:
    """
    Publica de forma segura el estado vivo de MSI.
    """

    def __init__(self) -> None:
        """
        Localiza manager/shared/live_mission_state.json.
        """

        manager_directory = (
            Path(__file__).resolve().parent.parent.parent
        )

        self.shared_directory = (
            manager_directory / "shared"
        )

        self.shared_directory.mkdir(
            parents=True,
            exist_ok=True,
        )

        self.state_file = (
            self.shared_directory
            / "live_mission_state.json"
        )

    def publish(
        self,
        state: dict[str, Any],
    ) -> None:
        """
        Publica el estado mediante escritura atómica.

        Primero escribe un archivo temporal y después reemplaza el JSON real.
        Así el monitor no intenta leer un archivo incompleto.
        """

        temporary_file = self.state_file.with_suffix(
            ".tmp"
        )

        with temporary_file.open(
            "w",
            encoding="utf-8",
        ) as file:
            json.dump(
                state,
                file,
                ensure_ascii=False,
                indent=4,
            )

        temporary_file.replace(
            self.state_file
        )