"""
Publicador manual de prueba para MSI Mission Monitor.
"""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any


STATE_FILE = (
    Path(__file__).resolve().parent
    / "live_mission_state.json"
)


def publish(state: dict[str, Any]) -> None:
    """
    Escribe el estado de forma temporal y luego lo reemplaza.

    Esto reduce la posibilidad de que el monitor lea un JSON incompleto.
    """

    temporary_file = STATE_FILE.with_suffix(
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

    temporary_file.replace(STATE_FILE)


states = [
    {
        "status": "interviewing",
        "phase": "interview",
        "action": "Pulverización",
        "location": "",
        "progress_percent": 0,
        "connected_nodes": 4,
        "assigned_nodes": 0,
        "operational_nodes": 3,
        "wind_m_s": 2.7,
        "temperature_c": 21,
        "link_quality_percent": 96,
        "latest_decision": {
            "summary": "Recopilando ubicación",
            "reason": "Falta definir el área de trabajo",
            "impact": "La misión todavía no puede planificarse",
            "intervention_required": True
        }
    },
    {
        "status": "analyzing",
        "phase": "capability_check",
        "action": "Pulverización",
        "location": "Finca Los Álamos",
        "progress_percent": 0,
        "connected_nodes": 4,
        "assigned_nodes": 0,
        "operational_nodes": 3,
        "wind_m_s": 2.7,
        "temperature_c": 21,
        "link_quality_percent": 96,
        "latest_decision": {
            "summary": "Validando pulverizadores",
            "reason": "La misión requiere capacidad de aplicación",
            "impact": "2 nodos resultaron compatibles",
            "intervention_required": False
        }
    },
    {
        "status": "planning",
        "phase": "planning",
        "action": "Pulverización",
        "location": "Finca Los Álamos",
        "progress_percent": 0,
        "connected_nodes": 4,
        "assigned_nodes": 2,
        "operational_nodes": 3,
        "wind_m_s": 2.7,
        "temperature_c": 21,
        "link_quality_percent": 96,
        "latest_decision": {
            "summary": "Asignar 2 nodos",
            "reason": "Ambos poseen pulverizador operativo",
            "impact": "Tiempo estimado: 24 minutos",
            "intervention_required": False
        }
    }
]


for index, state in enumerate(
    states,
    start=1,
):
    print(
        f"Publicando estado {index}..."
    )

    publish(state)
    time.sleep(3)

print("Prueba finalizada.")