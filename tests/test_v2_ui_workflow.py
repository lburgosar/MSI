from __future__ import annotations

import os
import sys
import unittest
from pathlib import Path


os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "manager"))
sys.path.insert(0, str(ROOT / "manager" / "mission_studio"))

import pygame

from core.mission_state import MissionState
from ui.screens.v2_mission_screen import MissionScreen


class V2UiWorkflowTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        pygame.init()
        pygame.display.set_mode((1280, 800))

    @classmethod
    def tearDownClass(cls) -> None:
        pygame.quit()

    def test_two_stage_authorization_and_responsive_render(self) -> None:
        screen = MissionScreen("Pulverización · Las Marías", MissionState())
        self.assertEqual(screen.primary_label(), "Autorizar plan")

        screen.primary_action()
        self.assertEqual(screen.primary_label(), "Ejecutar misión")
        screen.primary_action()
        screen.update(1.0)

        self.assertEqual(screen.runtime.status, "running")
        self.assertGreater(screen.runtime.progress_percent(), 0)
        screen.render(pygame.Surface((1280, 800)))
        screen.render(pygame.Surface((1350, 229)))

    def test_numeric_position_changes_provider_and_replans(self) -> None:
        screen = MissionScreen("Pulverización · Las Marías", MissionState())
        original_version = screen.runtime.plan.version
        screen.set_numeric_position("D1", -34.602, -58.401, 4.5)
        resource = screen.provider.get_resource("D1")

        self.assertAlmostEqual(resource.position.latitude, -34.602)
        self.assertAlmostEqual(resource.position.altitude.meters, 4.5)
        self.assertGreater(screen.runtime.plan.version, original_version)


if __name__ == "__main__":
    unittest.main()
