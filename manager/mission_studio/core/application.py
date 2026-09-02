"""
===============================================================================
MSI Mission Studio - Application
===============================================================================

Contiene la aplicación principal.

Responsabilidades:

- inicializar Pygame;
- crear una ventana redimensionable;
- administrar el ciclo principal;
- procesar teclado, mouse y eventos táctiles;
- controlar el tiempo entre cuadros;
- delegar la interfaz al ScreenManager.

===============================================================================
"""

from __future__ import annotations

import os

import pygame

from core import theme
from core.screen_manager import ScreenManager


class MissionStudio:
    """
    Aplicación principal de MSI Mission Studio.
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

        pygame.display.set_caption(theme.WINDOW_TITLE)

        self.clock = pygame.time.Clock()
        self.running = True
        self.delta_time = 0.0

        self.screen_manager = ScreenManager()

    def process_events(self) -> None:
        """
        Procesa eventos globales y los delega a la pantalla activa.
        """

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                continue

            if event.type == pygame.VIDEORESIZE:
                new_width = max(
                    theme.MIN_WINDOW_WIDTH,
                    event.w,
                )

                new_height = max(
                    theme.MIN_WINDOW_HEIGHT,
                    event.h,
                )

                self.screen = pygame.display.set_mode(
                    (
                        new_width,
                        new_height,
                    ),
                    pygame.RESIZABLE,
                )

                continue

            self.screen_manager.process_event(event)

    def update(self) -> None:
        """
        Actualiza la pantalla activa.
        """

        self.screen_manager.update(self.delta_time)

    def render(self) -> None:
        """
        Renderiza la pantalla activa.
        """

        self.screen_manager.render(self.screen)
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
