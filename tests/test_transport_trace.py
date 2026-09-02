from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "manager"))

from traceability.recorder import OperationalTraceRecorder
from transport.channels import CallbackStatePublisher, InMemoryChannel
from application.demo_catalog import demo_configuration, demo_resources
from domain.mission import MissionIntent
from providers.resources import SimulatedResourceProvider
from runtime_v2.mission_runtime import MissionRuntimeV2


class TransportAndTraceTests(unittest.TestCase):
    def test_callback_publisher_hides_concrete_transport_from_runtime(self) -> None:
        states: list[dict[str, object]] = []
        CallbackStatePublisher(states.append).publish({"status": "ready"})
        self.assertEqual(states, [{"status": "ready"}])

    def test_in_memory_channel_preserves_command_order(self) -> None:
        channel: InMemoryChannel[str] = InMemoryChannel()
        channel.send("PLAN")
        channel.send("AUTHORIZE")
        self.assertEqual(channel.receive(), "PLAN")
        self.assertEqual(channel.receive(), "AUTHORIZE")

    def test_trace_is_structured_json_lines(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            recorder = OperationalTraceRecorder("mission-01", Path(directory))
            recorder.record("decision", {"selected_action": "pause_mission"})
            line = json.loads(recorder.path.read_text(encoding="utf-8"))
        self.assertEqual(line["record_type"], "decision")
        self.assertEqual(line["payload"]["selected_action"], "pause_mission")

    def test_completed_runtime_records_reconstructable_outcome(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            recorder = OperationalTraceRecorder("mission-outcome", Path(directory))
            runtime = MissionRuntimeV2(
                demo_configuration(MissionIntent.PRECISION_SPRAYING),
                SimulatedResourceProvider(demo_resources()),
                trace_recorder=recorder,
            )
            runtime.authorize(); runtime.start()
            for _ in range(2500):
                runtime.update(0.2)
                if runtime.status == "completed":
                    break
            records = [json.loads(line) for line in recorder.path.read_text(encoding="utf-8").splitlines()]

        outcome = next(record["payload"] for record in records if record["record_type"] == "outcome")
        self.assertEqual(outcome["result"], "COMPLETADA")
        self.assertEqual(outcome["progress_percent"], 100)
        self.assertEqual(outcome["coverage_hectares"], 3.6)


if __name__ == "__main__":
    unittest.main()
