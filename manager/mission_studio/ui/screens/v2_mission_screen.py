"""Mission Studio V2: configuración, preview, autorización y control operacional."""

from __future__ import annotations

from copy import deepcopy
from dataclasses import replace
from pathlib import Path

import pygame

from application.demo_catalog import DEMO_BOUNDS, demo_configuration, demo_resources
from core import layout, theme
from core.mission_log import MissionLog
from core.mission_state import MissionState
from domain.geography import Altitude
from domain.mission import MissionIntent
from domain.resources import Availability
from planning.preflight import PreflightStatus
from presentation.operational_map import OperationalMapView
from providers.resources import SimulatedResourceProvider
from runtime_v2.mission_runtime import MissionRuntimeV2
from runtime_v2.scenario_engine import ScenarioEngine
from traceability.recorder import OperationalTraceRecorder
from transport.channels import CallbackStatePublisher


class MissionScreen:
    """Interfaz de aplicación; las decisiones permanecen en MissionRuntimeV2."""

    def __init__(self, mission_text: str, mission_state: MissionState) -> None:
        self.mission_text = mission_text
        self.mission_state = mission_state
        self.next_screen: str | None = None
        self.mission_finished = False
        self.command_text = ""
        self.input_focused = True
        self.feedback_text = "MSI generó un plan y ejecutó preflight. Revisá antes de autorizar."
        self.selected_resource_id = "D1"
        self.dragging_resource_id: str | None = None
        self.map_rect: pygame.Rect | None = None
        self.resource_rects: dict[str, pygame.Rect] = {}
        self.scenario_rects: dict[str, pygame.Rect] = {}

        action, location = self.parse_mission_text(mission_text)
        self.action = action
        self.location = location
        self.intent = self.intent_from_action(action)
        self.provider = SimulatedResourceProvider(demo_resources())
        self.configuration = replace(
            demo_configuration(self.intent),
            name=f"{action} · {location}",
        )
        self.runtime = MissionRuntimeV2(
            self.configuration,
            self.provider,
            state_publisher=CallbackStatePublisher(
                lambda snapshot: self.mission_state.update(**snapshot)
            ),
            trace_recorder=OperationalTraceRecorder(
                self.configuration.mission_id,
                Path(__file__).resolve().parents[2] / "data" / "v2_traces",
            ),
        )
        self.scenario = ScenarioEngine(self.runtime)
        self.map_view = OperationalMapView()
        self.mission_log = MissionLog(action, location)
        self.mission_log.set_status("preview", "Plan V2 generado y preflight ejecutado.")

        self.title_font = pygame.font.SysFont("Segoe UI", 22, bold=True)
        self.section_font = pygame.font.SysFont("Segoe UI", 13, bold=True)
        self.text_font = pygame.font.SysFont("Segoe UI", 14)
        self.small_font = pygame.font.SysFont("Segoe UI", 12)

    @staticmethod
    def parse_mission_text(mission_text: str) -> tuple[str, str]:
        parts = mission_text.split("·", maxsplit=1)
        return (
            parts[0].strip() if parts else "Misión",
            parts[1].strip() if len(parts) == 2 else "Las Marías",
        )

    @staticmethod
    def intent_from_action(action: str) -> MissionIntent:
        normalized = action.lower()
        if "patr" in normalized or "inspec" in normalized or "recorr" in normalized:
            return MissionIntent.AUTONOMOUS_PATROL
        if "emerg" in normalized or "respuesta" in normalized:
            return MissionIntent.EMERGENCY_RESPONSE
        return MissionIntent.PRECISION_SPRAYING

    def primary_label(self) -> str:
        if self.runtime.status == "ready":
            return "Autorizar plan"
        if self.runtime.status == "authorized":
            return "Ejecutar misión"
        if self.runtime.status == "paused":
            return "Reanudar"
        if self.runtime.status == "completed":
            return "Misión completada"
        if self.runtime.status == "blocked":
            return "Preflight bloqueado"
        return "En ejecución"

    def primary_action(self) -> None:
        if self.runtime.status == "ready":
            if self.runtime.authorize():
                self.feedback_text = "Plan autorizado. La ejecución requiere una segunda acción explícita."
                self.mission_log.add_event("authorization", "Operador autorizó el plan V2.")
        elif self.runtime.status == "authorized":
            if self.runtime.start():
                self.feedback_text = "Misión en ejecución bajo gobierno de MSI."
                self.mission_log.add_event("execution_started", "Runtime V2 inició ejecución.")
        elif self.runtime.status == "paused":
            if self.runtime.resume_if_valid():
                self.feedback_text = "Condiciones válidas. MSI reanudó la misión."
            else:
                wind = self.runtime.environment["wind_m_s"]
                limit = float(self.configuration.parameters.get("max_wind_m_s", 999.0))
                self.feedback_text = (
                    "REANUDACIÓN RECHAZADA · "
                    f"Viento actual {wind:.1f} m/s · límite {limit:.1f} m/s. "
                    "Esperar condiciones válidas o modificar la misión."
                )
        elif self.runtime.status == "blocked":
            self.feedback_text = self.preflight_feedback()

    def preflight_feedback(self) -> str:
        if self.runtime.preflight is None or not self.runtime.preflight.findings:
            return "PREFLIGHT BLOCKED · Sin detalle disponible."
        finding = self.runtime.preflight.findings[0]
        return f"PREFLIGHT {self.runtime.preflight.status.value.upper()} · {finding.summary}: {finding.detail}"

    def process_event(self, event: pygame.event.Event) -> None:
        screen = pygame.display.get_surface()
        if screen is None:
            return
        width, height = screen.get_size()
        prompt_rect = layout.get_bottom_prompt_rect(width, height)
        primary_rect = layout.get_finish_button_rect(width, height)

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                if self.runtime.status in {"completed", "blocked", "ready"}:
                    self.next_screen = "home_from_mission"
                return
            if not self.input_focused:
                return
            if event.key == pygame.K_RETURN:
                self.submit_command()
            elif event.key == pygame.K_BACKSPACE:
                self.command_text = self.command_text[:-1]
            elif event.unicode and event.unicode.isprintable() and len(self.command_text) < 120:
                self.command_text += event.unicode
            return

        if event.type == pygame.MOUSEBUTTONDOWN:
            point = event.pos
            if primary_rect.collidepoint(point):
                self.primary_action()
                return
            send_rect = layout.get_send_button_rect(prompt_rect)
            if send_rect.collidepoint(point):
                self.submit_command()
                return
            for action, rect in self.scenario_rects.items():
                if rect.collidepoint(point):
                    self.apply_scenario_action(action)
                    return
            for resource_id, rect in self.resource_rects.items():
                if rect.collidepoint(point):
                    self.selected_resource_id = resource_id
                    self.map_view.simulation_view.selected_drone_id = resource_id
                    return
            if self.map_rect and self.map_rect.collidepoint(point):
                selected = self.map_view.select_at(point)
                if selected:
                    self.selected_resource_id = selected
                    self.dragging_resource_id = selected
                return
            self.input_focused = prompt_rect.collidepoint(point)

        elif event.type == pygame.MOUSEMOTION and self.dragging_resource_id and self.map_rect:
            viewport = self.map_view.viewport(self.map_rect)
            x = min(1.0, max(0.0, (event.pos[0] - viewport.left) / max(1, viewport.width)))
            y = min(1.0, max(0.0, (event.pos[1] - viewport.top) / max(1, viewport.height)))
            resource = self.provider.get_resource(self.dragging_resource_id)
            resource.position = DEMO_BOUNDS.from_normalized(x, y, resource.position.altitude)
            self.provider.update_resource(resource)
            if self.runtime.simulation and self.dragging_resource_id in self.runtime.simulation.drones:
                self.runtime.simulation.drones[self.dragging_resource_id].position = (x, y)

        elif event.type == pygame.MOUSEBUTTONUP and self.dragging_resource_id:
            self.dragging_resource_id = None
            if self.runtime.status in {"ready", "authorized", "blocked"}:
                self.runtime.plan_mission()
                self.feedback_text = "Posición actualizada; MSI recalculó plan y preflight."

    def submit_command(self) -> None:
        command = self.command_text.strip()
        if not command:
            self.feedback_text = "Escribí una orden o un valor operacional."
            return
        tokens = command.replace(",", ".").split()
        preserve_feedback = False
        try:
            keyword = tokens[0].lower()
            if keyword in {"autorizar", "ejecutar", "reanudar"}:
                self.primary_action()
            elif keyword == "wind" or keyword == "viento":
                direction = float(tokens[2]) if len(tokens) > 2 else None
                self.scenario.set_wind(float(tokens[1]), direction)
                if self.runtime.paused and self.runtime.environment["wind_m_s"] <= float(
                    self.configuration.parameters.get("max_wind_m_s", 999.0)
                ):
                    self.feedback_text = "CONDICIONES RESTABLECIDAS · Reanudar está disponible."
                    preserve_feedback = True
            elif keyword in {"product", "producto"}:
                self.scenario.set_product(tokens[1].upper(), float(tokens[2]))
            elif keyword in {"battery", "bateria"}:
                self.scenario.set_battery(tokens[1].upper(), float(tokens[2]))
            elif keyword in {"withdraw", "retirar"}:
                self.scenario.withdraw(tokens[1].upper())
            elif keyword == "link" or keyword == "enlace":
                self.scenario.set_link_quality(tokens[1].upper(), float(tokens[2]))
            elif keyword == "sensor":
                self.scenario.fail_sensor(tokens[1].upper(), tokens[2])
            elif keyword in {"position", "posicion"}:
                self.set_numeric_position(tokens[1].upper(), float(tokens[2]), float(tokens[3]), float(tokens[4]))
            elif keyword == "add" or keyword == "agregar":
                self.add_resource()
            else:
                raise ValueError("Orden no reconocida")
            if not preserve_feedback:
                self.feedback_text = (
                    self.preflight_feedback()
                    if self.runtime.status == "blocked"
                    else f'Orden aplicada: "{command}"'
                )
            self.mission_log.add_event("operator_command", command)
        except (ValueError, IndexError) as error:
            self.feedback_text = f"No pude aplicar la orden: {error}"
        self.command_text = ""

    def set_numeric_position(
        self,
        resource_id: str,
        latitude: float,
        longitude: float,
        altitude_m: float,
    ) -> None:
        resource = self.provider.get_resource(resource_id)
        altitude = Altitude(
            altitude_m,
            resource.position.altitude.reference,
            resource.position.altitude.uncertainty_m,
        )
        resource.position = type(resource.position)(latitude, longitude, altitude)
        self.provider.update_resource(resource)
        if self.runtime.status in {"ready", "authorized", "blocked"}:
            self.runtime.plan_mission()

    def add_resource(self) -> None:
        existing = self.provider.list_catalog()
        template = deepcopy(existing[0])
        numbers = [int(item.resource_id[1:]) for item in existing if item.resource_id.startswith("D")]
        template.resource_id = f"D{max(numbers, default=0) + 1}"
        template.display_name = f"Aquila Configurable {template.resource_id}"
        template.energy.percent = 84.0
        template.selected = True
        template.availability = Availability.AVAILABLE
        x, y = DEMO_BOUNDS.to_normalized(template.position)
        template.position = DEMO_BOUNDS.from_normalized(min(.95, x + .04), min(.95, y + .04), template.position.altitude)
        self.provider.add_resource(template)
        self.selected_resource_id = template.resource_id
        self.runtime.plan_mission()

    def apply_scenario_action(self, action: str) -> None:
        resource_id = self.selected_resource_id
        try:
            if action == "wind":
                self.scenario.set_wind(7.2, 265)
            elif action == "product":
                self.scenario.set_product(resource_id, 1.0)
            elif action == "battery":
                self.scenario.set_battery(resource_id, 18.0)
            elif action in {"withdraw", "remove"}:
                self.scenario.withdraw(resource_id)
            elif action == "disable":
                resource = self.provider.get_resource(resource_id)
                resource.availability = Availability.DISABLED
                resource.selected = False
                self.provider.update_resource(resource)
                self.runtime.plan_mission()
            elif action == "enable":
                resource = self.provider.get_resource(resource_id)
                resource.availability = Availability.AVAILABLE
                resource.selected = True
                self.provider.update_resource(resource)
                self.runtime.plan_mission()
            elif action == "anomaly":
                self.scenario.inject_thermal_anomaly(-34.601, -58.398)
            elif action == "add":
                self.add_resource()
            self.feedback_text = (
                self.preflight_feedback()
                if self.runtime.status == "blocked"
                else f"Scenario Control aplicó: {action}"
            )
        except ValueError as error:
            self.feedback_text = f"No se pudo aplicar {action}: {error}"

    def update(self, delta_time: float) -> None:
        self.runtime.update(delta_time)
        if self.runtime.status == "completed" and not self.mission_finished:
            self.mission_finished = True
            self.feedback_text = "Misión completada y trazabilidad disponible en Monitor."
            self.mission_log.finalize("completed")

    def augmented_snapshot(self) -> dict[str, object]:
        state = self.runtime.snapshot()
        drone_ids = {str(item["id"]) for item in state["drones"]}  # type: ignore[index]
        markers = list(state["drones"])  # type: ignore[arg-type]
        for resource in self.provider.list_resources():
            if resource.resource_id in drone_ids:
                continue
            x, y = DEMO_BOUNDS.to_normalized(resource.position)
            markers.append({
                "id": resource.resource_id,
                "position": {"x": x, "y": y},
                "orientation_degrees": 0.0,
                "speed": 0.0,
                "battery_percent": resource.energy.percent,
                "status": resource.availability.value,
                "capabilities": sorted(resource.capabilities),
                "assigned_task": None,
                "target": None,
                "objective": None,
                "trajectory": [],
            })
        state["drones"] = markers
        return state

    def render(self, screen: pygame.Surface) -> None:
        screen.fill(theme.BACKGROUND)
        width, height = screen.get_size()
        compact = height < 360
        margin = layout.get_horizontal_margin(width)
        primary_rect = layout.get_finish_button_rect(width, height)

        title = self.title_font.render(self.configuration.name, True, theme.TEXT)
        screen.blit(title, (margin, 10 if compact else 22))
        preflight = self.runtime.preflight.status.value.upper() if self.runtime.preflight else "—"
        summary = (
            f"{self.runtime.status.upper()}  ·  PREFLIGHT {preflight}  ·  "
            f"PLAN V{self.runtime.plan.version if self.runtime.plan else 0}  ·  "
            f"{len(self.provider.list_resources())} RECURSOS"
        )
        summary_surface = self.small_font.render(summary, True, theme.SECONDARY_TEXT)
        screen.blit(summary_surface, (margin, 48 if compact else 57))
        self.draw_primary_button(screen, primary_rect)

        snapshot = self.augmented_snapshot()
        self.map_view.set_state(snapshot)
        self.resource_rects.clear()
        self.scenario_rects.clear()
        if compact:
            self.render_compact_controls(screen, width)
            self.map_rect = None
        else:
            prompt_rect = layout.get_bottom_prompt_rect(width, height)
            available_height = prompt_rect.top - 96
            map_width = int((width - margin * 2) * .70)
            self.map_rect = pygame.Rect(margin, 88, map_width, available_height)
            self.map_view.render(screen, self.map_rect, interactive=True)
            panel = pygame.Rect(
                self.map_rect.right + 14,
                self.map_rect.top,
                width - margin - self.map_rect.right - 14,
                self.map_rect.height,
            )
            self.render_side_panel(screen, panel)

        self.render_prompt(screen, width, height)

    def draw_primary_button(self, screen: pygame.Surface, rect: pygame.Rect) -> None:
        enabled = self.runtime.status in {"ready", "authorized", "paused"}
        color = theme.PRIMARY if enabled else (theme.SUCCESS if self.runtime.status == "completed" else theme.PANEL)
        pygame.draw.rect(screen, color, rect, border_radius=20)
        pygame.draw.rect(screen, theme.PRIMARY if enabled else theme.BORDER, rect, width=1, border_radius=20)
        label = self.small_font.render(self.primary_label(), True, theme.PANEL if enabled else theme.TEXT)
        screen.blit(label, label.get_rect(center=rect.center))

    def render_compact_controls(self, screen: pygame.Surface, width: int) -> None:
        actions = self.scenario_actions()
        button_width = min(160, (width - 80) // max(1, len(actions)))
        total_width = button_width * len(actions) + 8 * (len(actions) - 1)
        x = (width - total_width) // 2
        for action, label in actions:
            rect = pygame.Rect(x, 77, button_width, 40)
            self.scenario_rects[action] = rect
            pygame.draw.rect(screen, theme.PANEL, rect, border_radius=14)
            pygame.draw.rect(screen, theme.BORDER, rect, width=1, border_radius=14)
            surface = self.small_font.render(label, True, theme.TEXT)
            screen.blit(surface, surface.get_rect(center=rect.center))
            x += button_width + 8

    def render_side_panel(self, screen: pygame.Surface, panel: pygame.Rect) -> None:
        pygame.draw.rect(screen, theme.PANEL, panel, border_radius=18)
        pygame.draw.rect(screen, theme.BORDER, panel, width=1, border_radius=18)
        x, y = panel.left + 14, panel.top + 14
        heading = self.section_font.render("FLOTA / RECURSOS", True, theme.SECONDARY_TEXT)
        screen.blit(heading, (x, y))
        y += 26
        for resource in self.provider.list_resources()[:6]:
            rect = pygame.Rect(x, y, panel.width - 28, 47)
            self.resource_rects[resource.resource_id] = rect
            selected = resource.resource_id == self.selected_resource_id
            pygame.draw.rect(screen, theme.PRIMARY_SOFT if selected else (249, 249, 250), rect, border_radius=11)
            if selected:
                pygame.draw.rect(screen, theme.PRIMARY, rect, width=1, border_radius=11)
            name = self.small_font.render(f"{resource.resource_id}  {resource.display_name}", True, theme.TEXT)
            details = self.small_font.render(
                f"BAT {resource.energy.percent:.0f}%  ·  LINK {resource.communication.link_quality_percent:.0f}%  ·  {resource.availability.value.upper()}",
                True, theme.SECONDARY_TEXT,
            )
            screen.blit(name, (rect.left + 10, rect.top + 7))
            screen.blit(details, (rect.left + 10, rect.top + 26))
            y += 53
        y += 4
        label = self.section_font.render("SCENARIO CONTROL · SIMULATION", True, theme.SECONDARY_TEXT)
        screen.blit(label, (x, y))
        y += 24
        for action, text in self.scenario_actions():
            rect = pygame.Rect(x, y, panel.width - 28, 34)
            self.scenario_rects[action] = rect
            pygame.draw.rect(screen, (248, 248, 249), rect, border_radius=10)
            pygame.draw.rect(screen, theme.BORDER, rect, width=1, border_radius=10)
            surface = self.small_font.render(text, True, theme.TEXT)
            screen.blit(surface, (rect.left + 10, rect.centery - surface.get_height() // 2))
            y += 39

    def scenario_actions(self) -> list[tuple[str, str]]:
        if self.runtime.status not in {"running", "paused"}:
            return [
                ("add", "+ Agregar recurso"),
                ("disable", "Desactivar seleccionado"),
                ("enable", "Activar seleccionado"),
                ("remove", "Retirar seleccionado"),
            ]
        if self.intent is MissionIntent.AUTONOMOUS_PATROL:
            return [("anomaly", "Anomalía térmica"), ("battery", "Batería 18%"), ("withdraw", "Retirar seleccionado")]
        if self.intent is MissionIntent.EMERGENCY_RESPONSE:
            return [("anomaly", "Nuevo foco prioritario"), ("battery", "Batería 18%"), ("withdraw", "Retirar seleccionado")]
        return [
            ("wind", "Viento 7.2 m/s"),
            ("product", "Producto 1 L"),
            ("battery", "Batería 18%"),
            ("withdraw", "Retirar seleccionado"),
        ]

    def render_prompt(self, screen: pygame.Surface, width: int, height: int) -> None:
        rect = layout.get_bottom_prompt_rect(width, height)
        pygame.draw.rect(screen, theme.PANEL, rect, border_radius=22)
        pygame.draw.rect(screen, theme.PRIMARY if self.input_focused else theme.BORDER, rect, width=1, border_radius=22)
        send_rect = layout.get_send_button_rect(rect)
        pygame.draw.circle(screen, theme.PRIMARY, send_rect.center, 18)
        send = self.text_font.render("→", True, theme.PANEL)
        screen.blit(send, send.get_rect(center=send_rect.center))
        placeholder = self.feedback_text or "Comando: viento 7.2 · producto D1 1 · posición D1 LAT LON ALT"
        text = self.command_text or placeholder
        color = theme.TEXT if self.command_text else theme.MUTED_TEXT
        available = send_rect.left - rect.left - 28
        while self.text_font.size(text)[0] > available and len(text) > 3:
            text = text[:-4] + "..."
        surface = self.text_font.render(text, True, color)
        screen.blit(surface, (rect.left + 18, rect.centery - surface.get_height() // 2))

    def get_next_screen(self) -> str | None:
        return self.next_screen

    def get_mission_text(self) -> str:
        return self.mission_text
