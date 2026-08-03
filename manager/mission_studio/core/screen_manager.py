"""
===============================================================================
MSI Mission Studio - Screen Manager
===============================================================================

Este módulo administra la pantalla activa de MSI Mission Studio.

Responsabilidades:

- mantener una referencia a la pantalla actualmente visible;
- delegar eventos, actualizaciones y renderizado;
- permitir futuras transiciones entre pantallas.

MissionStudio utiliza este administrador sin necesitar conocer los detalles
internos de HomeScreen, SimulationScreen u otras pantallas futuras.

===============================================================================
"""

from __future__ import annotations

import pygame

from ui.screens.home_screen import HomeScreen


class ScreenManager:
    """
    Administra la pantalla activa de MSI Mission Studio.
    """

    def __init__(self) -> None:
        """
        Crea la pantalla inicial de la aplicación.
        """

        self.active_screen = HomeScreen()

    def process_event(self, event: pygame.event.Event) -> None:
        """
        Entrega un evento a la pantalla activa.
        """

        self.active_screen.process_event(event)

    def update(self) -> None:
        """
        Actualiza la pantalla activa.
        """

        self.active_screen.update()

    def render(self, screen: pygame.Surface) -> None:
        """
        Solicita a la pantalla activa que dibuje su contenido.
        """

        self.active_screen.render(screen)