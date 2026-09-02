"""Representación gráfica del estado simulado, sin lógica de movimiento."""

from __future__ import annotations

from math import cos, radians, sin
from typing import Any

import pygame


class SimulationView:
    """Dibuja drones, objetivos y progreso sobre cualquier escena 2D.

    Las coordenadas operativas están normalizadas entre 0 y 1. El componente
    sólo las proyecta al rectángulo disponible, lo que evita acoplar el estado
    de misión a una resolución desktop y permite reutilizarlo en MSI TAB.
    """

    DRONE_COLOR = (0, 122, 255)
    PATH_COMPLETE = (158, 177, 194)
    PATH_PENDING = (0, 122, 255)
    TARGET_COLOR = (52, 168, 83)
    SELECTED_COLOR = (255, 255, 255)
    TEXT = (30, 30, 32)
    PANEL = (255, 255, 255)
    BORDER = (214, 218, 224)

    def __init__(self) -> None:
        self.selected_drone_id: str | None = None
        self.label_font = pygame.font.SysFont("Segoe UI", 12, bold=True)
        self.detail_font = pygame.font.SysFont("Segoe UI", 13)
        self._hitboxes: dict[str, pygame.Rect] = {}

    @staticmethod
    def project(point: dict[str, float], rect: pygame.Rect) -> tuple[int, int]:
        return (
            rect.left + int(float(point["x"]) * rect.width),
            rect.top + int(float(point["y"]) * rect.height),
        )

    def select_at(self, position: tuple[int, int]) -> str | None:
        selected = next(
            (drone_id for drone_id, area in self._hitboxes.items() if area.collidepoint(position)),
            None,
        )
        self.selected_drone_id = selected
        return selected

    def render(
        self,
        screen: pygame.Surface,
        viewport: pygame.Rect,
        drones: list[dict[str, Any]],
        interactive: bool = True,
    ) -> None:
        self._hitboxes.clear()

        for drone in drones:
            self._render_path(screen, viewport, drone)

        for drone in drones:
            self._render_drone(screen, viewport, drone, interactive)

        if interactive:
            selected = next(
                (item for item in drones if item.get("id") == self.selected_drone_id),
                None,
            )
            if selected is not None:
                self._render_selection_card(screen, viewport, selected)

    def _render_path(
        self,
        screen: pygame.Surface,
        viewport: pygame.Rect,
        drone: dict[str, Any],
    ) -> None:
        trajectory = drone.get("trajectory") or []
        target = drone.get("target")
        position = drone.get("position")

        if not trajectory or not target or not position:
            return

        current = self.project(position, viewport)
        objective = drone.get("objective") or target
        endpoint = self.project(objective, viewport)
        target_radius = 5 if viewport.height < 100 else 8
        waypoint_index = int(drone.get("waypoint_index", 0))
        projected = [self.project(point, viewport) for point in trajectory]
        completed_points = [*projected[: waypoint_index + 1], current]
        pending_points = [current, *projected[waypoint_index + 1:]]
        if len(completed_points) >= 2:
            pygame.draw.lines(screen, self.PATH_COMPLETE, False, completed_points, width=5)
        if len(pending_points) >= 2:
            pygame.draw.lines(screen, self.PATH_PENDING, False, pending_points, width=2)
        pygame.draw.circle(screen, self.PANEL, endpoint, target_radius)
        pygame.draw.circle(screen, self.TARGET_COLOR, endpoint, target_radius, width=2)

    def _render_drone(
        self,
        screen: pygame.Surface,
        viewport: pygame.Rect,
        drone: dict[str, Any],
        interactive: bool,
    ) -> None:
        center = self.project(drone["position"], viewport)
        drone_id = str(drone.get("id", "?"))
        selected = drone_id == self.selected_drone_id
        compact = viewport.height < 100
        marker_radius = 11 if compact else 18
        selection_radius = 15 if compact else 23
        direction_length = 17 if compact else 27

        if selected:
            pygame.draw.circle(screen, self.SELECTED_COLOR, center, selection_radius)
            pygame.draw.circle(screen, self.DRONE_COLOR, center, selection_radius, width=2)

        color = self._resource_color(drone)
        pygame.draw.circle(screen, color, center, marker_radius)

        angle = radians(float(drone.get("orientation_degrees", 0.0)))
        direction = (
            center[0] + int(cos(angle) * direction_length),
            center[1] + int(sin(angle) * direction_length),
        )
        pygame.draw.line(screen, color, center, direction, width=3)
        pygame.draw.circle(screen, self.PANEL, direction, 3)

        # Silueta funcional de multirrotor; el renderer puede cambiar sin tocar
        # el modelo ni la simulación.
        arm = max(5, marker_radius - 5)
        pygame.draw.line(screen, self.PANEL, (center[0] - arm, center[1]), (center[0] + arm, center[1]), 2)
        pygame.draw.line(screen, self.PANEL, (center[0], center[1] - arm), (center[0], center[1] + arm), 2)

        short_id = drone_id.replace("MSI-DRONE-0", "D")
        label = self.label_font.render(short_id, True, self.PANEL)
        screen.blit(label, label.get_rect(center=center))

        if interactive:
            # El hitbox es mayor que el marcador para admitir interacción táctil.
            self._hitboxes[drone_id] = pygame.Rect(center[0] - 28, center[1] - 28, 56, 56)

    @staticmethod
    def _resource_color(drone: dict[str, Any]) -> tuple[int, int, int]:
        capabilities = set(drone.get("capabilities") or [])
        if "precision_spraying" in capabilities:
            return 32, 132, 102
        if "thermal_imaging" in capabilities:
            return 205, 104, 48
        if "communications_relay" in capabilities:
            return 105, 84, 180
        return SimulationView.DRONE_COLOR

    def _render_selection_card(
        self,
        screen: pygame.Surface,
        viewport: pygame.Rect,
        drone: dict[str, Any],
    ) -> None:
        width = min(360, viewport.width - 24)
        card = pygame.Rect(viewport.left + 12, viewport.bottom - 58, width, 46)
        pygame.draw.rect(screen, self.PANEL, card, border_radius=14)
        pygame.draw.rect(screen, self.BORDER, card, width=1, border_radius=14)

        task = drone.get("assigned_task") or "Sin tarea"
        status = str(drone.get("status", "—")).replace("_", " ").title()
        battery = float(drone.get("battery_percent", 0.0))
        text = f"{drone.get('id')}  ·  {task}  ·  {status}  ·  {battery:.0f}%"
        surface = self.detail_font.render(text, True, self.TEXT)
        screen.blit(surface, (card.left + 14, card.centery - surface.get_height() // 2))
