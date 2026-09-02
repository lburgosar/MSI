from __future__ import annotations

import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "manager"))

from application.demo_catalog import demo_configuration, demo_resources
from domain.mission import MissionIntent
from providers.resources import SimulatedResourceProvider
from runtime_v2.mission_runtime import MissionRuntimeV2
from runtime_v2.scenario_engine import ScenarioEngine


class RuntimeV2DecisionTests(unittest.TestCase):
    def runtime(self, intent: MissionIntent = MissionIntent.PRECISION_SPRAYING) -> MissionRuntimeV2:
        return MissionRuntimeV2(
            demo_configuration(intent), SimulatedResourceProvider(demo_resources())
        )

    def test_execution_requires_preflight_authorization(self) -> None:
        runtime = self.runtime()
        self.assertFalse(runtime.start())
        self.assertTrue(runtime.authorize())
        self.assertTrue(runtime.start())
        self.assertEqual(runtime.status, "running")

    def test_low_product_reassigns_real_remaining_route(self) -> None:
        runtime = self.runtime()
        runtime.authorize()
        runtime.start()
        runtime.update(1.0)
        original_version = runtime.plan.version  # type: ignore[union-attr]

        ScenarioEngine(runtime).set_product("D1", 1.0)

        self.assertGreater(runtime.plan.version, original_version)  # type: ignore[union-attr]
        self.assertTrue(any(item.selected_action == "reassign_remaining_route" for item in runtime.decisions))
        self.assertTrue(any(item.event_type == "replan" for item in runtime.events))

    def test_high_wind_pauses_and_valid_wind_can_resume(self) -> None:
        runtime = self.runtime()
        runtime.authorize()
        runtime.start()
        scenario = ScenarioEngine(runtime)
        scenario.set_wind(7.1, 260)

        self.assertEqual(runtime.status, "paused")
        self.assertEqual(runtime.decisions[-1].selected_action, "pause_mission")
        scenario.set_wind(3.0, 240)
        self.assertTrue(runtime.resume_if_valid())
        self.assertEqual(runtime.status, "running")

    def test_patrol_anomaly_diverts_thermal_resource(self) -> None:
        runtime = self.runtime(MissionIntent.AUTONOMOUS_PATROL)
        runtime.authorize()
        runtime.start()

        ScenarioEngine(runtime).inject_thermal_anomaly(-34.601, -58.398)

        self.assertEqual(runtime.decisions[-1].selected_action, "prioritize_anomaly")
        self.assertEqual(runtime.simulation.drones["D3"].assigned_task, "THERMAL-CONFIRM")  # type: ignore[union-attr]

    def test_snapshot_keeps_simulation_source_explicit(self) -> None:
        snapshot = self.runtime().snapshot()
        self.assertEqual(snapshot["schema_version"], 2)
        self.assertEqual(snapshot["mode"], "simulation")
        self.assertEqual(len(snapshot["resources"]), 4)


if __name__ == "__main__":
    unittest.main()
