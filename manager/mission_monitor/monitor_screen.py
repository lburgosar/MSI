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
from presentation.simulation_view import SimulationView
from presentation.operational_map import OperationalMapView


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
        self.simulation_view = SimulationView()
        self.operational_map = OperationalMapView()
        self.selected_resource_id: str | None = None
        self.resource_hitboxes: dict[str, pygame.Rect] = {}

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

        self.small_font = pygame.font.SysFont(
            "Segoe UI",
            12,
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

    def process_event(self, event: pygame.event.Event) -> None:
        if event.type != pygame.MOUSEBUTTONDOWN:
            return
        for resource_id, rect in self.resource_hitboxes.items():
            if rect.collidepoint(event.pos):
                self.selected_resource_id = resource_id
                return

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

        if self.state.get("schema_version") == 2:
            self.render_v2(screen, pygame.Rect(0, 0, width, height))
            return

        if height < 520:
            self.render_compact(screen, pygame.Rect(0, 0, width, height))
            return

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

    def render_v2(self, screen: pygame.Surface, window_rect: pygame.Rect) -> None:
        """Mission Monitor operacional: mapa, recursos, sensores y decisiones."""

        header_height = 82
        pygame.draw.rect(screen, theme.PANEL, (0, 0, window_rect.width, header_height))
        pygame.draw.line(screen, theme.BORDER, (0, header_height), (window_rect.width, header_height))
        scenario = str(self.state.get("scenario", "mission")).replace("_", " ").upper()
        status = str(self.state.get("status", "idle")).upper()
        progress = self.state.get("progress_percent", 0)
        mode = str(self.state.get("mode", "simulation")).upper()
        title = self.title_font.render("MSI Mission Monitor", True, theme.TEXT)
        screen.blit(title, (20, 11))
        subtitle = self.small_text(
            f"{scenario}  ·  {mode}  ·  {status}  ·  PROGRESO {progress}%",
            theme.SECONDARY_TEXT,
        )
        screen.blit(subtitle, (20, 45))

        environment = self.state.get("environment", {})
        environment_text = self.small_text(
            f"VIENTO {float(environment.get('wind_m_s', 0)):.1f} m/s  "
            f"{float(environment.get('wind_direction_deg', 0)):.0f}°  ·  "
            f"TEMP {float(environment.get('temperature_c', 0)):.0f}°C",
            theme.TEXT,
        )
        screen.blit(environment_text, (window_rect.width - environment_text.get_width() - 22, 18))
        latest = self.small_text(str(self.state.get("latest_event", "")), theme.SECONDARY_TEXT)
        screen.blit(latest, (window_rect.width - latest.get_width() - 22, 47))

        content = pygame.Rect(10, header_height + 8, window_rect.width - 20, window_rect.height - header_height - 18)
        panel_width = max(320, int(content.width * .29))
        map_rect = pygame.Rect(content.left, content.top, content.width - panel_width - 10, content.height)
        panel_rect = pygame.Rect(map_rect.right + 10, content.top, panel_width, content.height)

        map_state = dict(self.state)
        drones = list(self.state.get("drones", []))
        drone_ids = {str(item.get("id")) for item in drones}
        for resource in self.state.get("resources", []):
            if resource.get("resource_id") in drone_ids:
                continue
            position = resource.get("map_position")
            if position:
                drones.append({
                    "id": resource.get("resource_id"),
                    "position": position,
                    "orientation_degrees": 0,
                    "battery_percent": resource.get("energy", {}).get("percent", 0),
                    "status": resource.get("availability", "available"),
                    "capabilities": resource.get("capabilities", []),
                    "trajectory": [],
                    "target": None,
                    "objective": None,
                })
        map_state["drones"] = drones
        self.operational_map.set_state(map_state)
        self.operational_map.render(screen, map_rect, interactive=False)
        self.render_v2_panel(screen, panel_rect)

    def small_text(self, text: str, color: tuple[int, int, int]) -> pygame.Surface:
        return self.text_font.render(text, True, color)

    def render_v2_panel(self, screen: pygame.Surface, panel: pygame.Rect) -> None:
        pygame.draw.rect(screen, theme.PANEL, panel, border_radius=18)
        pygame.draw.rect(screen, theme.BORDER, panel, width=1, border_radius=18)
        resources = list(self.state.get("resources", []))
        if self.selected_resource_id is None and resources:
            self.selected_resource_id = str(resources[0].get("resource_id"))
        selected = next(
            (item for item in resources if item.get("resource_id") == self.selected_resource_id),
            resources[0] if resources else None,
        )
        self.resource_hitboxes.clear()
        x, y = panel.left + 13, panel.top + 12
        heading = self.section_font.render("RECURSOS", True, theme.SECONDARY_TEXT)
        screen.blit(heading, (x, y))
        y += 22
        chip_width = max(52, (panel.width - 34) // max(1, min(4, len(resources))))
        for resource in resources[:4]:
            resource_id = str(resource.get("resource_id"))
            rect = pygame.Rect(x, y, chip_width, 34)
            self.resource_hitboxes[resource_id] = rect
            active = resource_id == self.selected_resource_id
            assigned = bool(resource.get("assigned"))
            fill = theme.PRIMARY_SOFT if active else ((237, 247, 241) if assigned else (248, 248, 249))
            pygame.draw.rect(screen, fill, rect, border_radius=10)
            pygame.draw.rect(screen, theme.PRIMARY if active else theme.BORDER, rect, 1, border_radius=10)
            energy = float(resource.get("energy", {}).get("percent", 0))
            label = self.small_font.render(f"{resource_id}  {energy:.0f}%", True, theme.TEXT)
            screen.blit(label, label.get_rect(center=rect.center))
            x += chip_width + 3
        x = panel.left + 13
        y += 43

        if selected:
            name = self.section_font.render(str(selected.get("display_name", "Resource")), True, theme.TEXT)
            screen.blit(name, (x, y))
            y += 21
            consumable = selected.get("consumable")
            product = (
                f"  ·  PROD {float(consumable.get('remaining_l', 0)):.1f} L"
                if consumable else ""
            )
            comm = selected.get("communication", {})
            detail = self.small_font.render(
                f"LINK {float(comm.get('link_quality_percent', 0)):.0f}%{product}",
                True, theme.SECONDARY_TEXT,
            )
            screen.blit(detail, (x, y))
            y += 22
            assignment = selected.get("assignment") or {}
            assignment_text = (
                f"ASIGNADO · {assignment.get('task_id')} · SECTOR {assignment.get('sector')}"
                if selected.get("assigned") else "DISPONIBLE · NO ASIGNADO"
            )
            role = self.fit_text(f"{assignment_text} · {selected.get('mission_role', '')}", panel.width - 26)
            screen.blit(self.small_font.render(role, True, theme.PRIMARY if selected.get("assigned") else theme.SECONDARY_TEXT), (x, y))
            y += 19
            sensors = selected.get("sensors", [])
            feed_rect = pygame.Rect(x, y, panel.width - 26, min(60, max(42, panel.height // 5)))
            pygame.draw.rect(screen, (35, 44, 47), feed_rect, border_radius=10)
            sensor_type = sensors[0].get("sensor_type", "NO SENSOR") if sensors else "NO SENSOR"
            sensor_label = self.small_font.render(
                f"SIMULATED SENSOR DATA · {str(sensor_type).upper()}", True, (210, 225, 221)
            )
            screen.blit(sensor_label, (feed_rect.left + 10, feed_rect.top + 8))
            for offset in range(24, feed_rect.height - 5, 12):
                pygame.draw.line(
                    screen, (65, 91, 86),
                    (feed_rect.left + 10, feed_rect.top + offset),
                    (feed_rect.right - 10, feed_rect.top + offset), 1,
                )
            y = feed_rect.bottom + 10

        preflight = self.state.get("preflight_explanation", {})
        if preflight and self.state.get("status") in {"ready", "blocked"}:
            color = theme.SUCCESS if preflight.get("status") == "ready" else theme.WARNING
            title = self.section_font.render(
                f"PREFLIGHT {str(preflight.get('status', '')).upper()} · {preflight.get('result', '')}",
                True, color,
            )
            screen.blit(title, (x, y))
            y += 21
            for check in list(preflight.get("checks", []))[:4]:
                marker = "OK" if check.get("ok") else "ATENCIÓN"
                line = self.fit_text(
                    f"{marker} {check.get('label')}: {check.get('actual')} / {check.get('required')}",
                    panel.width - 26,
                )
                screen.blit(self.small_font.render(line, True, theme.TEXT), (x, y))
                y += 17
            y += 5

        narrative = self.state.get("decision_narrative")
        if narrative:
            decision_rect = pygame.Rect(x, y, panel.width - 26, 112)
            pygame.draw.rect(screen, (241, 247, 255), decision_rect, border_radius=10)
            pygame.draw.rect(screen, (181, 211, 244), decision_rect, width=1, border_radius=10)
            rows = (
                ("CONDITION", narrative.get("condition")),
                ("EVALUATION", narrative.get("evaluation")),
                ("DECISION", str(narrative.get("decision", "")).replace("_", " ").upper()),
                ("IMPACT", narrative.get("impact")),
                ("ACTION", narrative.get("action")),
            )
            row_y = decision_rect.top + 7
            for label, value in rows:
                prefix = self.small_font.render(label, True, theme.PRIMARY)
                screen.blit(prefix, (decision_rect.left + 9, row_y))
                clipped = self.fit_text(str(value), decision_rect.width - prefix.get_width() - 24)
                screen.blit(self.small_font.render(clipped, True, theme.TEXT), (decision_rect.left + 14 + prefix.get_width(), row_y))
                row_y += 20
            y = decision_rect.bottom + 8

        timeline_title = self.section_font.render("DECISIONES / EVENTOS", True, theme.SECONDARY_TEXT)
        screen.blit(timeline_title, (x, y))
        y += 21
        available_rows = max(0, (panel.bottom - y - 8) // 34)
        events = list(self.state.get("events", []))[-available_rows:] if available_rows else []
        for event in reversed(events):
            event_type = str(event.get("event_type", "event")).upper()
            summary = str(event.get("summary", ""))
            type_surface = self.small_font.render(event_type, True, theme.PRIMARY)
            screen.blit(type_surface, (x, y))
            clipped = self.fit_text(summary, panel.width - 30)
            summary_surface = self.small_font.render(clipped, True, theme.TEXT)
            screen.blit(summary_surface, (x, y + 14))
            y += 34

    def fit_text(self, text: str, max_width: int) -> str:
        clipped = text
        while self.small_font.size(clipped)[0] > max_width and len(clipped) > 3:
            clipped = clipped[:-4] + "..."
        return clipped

    def render_compact(
        self,
        screen: pygame.Surface,
        window_rect: pygame.Rect,
    ) -> None:
        """Layout horizontal para Monitor cuando comparte una pantalla baja."""

        header_height = 76
        pygame.draw.rect(screen, theme.PANEL, (0, 0, window_rect.width, header_height))
        pygame.draw.line(
            screen,
            theme.BORDER,
            (0, header_height),
            (window_rect.width, header_height),
        )

        status_code = self.state.get("status", "idle")
        status_label = self.STATUS_LABELS.get(status_code, status_code)
        progress = self.state.get("progress_percent", 0)
        active = self.state.get("active_drones", 0)
        drones = self.state.get("drones", [])
        average_battery = (
            sum(float(drone.get("battery_percent", 0.0)) for drone in drones) / len(drones)
            if drones
            else 0.0
        )

        title = self.title_font.render("MSI Mission Monitor", True, theme.TEXT)
        screen.blit(title, (22, 12))
        summary = self.text_font.render(
            f"{status_label}   ·   Progreso {progress}%   ·   En vuelo {active}   ·   Batería {average_battery:.0f}%",
            True,
            theme.SECONDARY_TEXT,
        )
        screen.blit(summary, (22, 45))

        event_text = self.state.get("latest_event", "Esperando misión")
        event = self.text_font.render(str(event_text), True, theme.TEXT)
        screen.blit(event, (window_rect.right - event.get_width() - 24, 28))

        content_rect = pygame.Rect(0, header_height, window_rect.width, window_rect.height - header_height)
        if drones:
            self.render_synoptic(screen, content_rect, drones, compact=True)
        else:
            waiting = self.text_font.render("Esperando una nueva misión desde Studio", True, theme.SECONDARY_TEXT)
            screen.blit(waiting, waiting.get_rect(center=content_rect.center))

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

        drones = self.state.get("drones", [])
        average_battery = (
            sum(float(drone.get("battery_percent", 0.0)) for drone in drones) / len(drones)
            if drones
            else 0.0
        )
        average_speed = (
            sum(float(drone.get("speed", 0.0)) for drone in drones) / len(drones)
            if drones
            else 0.0
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
                (
                    "En vuelo",
                    str(self.state.get("active_drones", 0)),
                ),
                ("Batería media", f"{average_battery:.0f} %" if drones else "—"),
                ("Velocidad media", f"{average_speed:.2f} u/s" if drones else "—"),
            ],
        )

        y += 226

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
                (
                    "Evento",
                    self.state.get("latest_event", "—"),
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

        drones = self.state.get("drones", [])

        if drones:
            self.render_synoptic(screen, simulation_rect, drones)
            return

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

    def render_synoptic(
        self,
        screen: pygame.Surface,
        simulation_rect: pygame.Rect,
        drones: list[dict[str, Any]],
        compact: bool = False,
    ) -> None:
        """Dibuja una vista operacional resumida, no una copia de Studio."""

        margin = 10 if compact else 42
        viewport = simulation_rect.inflate(-margin * 2, -margin * 2)
        pygame.draw.rect(screen, theme.PANEL, viewport, border_radius=22)
        pygame.draw.rect(screen, theme.BORDER, viewport, width=1, border_radius=22)

        title_height = 0 if compact else 40
        if not compact:
            title = self.section_font.render("VISTA SINÓPTICA DE MISIÓN", True, theme.SECONDARY_TEXT)
            screen.blit(title, (viewport.left + 22, viewport.top + 18))

        map_rect = pygame.Rect(
            viewport.left + 34,
            viewport.top + 12 + title_height,
            viewport.width - 68,
            viewport.height - 24 - title_height,
        )

        row_spacing = max(22, map_rect.height // 8)
        for row_y in range(map_rect.top + row_spacing, map_rect.bottom, row_spacing):
            pygame.draw.line(
                screen,
                (88, 116, 76),
                (map_rect.left + 18, row_y),
                (map_rect.right - 18, row_y),
                width=3,
            )

        self.simulation_view.render(screen, map_rect, drones, interactive=False)
