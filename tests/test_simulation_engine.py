from __future__ import annotations

import sys
import unittest
from pathlib import Path


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPOSITORY_ROOT / "manager"))

from simulation.engine import DroneCommand, SimulationEngine, SimulatedDrone


class SimulationEngineTests(unittest.TestCase):
    def setUp(self) -> None:
        self.drone = SimulatedDrone(
            drone_id="MSI-DRONE-01",
            position=(0.0, 0.0),
            capabilities=("spraying",),
        )
        self.engine = SimulationEngine([self.drone], cruise_speed=2.0)

    def test_command_moves_drone_without_assigning_it_inside_engine(self) -> None:
        self.engine.apply_commands(
            [DroneCommand("MSI-DRONE-01", (3.0, 4.0), "spray-row-01")]
        )

        self.engine.update(1.0)

        self.assertEqual(self.drone.status, "moving")
        self.assertAlmostEqual(self.drone.position[0], 1.2)
        self.assertAlmostEqual(self.drone.position[1], 1.6)
        self.assertEqual(self.drone.assigned_task, "spray-row-01")
        self.assertLess(self.drone.battery_percent, 100.0)

    def test_drone_reports_arrival_and_complete_telemetry(self) -> None:
        self.engine.apply_commands(
            [DroneCommand("MSI-DRONE-01", (0.0, 1.0), "inspect-row-01")]
        )

        self.engine.update(1.0)
        telemetry = self.engine.telemetry()[0]

        self.assertEqual(telemetry["status"], "on_task")
        self.assertEqual(telemetry["position"], {"x": 0.0, "y": 1.0})
        self.assertEqual(telemetry["target"], {"x": 0.0, "y": 1.0})
        self.assertEqual(telemetry["capabilities"], ["spraying"])
        self.assertEqual(len(telemetry["trajectory"]), 2)

    def test_unknown_drone_command_is_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "Unknown simulated drone"):
            self.engine.apply_commands(
                [DroneCommand("missing", (1.0, 1.0), "task")]
            )


if __name__ == "__main__":
    unittest.main()
