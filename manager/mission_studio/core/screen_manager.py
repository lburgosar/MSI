"""
===============================================================================
MSI Mission Studio - Screen Manager
===============================================================================

Administra el flujo entre SplashScreen, HomeScreen y MissionScreen.

También conserva el mismo MissionState cuando la entrevista pasa a la
planificación, evitando crear estados independientes para una sola misión.

===============================================================================
"""

from __future__ import annotations

import pygame

from ui.screens.home_screen import HomeScreen
from ui.screens.mission_screen import MissionScreen
from ui.screens.splash_screen import SplashScreen


class ScreenManager:
    """
    Administra la pantalla activa.
    """

    def __init__(self) -> None:
        self.active_screen = SplashScreen()

    def process_event(
        self,
        event: pygame.event.Event,
    ) -> None:
        self.active_screen.process_event(event)

    def update(
        self,
        delta_time: float,
    ) -> None:
        self.active_screen.update(delta_time)

        next_screen = (
            self.active_screen.get_next_screen()
        )

        if next_screen == "home":
            self.active_screen = HomeScreen()

        elif next_screen == "mission":
            mission_text = (
                self.active_screen.get_mission_text()
            )

            mission_state = (
                self.active_screen.get_mission_state()
            )

            self.active_screen = MissionScreen(
                mission_text=mission_text,
                mission_state=mission_state,
            )

        elif next_screen == "home_from_mission":
            self.active_screen = HomeScreen()

    def render(
        self,
        screen: pygame.Surface,
    ) -> None:
        self.active_screen.render(screen)