from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "manager"))

from msi_next.environment import Evidence, EnvironmentFeature, EnvironmentModel, JsonEnvironmentRepository, PersistenceClass
from msi_next.observations import Observation, ObservationKind
from msi_next.operational_commands import CommandSupport, OperationalCommand, OperationalCommandType


class MsiNextContractTests(unittest.TestCase):
    def evidence(self) -> Evidence:
        return Evidence("survey-2026", "2026-09-03T08:00:00", .92, 86400, .15)

    def test_environment_persists_geometry_and_evidence(self) -> None:
        model = EnvironmentModel("las-marias", "Finca Las Marías")
        model.upsert(EnvironmentFeature(
            "lot-north", "field_boundary",
            {"type": "Polygon", "coordinates": [[[-58.4, -34.6], [-58.39, -34.6], [-58.4, -34.6]]]},
            PersistenceClass.PERSISTENT, self.evidence(), {"label": "Lote Norte"},
        ))
        with tempfile.TemporaryDirectory() as directory:
            path = JsonEnvironmentRepository(Path(directory)).save(model)
            payload = json.loads(path.read_text(encoding="utf-8"))
        self.assertEqual(payload["coordinate_reference_system"], "EPSG:4326")
        self.assertEqual(payload["features"][0]["evidence"]["accuracy_m"], .15)

    def test_dynamic_knowledge_can_expire_without_deleting_stable_boundaries(self) -> None:
        model = EnvironmentModel("farm", "Farm")
        for identifier, persistence in (("boundary", PersistenceClass.PERSISTENT), ("vehicle", PersistenceClass.DYNAMIC)):
            model.upsert(EnvironmentFeature(identifier, identifier, {"type": "Point", "coordinates": [0, 0]}, persistence, self.evidence()))
        model.remove_dynamic()
        self.assertEqual(set(model.features), {"boundary"})

    def test_observation_is_evidence_not_a_decision(self) -> None:
        observation = Observation("obs-1", ObservationKind.THERMAL_ANOMALY, {"type": "Point", "coordinates": [-58.4, -34.6]}, self.evidence(), "D3")
        self.assertFalse(hasattr(observation, "selected_action"))

    def test_critical_command_declares_support_and_confirmation_separately(self) -> None:
        command = OperationalCommand("cmd-1", OperationalCommandType.ABORT, "mission-1", "operator", "2026-09-03T08:00:00", support=CommandSupport.ADAPTER_REQUIRED, requires_confirmation=True)
        self.assertTrue(command.critical)
        self.assertTrue(command.executable)
        self.assertTrue(command.requires_confirmation)

    def test_unsupported_command_never_looks_executable(self) -> None:
        command = OperationalCommand("cmd-2", OperationalCommandType.HOLD, "mission-1", "operator", "2026-09-03T08:00:00")
        self.assertFalse(command.executable)


if __name__ == "__main__":
    unittest.main()
