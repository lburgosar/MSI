"""Registro JSONL append-only de la sesión operacional."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

from domain.serialization import to_primitive


class OperationalTraceRecorder:
    """Cada línea es autosuficiente y puede alimentar Replay o datasets."""

    def __init__(self, mission_id: str, directory: Path) -> None:
        directory.mkdir(parents=True, exist_ok=True)
        self.path = directory / f"{mission_id}.jsonl"

    def record(self, record_type: str, payload: Any) -> None:
        record = {
            "timestamp": datetime.now().isoformat(timespec="milliseconds"),
            "record_type": record_type,
            "payload": to_primitive(payload),
        }
        with self.path.open("a", encoding="utf-8") as stream:
            stream.write(json.dumps(record, ensure_ascii=False) + "\n")
