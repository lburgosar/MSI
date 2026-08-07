"""
===============================================================================
MSI Mission Monitor - Monitor Screen
===============================================================================

Muestra en tiempo real el estado compartido de la misión.

La barra lateral es de solo lectura.
La región derecha se reservará para la simulación de los nodos.
===============================================================================
"""

from __future__ import annotations

from typing import Any

import pygame

import theme
from live_state_reader import LiveStateReader


class MonitorScreen:
    """
    Vista principal del Mission Monitor.
    """

    STATUS_LABELS = {
        "idle": "Sin misión activa",
        "interviewing": "Entrevistando al operador",
        "analyzing": "Analizando misión",
        "planning": "Planificando",
        "accepted": "Misión aceptada",
        "running": "Misión en ejecución",
        "paused": "Misión pausada",
        "completed": "Misión completada",
        "cancelled": "Misión cancelada",
    }

    PHASE_LABELS = {
        "waiting": "Esperando",
        "interview": "Precarga",
        "capability_check": "Validación de capacidades",
        "planning": "Planificación",
        "patrol": "Patrullaje",
        "execution": "Ejecución",
        "return": "Retorno",
        "finished": "Finalizada",
    }

    def __init__(self) -> None:
        self.state_reader = LiveStateReader()
        self.state = self.state_reader.read()

        self.refresh_timer = 0.0
        self.refresh_interval = 0.20

        self.title_font = pygame.font.SysFont(
            "Segoe UI",
            24,
            bold=True,
        )

        self.section_font = pygame.font.SysFont(
            "Segoe UI",
            15,
            bold=True,
        )

        self.text_font = pygame.font.SysFont(
            "Segoe UI",
            15,
        )

        self.large_status_font = pygame.font.SysFont(
            "Segoe UI",
            28,
            bold=True,
        )

    def update(self, delta_time: float) -> None:
        """
        Actualiza el estado cinco veces por segundo.
        """

        self.refresh_timer += delta_time

        if self.refresh_timer >= self.refresh_interval:
            self.state = self.state_reader.read()
            self.refresh_timer = 0.0

    @staticmethod
    def format_value(
        value: Any,
        suffix: str = "",
    ) -> str:
        """
        Convierte valores vacíos en una representación legible.
        """

        if value is None or value == "":
            return "—"

        return f"{value}{suffix}"

    def render(self, screen: pygame.Surface) -> None:
        """
        Dibuja la barra lateral y el área operativa.
        """

        screen.fill(theme.BACKGROUND)

        width, height = screen.get_size()

        sidebar_width = int(
            width * theme.SIDEBAR_RATIO
        )

        sidebar_width = max(
            theme.MIN_SIDEBAR_WIDTH,
            min(
                theme.MAX_SIDEBAR_WIDTH,
                sidebar_width,
            ),
        )

        sidebar_rect = pygame.Rect(
            0,
            0,
            sidebar_width,
            height,
        )

        simulation_rect = pygame.Rect(
            sidebar_width,
            0,
            width - sidebar_width,
            height,
        )

        pygame.draw.rect(
            screen,
            theme.PANEL,
            sidebar_rect,
        )

        pygame.draw.line(
            screen,
            theme.BORDER,
            (sidebar_rect.right, 0),
            (sidebar_rect.right, height),
            width=1,
        )

        self.render_sidebar(
            screen,
            sidebar_rect,
        )

        self.render_main_area(
            screen,
            simulation_rect,
        )

    def render_sidebar(
        self,
        screen: pygame.Surface,
        sidebar_rect: pygame.Rect,
    ) -> None:
        """
        Dibuja información operativa de solo lectura.
        """

        x = sidebar_rect.left + 28
        y = 30

        title = self.title_font.render(
            "MSI Mission Monitor",
            True,
            theme.TEXT,
        )

        screen.blit(title, (x, y))

        status_code = self.state.get(
            "status",
            "idle",
        )

        phase_code = self.state.get(
            "phase",
            "waiting",
        )

        status_label = self.STATUS_LABELS.get(
            status_code,
            status_code,
        )

        phase_label = self.PHASE_LABELS.get(
            phase_code,
            phase_code,
        )

        y += 68

        self.draw_section(
            screen,
            x,
            y,
            "MISIÓN",
            [
                ("Estado", status_label),
                ("Fase", phase_label),
                (
                    "Acción",
                    self.format_value(
                        self.state.get("action")
                    ),
                ),
                (
                    "Ubicación",
                    self.format_value(
                        self.state.get("location")
                    ),
                ),
                (
                    "Progreso",
                    self.format_value(
                        self.state.get(
                            "progress_percent"
                        ),
                        " %",
                    ),
                ),
            ],
        )

        y += 196

        self.draw_section(
            screen,
            x,
            y,
            "NODOS",
            [
                (
                    "Conectados",
                    str(
                        self.state.get(
                            "connected_nodes",
                            0,
                        )
                    ),
                ),
                (
                    "Asignados",
                    str(
                        self.state.get(
                            "assigned_nodes",
                            0,
                        )
                    ),
                ),
                (
                    "Operativos",
                    str(
                        self.state.get(
                            "operational_nodes",
                            0,
                        )
                    ),
                ),
            ],
        )

        y += 142

        self.draw_section(
            screen,
            x,
            y,
            "ENTORNO",
            [
                (
                    "Viento",
                    self.format_value(
                        self.state.get("wind_m_s"),
                        " m/s",
                    ),
                ),
                (
                    "Temperatura",
                    self.format_value(
                        self.state.get(
                            "temperature_c"
                        ),
                        " °C",
                    ),
                ),
                (
                    "Enlace",
                    self.format_value(
                        self.state.get(
                            "link_quality_percent"
                        ),
                        " %",
                    ),
                ),
            ],
        )

        y += 142

        decision = self.state.get(
            "latest_decision",
            {},
        )

        intervention_required = decision.get(
            "intervention_required",
            False,
        )

        intervention_text = (
            "Requerida"
            if intervention_required
            else "No requerida"
        )

        self.draw_section(
            screen,
            x,
            y,
            "ÚLTIMA DECISIÓN MSI",
            [
                (
                    "Resumen",
                    decision.get(
                        "summary",
                        "Esperando planificación",
                    ),
                ),
                (
                    "Intervención",
                    intervention_text,
                ),
            ],
        )

    def draw_section(
        self,
        screen: pygame.Surface,
        x: int,
        y: int,
        title: str,
        rows: list[tuple[str, str]],
    ) -> None:
        """
        Dibuja una sección lateral.
        """

        section_title = self.section_font.render(
            title,
            True,
            theme.SECONDARY_TEXT,
        )

        screen.blit(
            section_title,
            (x, y),
        )

        row_y = y + 30

        for label, value in rows:
            label_surface = self.text_font.render(
                label,
                True,
                theme.MUTED_TEXT,
            )

            value_surface = self.text_font.render(
                value,
                True,
                theme.TEXT,
            )

            screen.blit(
                label_surface,
                (x, row_y),
            )

            screen.blit(
                value_surface,
                (x + 105, row_y),
            )

            row_y += 28

    def render_main_area(
        self,
        screen: pygame.Surface,
        simulation_rect: pygame.Rect,
    ) -> None:
        """
        Muestra el estado actual en la región de simulación.
        """

        status_code = self.state.get(
            "status",
            "idle",
        )

        if status_code == "idle":
            title_text = "Sin misión activa"
            subtitle_text = (
                "MSI está esperando una misión."
            )
        else:
            title_text = self.STATUS_LABELS.get(
                status_code,
                status_code,
            )

            action = self.state.get(
                "action",
                "",
            )

            location = self.state.get(
                "location",
                "",
            )

            if action and location:
                subtitle_text = (
                    f"{action} · {location}"
                )
            else:
                subtitle_text = (
                    "MSI está recopilando parámetros."
                )

        title = self.large_status_font.render(
            title_text,
            True,
            theme.TEXT,
        )

        subtitle = self.text_font.render(
            subtitle_text,
            True,
            theme.SECONDARY_TEXT,
        )

        screen.blit(
            title,
            title.get_rect(
                center=(
                    simulation_rect.centerx,
                    simulation_rect.centery - 20,
                )
            ),
        )

        screen.blit(
            subtitle,
            subtitle.get_rect(
                center=(
                    simulation_rect.centerx,
                    simulation_rect.centery + 25,
                )
            ),
        )