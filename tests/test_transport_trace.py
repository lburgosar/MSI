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


if __name__ == "__main__":
    unittest.main()
