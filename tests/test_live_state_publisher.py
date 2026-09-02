from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPOSITORY_ROOT / "manager" / "mission_studio"))

from core.live_state_publisher import LiveStatePublisher


class LiveStatePublisherTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.publisher = LiveStatePublisher()
        self.publisher.shared_directory = Path(self.temporary_directory.name)
        self.publisher.state_file = self.publisher.shared_directory / "state.json"

    def tearDown(self) -> None:
        self.temporary_directory.cleanup()

    def test_retries_a_temporarily_locked_state_file(self) -> None:
        original_replace = Path.replace
        attempts = 0

        def intermittently_locked(path: Path, target: Path) -> Path:
            nonlocal attempts
            attempts += 1
            if attempts < 3:
                raise PermissionError(13, "Acceso denegado")
            return original_replace(path, target)

        with patch.object(Path, "replace", intermittently_locked):
            published = self.publisher.publish({"status": "running"})

        self.assertTrue(published)
        self.assertEqual(attempts, 3)
        self.assertTrue(self.publisher.state_file.exists())

    def test_drops_one_sample_instead_of_crashing_after_retries(self) -> None:
        with patch.object(Path, "replace", side_effect=PermissionError(13, "Acceso denegado")):
            published = self.publisher.publish({"status": "running"})

        self.assertFalse(published)


if __name__ == "__main__":
    unittest.main()
