import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "manager"))

from msi_next.workflow import MissionPhase, OperatorWorkflow


class OperatorWorkflowTests(unittest.TestCase):
    def test_requires_geometry_before_preflight(self):
        model = OperatorWorkflow()
        self.assertFalse(model.primary_action(False))
        self.assertEqual(model.phase, MissionPhase.DEFINE)

    def test_guided_path_reaches_execution(self):
        model = OperatorWorkflow()
        self.assertTrue(model.primary_action(True))
        self.assertEqual(model.phase, MissionPhase.PREFLIGHT)
        model.primary_action(True)
        model.tick(6)
        self.assertEqual(model.phase, MissionPhase.CORRECTION)
        model.primary_action(True)
        model.primary_action(True)
        self.assertEqual(model.phase, MissionPhase.EXECUTING)

    def test_wind_visibly_pauses_execution(self):
        model = OperatorWorkflow(phase=MissionPhase.EXECUTING)
        model.inject_wind()
        self.assertEqual(model.phase, MissionPhase.PAUSED)
        self.assertIn("Viento", model.decision)

    def test_execution_completes(self):
        model = OperatorWorkflow(phase=MissionPhase.EXECUTING)
        model.tick(18)
        self.assertEqual(model.phase, MissionPhase.COMPLETE)


if __name__ == "__main__":
    unittest.main()
