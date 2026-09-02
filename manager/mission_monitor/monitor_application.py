"""
===============================================================================
MSI Mission Monitor - Application
===============================================================================

Aplicación principal del monitor operativo.

===============================================================================
"""

from __future__ import annotations

import os

import pygame

import theme
from monitor_screen import MonitorScreen


class MissionMonitor:
    """
    Aplicación principal del Mission Monitor.
    """

    def __init__(self) -> None:
        pygame.init()

        window_width = int(os.environ.get("MSI_WINDOW_WIDTH", theme.WINDOW_WIDTH))
        window_height = int(os.environ.get("MSI_WINDOW_HEIGHT", theme.WINDOW_HEIGHT))

        self.screen = pygame.display.set_mode(
            (
                window_width,
                window_height,
            ),
            pygame.RESIZABLE,
        )

        pygame.display.set_caption(
            theme.WINDOW_TITLE
        )

        self.clock = pygame.time.Clock()
        self.running = True
        self.delta_time = 0.0

        self.monitor_screen = MonitorScreen()

    def process_events(self) -> None:
        """
        Procesa cierre y redimensionamiento.
        """

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

    def update(self) -> None:
        """
        Actualiza el monitor.
        """

        self.monitor_screen.update(
            self.delta_time
        )

    def render(self) -> None:
        """
        Renderiza la interfaz.
        """

        self.monitor_screen.render(
            self.screen
        )

        pygame.display.flip()

    def run(self) -> None:
        """
        Ejecuta el ciclo principal.
        """

        try:
            while self.running:
                self.process_events()
                self.update()
                self.render()

                self.delta_time = (
                    self.clock.tick(theme.FPS) / 1000.0
                )

        finally:
            pygame.quit()
