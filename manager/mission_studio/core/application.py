"""
===============================================================================
MSI Mission Studio - Application
===============================================================================

Este módulo contiene la clase principal de MSI Mission Studio.

La clase MissionStudio es responsable de:

- inicializar Pygame;
- crear la ventana principal;
- administrar el ciclo de ejecución;
- procesar eventos globales;
- delegar la lógica visual al ScreenManager;
- cerrar correctamente los recursos utilizados.

===============================================================================
"""

from __future__ import annotations

import pygame

from core import theme
from core.screen_manager import ScreenManager


class MissionStudio:
    """
    Clase principal de MSI Mission Studio.
    """

    def __init__(self) -> None:
        """
        Inicializa Pygame y los componentes principales de la aplicación.
        """

        pygame.init()

        self.screen = pygame.display.set_mode(
            (
                theme.WINDOW_WIDTH,
                theme.WINDOW_HEIGHT,
            )
        )

        pygame.display.set_caption(theme.WINDOW_TITLE)

        self.clock = pygame.time.Clock()
        self.running = True

        # Administra la pantalla actualmente visible.
        self.screen_manager = ScreenManager()

    def process_events(self) -> None:
        """
        Procesa eventos globales y los delega a la pantalla activa.
        """

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                continue

            self.screen_manager.process_event(event)

    def update(self) -> None:
        """
        Actualiza la pantalla activa.
        """

        self.screen_manager.update()

    def render(self) -> None:
        """
        Renderiza la pantalla activa y presenta el cuadro.
        """

        self.screen_manager.render(self.screen)
        pygame.display.flip()

    def run(self) -> None:
        """
        Ejecuta el ciclo principal de MSI Mission Studio.
        """

        try:
            while self.running:
                self.process_events()
                self.update()
                self.render()

                self.clock.tick(theme.FPS)

        finally:
            pygame.quit()