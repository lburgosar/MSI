from __future__ import annotations

import sys
import unittest
from pathlib import Path
from typing import Any


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPOSITORY_ROOT / "manager"))
sys.path.insert(0, str(REPOSITORY_ROOT / "manager" / "mission_studio"))

from core.mission_runtime import MissionRuntime


class RecordingMissionState:
    def __init__(self) -> None:
        self.data: dict[str, Any] = {}
        self.execution_started = False
        self.completed = False

    def update(self, **changes: Any) -> None:
        self.data.update(changes)

    def begin_execution(self) -> None:
        self.execution_started = True

    def complete(self) -> None:
        self.completed = True


class MissionRuntimeTests(unittest.TestCase):
    def setUp(self) -> None:
        self.state = RecordingMissionState()
        self.events: list[tuple[str, str]] = []
        self.runtime = MissionRuntime(
            mission_state=self.state,  # type: ignore[arg-type]
            action="Pulverización",
            on_event=lambda event_type, message: self.events.append((event_type, message)),
        )

    def test_plan_exposes_three_assigned_drones_before_execution(self) -> None:
        self.assertTrue(self.runtime.plan_valid)
        self.assertEqual(self.state.data["assigned_nodes"], 3)
        self.assertEqual(len(self.state.data["drones"]), 3)
        self.assertTrue(all(item["status"] == "assigned" for item in self.state.data["drones"]))

    def test_execution_moves_drones_and_completes_mission(self) -> None:
        initial_positions = [item["position"] for item in self.state.data["drones"]]

        self.runtime.start()
        self.runtime.update(1.0)

        moved_positions = [item["position"] for item in self.state.data["drones"]]
        self.assertTrue(self.state.execution_started)
        self.assertNotEqual(initial_positions, moved_positions)
        self.assertGreater(self.state.data["progress_percent"], 0)

        for _ in range(12):
            self.runtime.update(1.0)

        self.assertTrue(self.runtime.completed)
        self.assertTrue(self.state.completed)
        self.assertEqual(self.state.data["progress_percent"], 100)
        self.assertIn(("execution_completed", "Los 3 drones alcanzaron sus objetivos."), self.events)


if __name__ == "__main__":
    unittest.main()
