"""
===============================================================================
MSI Mission Studio - Home Screen
===============================================================================

Este módulo define la pantalla inicial de MSI Mission Studio.

Responsabilidades:

- presentar la identidad visual del producto;
- mostrar la pregunta principal al usuario;
- servir como punto de entrada para la creación de misiones.

Esta pantalla no administra el ciclo principal de la aplicación ni decide
qué pantalla está activa. Esa responsabilidad pertenece al ScreenManager.

===============================================================================
"""

from __future__ import annotations

import pygame

from core import theme


class HomeScreen:
    """
    Pantalla inicial de MSI Mission Studio.
    """

    def __init__(self) -> None:
        """
        Inicializa las tipografías utilizadas por la pantalla.
        """

        pygame.font.init()

        self.title_font = pygame.font.SysFont(
            "Segoe UI",
            theme.TITLE_SIZE,
            bold=True,
        )

        self.subtitle_font = pygame.font.SysFont(
            "Segoe UI",
            theme.SUBTITLE_SIZE,
        )

        self.prompt_font = pygame.font.SysFont(
            "Segoe UI",
            theme.TEXT_SIZE,
        )

    def process_event(self, event: pygame.event.Event) -> None:
        """
        Procesa eventos recibidos por esta pantalla.

        Por ahora HomeScreen no tiene componentes interactivos.
        """

        return

    def update(self) -> None:
        """
        Actualiza la lógica interna de la pantalla.

        Por ahora no existe comportamiento dinámico.
        """

        return

    def render(self, screen: pygame.Surface) -> None:
        """
        Dibuja la pantalla inicial sobre la superficie recibida.
        """

        screen.fill(theme.BACKGROUND)

        title_surface = self.title_font.render(
            "MSI Mission Studio",
            True,
            theme.TEXT,
        )

        subtitle_surface = self.subtitle_font.render(
            "Mission Operating System for Autonomous Swarms",
            True,
            theme.SECONDARY_TEXT,
        )

        prompt_surface = self.prompt_font.render(
            "¿Qué querés lograr hoy?",
            True,
            theme.TEXT,
        )

        title_rect = title_surface.get_rect(
            center=(theme.WINDOW_WIDTH // 2, 235)
        )

        subtitle_rect = subtitle_surface.get_rect(
            center=(theme.WINDOW_WIDTH // 2, 295)
        )

        prompt_rect = prompt_surface.get_rect(
            center=(theme.WINDOW_WIDTH // 2, 430)
        )

        screen.blit(title_surface, title_rect)
        screen.blit(subtitle_surface, subtitle_rect)
        screen.blit(prompt_surface, prompt_rect)