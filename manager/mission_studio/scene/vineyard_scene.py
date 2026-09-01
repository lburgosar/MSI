"""
===============================================================================
MSI Mission Studio - Vineyard Scene
===============================================================================

Representa un viñedo adaptable dentro del workspace.

La escena recibe un pygame.Rect calculado por el sistema de layout.
Esto permite redimensionarla para escritorio, tablet o pantalla angosta.

===============================================================================
"""

from __future__ import annotations

import pygame

from core import theme
from presentation.simulation_view import SimulationView


class VineyardScene:
    """
    Escenario visual parametrizable para viñedos.
    """

    def __init__(
        self,
        location_name: str,
        row_count: int = 12,
    ) -> None:
        self.location_name = location_name
        self.row_count = row_count
        self.simulation_view = SimulationView()
        self.drones: list[dict] = []

        self.title_font = pygame.font.SysFont(
            "Segoe UI",
            17,
            bold=True,
        )

        self.label_font = pygame.font.SysFont(
            "Segoe UI",
            13,
        )

    def update(self, delta_time: float) -> None:
        """La escena no mueve recursos; sólo representa el estado recibido."""

    def set_drones(self, drones: list[dict]) -> None:
        self.drones = drones

    def select_at(self, position: tuple[int, int]) -> str | None:
        return self.simulation_view.select_at(position)

    @staticmethod
    def get_grid_rect(workspace_rect: pygame.Rect) -> pygame.Rect:
        return pygame.Rect(
            workspace_rect.left + 62,
            workspace_rect.top + 60,
            max(100, workspace_rect.width - 124),
            max(100, workspace_rect.height - 105),
        )

    def render(
        self,
        screen: pygame.Surface,
        workspace_rect: pygame.Rect,
    ) -> None:
        """
        Dibuja el viñedo dentro del espacio recibido.
        """

        pygame.draw.rect(
            screen,
            theme.PANEL,
            workspace_rect,
            border_radius=22,
        )

        pygame.draw.rect(
            screen,
            theme.BORDER,
            workspace_rect,
            width=2,
            border_radius=22,
        )

        title = self.title_font.render(
            f"{self.location_name} · Workspace de misión",
            True,
            theme.TEXT,
        )

        screen.blit(
            title,
            (
                workspace_rect.left + 24,
                workspace_rect.top + 18,
            ),
        )

        grid_rect = self.get_grid_rect(workspace_rect)

        # Cuadrícula de referencia para un mapa futuro.
        grid_step = max(
            28,
            min(50, grid_rect.width // 14),
        )

        for x in range(
            grid_rect.left,
            grid_rect.right + 1,
            grid_step,
        ):
            pygame.draw.line(
                screen,
                theme.GRID_LINE,
                (x, grid_rect.top),
                (x, grid_rect.bottom),
                width=1,
            )

        for y in range(
            grid_rect.top,
            grid_rect.bottom + 1,
            grid_step,
        ):
            pygame.draw.line(
                screen,
                theme.GRID_LINE,
                (grid_rect.left, y),
                (grid_rect.right, y),
                width=1,
            )

        available_height = grid_rect.height

        row_spacing = max(
            14,
            available_height // max(
                self.row_count,
                1,
            ),
        )

        total_rows_height = (
            self.row_count - 1
        ) * row_spacing

        first_row_y = (
            grid_rect.centery
            - total_rows_height // 2
        )

        for row_index in range(self.row_count):
            row_y = (
                first_row_y
                + row_index * row_spacing
            )

            pygame.draw.line(
                screen,
                theme.VINEYARD_ROW,
                (
                    grid_rect.left + 30,
                    row_y,
                ),
                (
                    grid_rect.right - 30,
                    row_y,
                ),
                width=max(2, min(5, row_spacing // 5)),
            )

            if workspace_rect.width >= 700:
                label = self.label_font.render(
                    f"H{row_index + 1:02d}",
                    True,
                    theme.SECONDARY_TEXT,
                )

                screen.blit(
                    label,
                    (
                        grid_rect.left - 34,
                        row_y - 7,
                    ),
                )

        west = self.label_font.render(
            "Cabecera oeste",
            True,
            theme.SECONDARY_TEXT,
        )

        east = self.label_font.render(
            "Cabecera este",
            True,
            theme.SECONDARY_TEXT,
        )

        screen.blit(
            west,
            (
                workspace_rect.left + 18,
                workspace_rect.bottom - 29,
            ),
        )

        screen.blit(
            east,
            (
                workspace_rect.right
                - east.get_width()
                - 18,
                workspace_rect.bottom - 29,
            ),
        )

        self.simulation_view.render(
            screen,
            grid_rect,
            self.drones,
            interactive=True,
        )
