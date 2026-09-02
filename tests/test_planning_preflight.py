from __future__ import annotations

import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "manager"))

from application.demo_catalog import demo_configuration, demo_resources
from domain.mission import MissionIntent, PreflightStatus
from planning.planners import MissionPlanner
from planning.preflight import PreflightService


class PlanningAndPreflightTests(unittest.TestCase):
    def setUp(self) -> None:
        self.planner = MissionPlanner()
        self.preflight = PreflightService()

    def test_spraying_plan_uses_capabilities_and_lawnmower_routes(self) -> None:
        config = demo_configuration(MissionIntent.PRECISION_SPRAYING)
        plan = self.planner.create_plan(config, demo_resources())

        self.assertEqual(len(plan.tasks), 2)
        self.assertTrue(all(task.task_type == "precision_spraying" for task in plan.tasks))
        self.assertGreater(len(plan.tasks[0].route), 2)
        self.assertNotEqual(plan.tasks[0].route[0].longitude, plan.tasks[0].route[1].longitude)

    def test_preflight_blocks_insufficient_product(self) -> None:
        resources = demo_resources()
        resources[0].consumable.remaining_l = 1.0  # type: ignore[union-attr]
        resources[1].consumable.remaining_l = 1.0  # type: ignore[union-attr]
        config = demo_configuration(MissionIntent.PRECISION_SPRAYING)
        plan = self.planner.create_plan(config, resources)
        result = self.preflight.validate(config, plan, resources)

        self.assertEqual(result.status, PreflightStatus.BLOCKED)
        self.assertIn("INSUFFICIENT_PRODUCT", {item.code for item in result.findings})

    def test_preflight_blocks_wind_beyond_explicit_limit(self) -> None:
        config = demo_configuration(MissionIntent.PRECISION_SPRAYING)
        config.parameters["wind_m_s"] = 7.2
        plan = self.planner.create_plan(config, demo_resources())
        result = self.preflight.validate(config, plan, demo_resources())

        self.assertEqual(result.status, PreflightStatus.BLOCKED)
        self.assertIn("WIND_LIMIT", {item.code for item in result.findings})

    def test_secondary_scenarios_produce_distinct_route_geometry(self) -> None:
        resources = demo_resources()
        patrol = self.planner.create_plan(
            demo_configuration(MissionIntent.AUTONOMOUS_PATROL), resources
        )
        emergency = self.planner.create_plan(
            demo_configuration(MissionIntent.EMERGENCY_RESPONSE), resources
        )

        self.assertGreaterEqual(len(patrol.tasks), 2)
        self.assertEqual(patrol.tasks[0].task_type, "area_patrol")
        self.assertEqual(emergency.tasks[0].sector, "INCIDENT")
        self.assertNotEqual(patrol.tasks[0].route, emergency.tasks[0].route)


if __name__ == "__main__":
    unittest.main()
