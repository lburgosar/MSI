"""Mapa local cartográfico provisional y proyección del estado operacional."""

from __future__ import annotations

from typing import Any

import pygame

from .simulation_view import SimulationView


class OperationalMapView:
    """Provider visual local; puede reemplazarse por tiles sin cambiar Runtime."""

    def __init__(self) -> None:
        self.simulation_view = SimulationView()
        self.title_font = pygame.font.SysFont("Segoe UI", 14, bold=True)
        self.small_font = pygame.font.SysFont("Segoe UI", 11)
        self.state: dict[str, Any] = {}

    def set_state(self, state: dict[str, Any]) -> None:
        self.state = state

    def select_at(self, point: tuple[int, int]) -> str | None:
        return self.simulation_view.select_at(point)

    @staticmethod
    def viewport(rect: pygame.Rect) -> pygame.Rect:
        return rect.inflate(-28, -42).move(0, 10)

    def render(self, screen: pygame.Surface, rect: pygame.Rect, interactive: bool) -> None:
        pygame.draw.rect(screen, (232, 236, 226), rect, border_radius=18)
        pygame.draw.rect(screen, (196, 203, 194), rect, width=1, border_radius=18)
        viewport = self.viewport(rect)

        # Parcelas, camino y curso de agua aportan contexto espacial sin fingir
        # que este provider local es cartografía certificada.
        parcels = [
            pygame.Rect(viewport.left, viewport.top, int(viewport.width * .46), int(viewport.height * .46)),
            pygame.Rect(viewport.left + int(viewport.width * .49), viewport.top, int(viewport.width * .51), int(viewport.height * .46)),
            pygame.Rect(viewport.left, viewport.top + int(viewport.height * .51), int(viewport.width * .58), int(viewport.height * .49)),
            pygame.Rect(viewport.left + int(viewport.width * .61), viewport.top + int(viewport.height * .51), int(viewport.width * .39), int(viewport.height * .49)),
        ]
        colors = ((211, 222, 190), (220, 226, 199), (204, 217, 181), (217, 224, 196))
        for parcel, color in zip(parcels, colors):
            pygame.draw.rect(screen, color, parcel, border_radius=5)
            pygame.draw.rect(screen, (181, 191, 168), parcel, width=1, border_radius=5)
        road_y = viewport.top + int(viewport.height * .485)
        pygame.draw.line(screen, (205, 194, 170), (viewport.left, road_y), (viewport.right, road_y), 8)
        pygame.draw.line(screen, (244, 239, 225), (viewport.left, road_y), (viewport.right, road_y), 2)

        for fraction in (.16, .32, .68, .84):
            x = viewport.left + int(viewport.width * fraction)
            pygame.draw.line(screen, (190, 204, 177), (x, viewport.top), (x, viewport.bottom), 1)

        drones = self.state.get("drones", [])
        self.simulation_view.render(screen, viewport, drones, interactive=interactive)

        scenario = str(self.state.get("scenario", "mission")).replace("_", " ").upper()
        mode = str(self.state.get("mode", "simulation")).upper()
        label = self.title_font.render(f"{scenario}  ·  {mode}  ·  LOCAL MAP PROVIDER", True, (44, 55, 45))
        screen.blit(label, (rect.left + 16, rect.top + 10))
        north = self.small_font.render("N ↑", True, (66, 74, 67))
        screen.blit(north, (rect.right - north.get_width() - 16, rect.top + 11))

        bounds = self.state.get("map", {}).get("bounds", {})
        if bounds and rect.height > 180:
            coordinates = self.small_font.render(
                f"{bounds.get('south', 0):.5f}, {bounds.get('west', 0):.5f}   ↔   "
                f"{bounds.get('north', 0):.5f}, {bounds.get('east', 0):.5f}",
                True,
                (84, 92, 84),
            )
            screen.blit(coordinates, (rect.left + 16, rect.bottom - 18))
