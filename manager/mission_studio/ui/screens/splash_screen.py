"""
===============================================================================
MSI Mission Studio - Splash Screen
===============================================================================

Muestra brevemente la identidad del producto.

La pantalla desaparece automáticamente y entrega el control a HomeScreen.

===============================================================================
"""

from __future__ import annotations

import pygame

from core import theme


class SplashScreen:
    """
    Pantalla inicial breve de MSI Mission Studio.
    """

    def __init__(self) -> None:
        self.elapsed_time = 0.0
        self.duration = 1.8
        self.next_screen: str | None = None

        self.title_font = pygame.font.SysFont(
            "Segoe UI",
            theme.SPLASH_TITLE_SIZE,
            bold=True,
        )

        self.subtitle_font = pygame.font.SysFont(
            "Segoe UI",
            theme.SUBTITLE_SIZE,
        )

    def process_event(self, event: pygame.event.Event) -> None:
        """
        Permite omitir la presentación presionando una tecla o haciendo clic.
        """

        if event.type in (pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN):
            self.next_screen = "home"

    def update(self, delta_time: float) -> None:
        """
        Cambia automáticamente a HomeScreen al cumplirse la duración.
        """

        self.elapsed_time += delta_time

        if self.elapsed_time >= self.duration:
            self.next_screen = "home"

    def render(self, screen: pygame.Surface) -> None:
        """
        Dibuja la identidad inicial del producto.
        """

        screen.fill(theme.BACKGROUND)
        screen_width, screen_height = screen.get_size()

        title = self.title_font.render(
            "MSI",
            True,
            theme.TEXT,
        )

        product = self.subtitle_font.render(
            "Mission Studio",
            True,
            theme.TEXT,
        )

        description = self.subtitle_font.render(
            "Mission Operating System",
            True,
            theme.SECONDARY_TEXT,
        )

        screen.blit(
            title,
            title.get_rect(
                center=(
                    screen_width // 2,
                    screen_height // 2 - 55,
                )
            ),
        )

        screen.blit(
            product,
            product.get_rect(
                center=(
                    screen_width // 2,
                    screen_height // 2 + 10,
                )
            ),
        )

        screen.blit(
            description,
            description.get_rect(
                center=(
                    screen_width // 2,
                    screen_height // 2 + 55,
                )
            ),
        )

    def get_next_screen(self) -> str | None:
        """
        Devuelve la transición solicitada.
        """

        return self.next_screen

    def get_mission_text(self) -> str:
        """
        SplashScreen no genera una misión.
        """

        return ""
