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
        self.assertFalse(runtime.resume_if_valid())
        self.assertEqual(runtime.status, "paused")
        self.assertEqual(runtime.events[-1].event_type, "resume_rejected")
        self.assertIn("7.1 m/s", runtime.events[-1].summary)
        scenario.set_wind(3.0, 240)
        self.assertTrue(any(
            event.event_type == "conditions_restored" for event in runtime.events[-2:]
        ))
        self.assertTrue(runtime.snapshot()["resume_allowed"])
        self.assertTrue(runtime.resume_if_valid())
        self.assertEqual(runtime.status, "running")

    def test_resource_identity_is_stable_across_replans_and_withdrawals(self) -> None:
        runtime = self.runtime()
        provider = runtime.resource_provider

        self.assertEqual([item.resource_id for item in provider.list_resources()], ["D1", "D2", "D3", "D4"])
        for _ in range(10):
            runtime.plan_mission()
        self.assertEqual([item.resource_id for item in provider.list_resources()], ["D1", "D2", "D3", "D4"])

        provider.withdraw_resource("D4")
        for _ in range(10):
            runtime.plan_mission()
        self.assertEqual([item.resource_id for item in provider.list_resources()], ["D1", "D2", "D3"])

        provider.withdraw_resource("D3")
        runtime.plan_mission()
        active_ids = [item.resource_id for item in provider.list_resources()]
        self.assertEqual(active_ids, ["D1", "D2"])
        self.assertEqual(len(active_ids), len(set(active_ids)))
        assigned_ids = {
            task.assigned_resource_id for task in runtime.plan.tasks if task.assigned_resource_id
        }
        self.assertEqual(assigned_ids, set(active_ids))
        self.assertEqual(len(runtime.snapshot()["resources"]), len(active_ids))
        self.assertEqual(
            {item.resource_id for item in provider.list_catalog()},
            {"D1", "D2", "D3", "D4"},
        )

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

    def test_preflight_explanation_exposes_compatibility_and_constraints(self) -> None:
        snapshot = self.runtime().snapshot()
        explanation = snapshot["preflight_explanation"]

        self.assertEqual(explanation["status"], "ready")
        self.assertEqual(explanation["compatible_ids"], ["D1", "D2"])
        self.assertEqual(explanation["assigned_ids"], ["D1", "D2"])
        self.assertEqual(explanation["area_hectares"], 3.6)
        self.assertEqual(explanation["result"], "MISIÓN VIABLE")
        self.assertTrue(all(check["ok"] for check in explanation["checks"]))

    def test_blocked_preflight_explanation_includes_feasible_alternatives(self) -> None:
        runtime = self.runtime()
        ScenarioEngine(runtime).set_wind(7.2)
        explanation = runtime.snapshot()["preflight_explanation"]

        self.assertEqual(explanation["status"], "blocked")
        finding = next(item for item in explanation["findings"] if item["code"] == "WIND_LIMIT")
        self.assertIn("esperar condiciones válidas", finding["alternatives"])

    def test_pre_execution_wind_change_recomputes_preflight_instead_of_pausing(self) -> None:
        runtime = self.runtime()
        ScenarioEngine(runtime).set_wind(7.0)
        self.assertEqual(runtime.status, "blocked")
        self.assertFalse(runtime.paused)

    def test_emergency_priority_event_diverts_specialized_resource(self) -> None:
        runtime = self.runtime(MissionIntent.EMERGENCY_RESPONSE)
        runtime.authorize()
        runtime.start()
        ScenarioEngine(runtime).inject_thermal_anomaly(-34.600, -58.399)
        self.assertEqual(runtime.simulation.drones["D3"].assigned_task, "THERMAL-CONFIRM")  # type: ignore[union-attr]

    def test_spraying_completes_after_real_route_reassignment(self) -> None:
        runtime = self.runtime()
        runtime.authorize()
        runtime.start()
        runtime.update(2.0)
        ScenarioEngine(runtime).set_product("D1", 1.0)

        for _ in range(2500):
            runtime.update(0.2)
            if runtime.status == "completed":
                break

        self.assertEqual(runtime.status, "completed")
        self.assertEqual(runtime.progress_percent(), 100)
        self.assertTrue(any(event.event_type == "result" for event in runtime.events))


if __name__ == "__main__":
    unittest.main()
