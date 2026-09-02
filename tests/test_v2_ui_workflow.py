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

    def test_selected_resource_action_targets_selected_identity_only(self) -> None:
        screen = MissionScreen("Pulverización · Las Marías", MissionState())
        screen.selected_resource_id = "D3"
        original_version = screen.runtime.plan.version

        screen.apply_scenario_action("remove")

        self.assertEqual(screen.provider.get_resource("D3").availability.value, "withdrawn")
        self.assertEqual(screen.provider.get_resource("D1").availability.value, "available")
        self.assertEqual(screen.runtime.plan.version, original_version + 1)

    def test_selection_alone_does_not_increment_plan_version(self) -> None:
        screen = MissionScreen("Pulverización · Las Marías", MissionState())
        surface = pygame.Surface((1280, 800))
        screen.render(surface)
        original_version = screen.runtime.plan.version
        d3_rect = screen.resource_rects["D3"]

        screen.process_event(pygame.event.Event(pygame.MOUSEBUTTONDOWN, pos=d3_rect.center))

        self.assertEqual(screen.selected_resource_id, "D3")
        self.assertEqual(screen.runtime.plan.version, original_version)

    def test_blocked_preflight_exposes_real_finding_in_feedback(self) -> None:
        screen = MissionScreen("Pulverización · Las Marías", MissionState())
        screen.command_text = "viento 7.2 265"

        screen.submit_command()

        self.assertEqual(screen.runtime.status, "blocked")
        self.assertIn("Viento fuera de restricción", screen.feedback_text)
        self.assertIn("7.2 m/s", screen.feedback_text)

    def test_rejected_resume_feedback_is_rendered_in_command_prompt(self) -> None:
        screen = MissionScreen("Pulverización · Las Marías", MissionState())
        screen.primary_action()
        screen.primary_action()
        screen.scenario.set_wind(7.2, 265)
        screen.primary_action()

        self.assertIn("REANUDACIÓN RECHAZADA", screen.feedback_text)
        screen.render(pygame.Surface((1280, 800)))
        self.assertFalse(screen.command_text)


if __name__ == "__main__":
    unittest.main()
