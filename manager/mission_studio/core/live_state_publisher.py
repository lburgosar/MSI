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
import time
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
    ) -> bool:
        """
        Publica el estado mediante escritura atómica.

        Primero escribe un archivo temporal y después reemplaza el JSON real.
        Así el monitor no intenta leer un archivo incompleto.
        """

        temporary_file = self.state_file.with_suffix(".tmp")

        # Windows puede impedir durante unos milisegundos el reemplazo si
        # Mission Monitor o OneDrive mantienen abierto el archivo anterior.
        # Perder una muestra de telemetría es preferible a cerrar la HMI; la
        # siguiente publicación llegará como máximo 100 ms después.
        for attempt in range(8):
            try:
                with temporary_file.open("w", encoding="utf-8") as file:
                    json.dump(state, file, ensure_ascii=False, indent=4)

                temporary_file.replace(self.state_file)
                return True
            except OSError:
                if attempt < 7:
                    time.sleep(0.005)

        return False
