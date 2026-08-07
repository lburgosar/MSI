"""
===============================================================================
MSI Mission Studio - Mission Screen
===============================================================================

Presenta una misión durante la etapa de planificación y supervisión.

Responsabilidades:

- conservar el MissionState creado durante la entrevista;
- mostrar el workspace asociado a la ubicación;
- registrar instrucciones del operador;
- publicar cambios hacia Mission Monitor;
- generar el log y el reporte final;
- conservar visible el estado final hasta que el operador decida volver.

===============================================================================
"""

from __future__ import annotations

import pygame

from core import layout
from core import theme
from core.mission_log import MissionLog
from core.mission_state import MissionState
from scene.vineyard_scene import VineyardScene


class MissionScreen:
    """
    Pantalla de planificación y supervisión conversacional.
    """

    def __init__(
        self,
        mission_text: str,
        mission_state: MissionState,
    ) -> None:
        """
        Inicializa la misión usando el estado creado en HomeScreen.
        """

        self.mission_text = mission_text
        self.mission_state = mission_state

        self.next_screen: str | None = None
        self.mission_finished = False

        (
            self.mission_action,
            self.mission_location,
        ) = self.parse_mission_text(mission_text)

        self.command_text = ""
        self.input_focused = True

        self.command_placeholder = (
            "Consultá, corregí o agregá información..."
        )

        self.feedback_text = (
            "MSI está evaluando capacidades y preparando el plan."
        )

        self.title_font = pygame.font.SysFont(
            "Segoe UI",
            22,
            bold=True,
        )

        self.text_font = pygame.font.SysFont(
            "Segoe UI",
            theme.TEXT_SIZE,
        )

        self.small_font = pygame.font.SysFont(
            "Segoe UI",
            theme.SMALL_TEXT_SIZE,
        )

        self.vineyard_scene = VineyardScene(
            location_name=self.mission_location,
        )

        self.mission_log = MissionLog(
            action=self.mission_action,
            location=self.mission_location,
        )

        self.mission_log.set_status(
            "preparing",
            "Workspace abierto y planificación iniciada.",
        )

        self.mission_state.begin_planning()

    @staticmethod
    def parse_mission_text(
        mission_text: str,
    ) -> tuple[str, str]:
        """
        Separa una descripción como:

            Pulverización · Don Pepe

        en acción y ubicación.
        """

        parts = mission_text.split(
            "·",
            maxsplit=1,
        )

        if len(parts) == 2:
            return (
                parts[0].strip(),
                parts[1].strip(),
            )

        return (
            "Misión",
            mission_text.strip()
            or "Ubicación sin nombre",
        )

    @staticmethod
    def get_pointer_position(
        event: pygame.event.Event,
        screen_size: tuple[int, int],
    ) -> tuple[int, int] | None:
        """
        Convierte eventos de mouse o táctiles en coordenadas de pantalla.
        """

        if event.type == pygame.MOUSEBUTTONDOWN:
            return event.pos

        if event.type == pygame.FINGERDOWN:
            width, height = screen_size

            return (
                int(event.x * width),
                int(event.y * height),
            )

        return None

    def process_event(
        self,
        event: pygame.event.Event,
    ) -> None:
        """
        Procesa teclado, mouse y entrada táctil.
        """

        screen = pygame.display.get_surface()

        if screen is None:
            return

        screen_width, screen_height = screen.get_size()

        prompt_rect = layout.get_bottom_prompt_rect(
            screen_width,
            screen_height,
        )

        send_rect = layout.get_send_button_rect(
            prompt_rect,
        )

        plus_rect = layout.get_plus_button_rect(
            prompt_rect,
        )

        finish_rect = layout.get_finish_button_rect(
            screen_width,
        )

        pointer = self.get_pointer_position(
            event,
            (
                screen_width,
                screen_height,
            ),
        )

        # ---------------------------------------------------------------------
        # MOUSE O PANTALLA TÁCTIL
        # ---------------------------------------------------------------------

        if pointer is not None:
            if finish_rect.collidepoint(pointer):
                self.finish_mission()
                return

            if self.mission_finished:
                return

            if send_rect.collidepoint(pointer):
                self.input_focused = True
                self.submit_command()
                return

            if plus_rect.collidepoint(pointer):
                self.input_focused = True

                self.feedback_text = (
                    "Próximamente: mapas, coordenadas, "
                    "archivos GIS e imágenes."
                )

                self.mission_log.add_event(
                    event_type="attachment_menu_requested",
                    message=(
                        "El operador abrió la entrada adicional."
                    ),
                )

                return

            self.input_focused = (
                prompt_rect.collidepoint(pointer)
            )

            return

        # ---------------------------------------------------------------------
        # TECLADO
        # ---------------------------------------------------------------------

        if event.type != pygame.KEYDOWN:
            return

        if event.key == pygame.K_ESCAPE:
            # Si la misión terminó, Escape vuelve al inicio sin cambiar
            # el resultado publicado en Mission Monitor.
            if self.mission_finished:
                self.next_screen = "home_from_mission"
                return

            # Si todavía estaba activa, Escape la cancela.
            self.mission_state.cancel()

            self.mission_log.finalize(
                result="cancelled",
            )

            self.next_screen = "home_from_mission"
            return

        # Una misión finalizada ya no recibe órdenes nuevas.
        if self.mission_finished:
            return

        if not self.input_focused:
            return

        if event.key == pygame.K_RETURN:
            self.submit_command()
            return

        if event.key == pygame.K_BACKSPACE:
            self.command_text = self.command_text[:-1]
            return

        if (
            event.unicode
            and event.unicode.isprintable()
            and len(self.command_text) < 90
        ):
            self.command_text += event.unicode

    def submit_command(self) -> None:
        """
        Registra una instrucción del operador.

        En la siguiente etapa, estas instrucciones pasarán al
        Mission Interview Engine y al Decision Engine.
        """

        if self.mission_finished:
            return

        command = self.command_text.strip()

        if not command:
            self.feedback_text = (
                "Escribí una indicación antes de enviarla."
            )
            return

        self.mission_log.add_event(
            event_type="user_command",
            message=command,
        )

        self.mission_state.set_decision(
            summary="Instrucción recibida",
            reason=command,
            impact="Pendiente de interpretación por MSI",
            intervention_required=False,
        )

        self.feedback_text = (
            f'Comando registrado: "{command}"'
        )

        self.command_text = ""

    def finish_mission(self) -> None:
        """
        Finaliza la misión, genera el reporte y conserva el resultado
        visible hasta que el operador presione Escape.
        """

        if self.mission_finished:
            return

        self.mission_state.complete()

        self.mission_log.finalize(
            result="completed",
        )

        self.feedback_text = (
            "Misión finalizada. El reporte fue guardado. "
            "Presioná Esc para volver."
        )

        self.command_placeholder = (
            "Misión finalizada · Presioná Esc para volver"
        )

        self.command_text = ""
        self.input_focused = False
        self.mission_finished = True

    def update(
        self,
        delta_time: float,
    ) -> None:
        """
        Actualiza la escena mientras la misión está activa.
        """

        if not self.mission_finished:
            self.vineyard_scene.update(delta_time)

    def render(
        self,
        screen: pygame.Surface,
    ) -> None:
        """
        Dibuja encabezado, workspace, controles y prompt inferior.
        """

        screen.fill(theme.BACKGROUND)

        screen_width, screen_height = screen.get_size()

        header_rect = layout.get_mission_header_rect(
            screen_width,
        )

        workspace_rect = layout.get_workspace_rect(
            screen_width,
            screen_height,
        )

        prompt_rect = layout.get_bottom_prompt_rect(
            screen_width,
            screen_height,
        )

        finish_rect = layout.get_finish_button_rect(
            screen_width,
        )

        # ---------------------------------------------------------------------
        # ENCABEZADO
        # ---------------------------------------------------------------------

        title = self.title_font.render(
            f"{self.mission_action} "
            f"en {self.mission_location}",
            True,
            theme.TEXT,
        )

        screen.blit(
            title,
            (
                header_rect.left,
                header_rect.top + 8,
            ),
        )

        status = self.small_font.render(
            self.feedback_text,
            True,
            theme.SECONDARY_TEXT,
        )

        screen.blit(
            status,
            (
                header_rect.left,
                header_rect.top + 49,
            ),
        )

        # ---------------------------------------------------------------------
        # BOTÓN DE FINALIZACIÓN
        # ---------------------------------------------------------------------

        finish_background = (
            theme.SUCCESS
            if self.mission_finished
            else theme.PANEL
        )

        finish_border = (
            theme.SUCCESS
            if self.mission_finished
            else theme.BORDER
        )

        finish_text_color = (
            theme.PANEL
            if self.mission_finished
            else theme.TEXT
        )

        pygame.draw.rect(
            screen,
            finish_background,
            finish_rect,
            border_radius=theme.BUTTON_RADIUS,
        )

        pygame.draw.rect(
            screen,
            finish_border,
            finish_rect,
            width=1,
            border_radius=theme.BUTTON_RADIUS,
        )

        finish_label = (
            "Misión completada"
            if self.mission_finished
            else "Finalizar misión"
        )

        finish_text = self.small_font.render(
            finish_label,
            True,
            finish_text_color,
        )

        screen.blit(
            finish_text,
            finish_text.get_rect(
                center=finish_rect.center,
            ),
        )

        # ---------------------------------------------------------------------
        # WORKSPACE
        # ---------------------------------------------------------------------

        self.vineyard_scene.render(
            screen,
            workspace_rect,
        )

        # ---------------------------------------------------------------------
        # PROMPT INFERIOR
        # ---------------------------------------------------------------------

        pygame.draw.rect(
            screen,
            theme.PANEL,
            prompt_rect,
            border_radius=22,
        )

        if self.mission_finished:
            border_color = theme.SUCCESS
        elif self.input_focused:
            border_color = theme.PRIMARY
        else:
            border_color = theme.BORDER

        pygame.draw.rect(
            screen,
            border_color,
            prompt_rect,
            width=1,
            border_radius=22,
        )

        plus_rect = layout.get_plus_button_rect(
            prompt_rect,
        )

        send_rect = layout.get_send_button_rect(
            prompt_rect,
        )

        # Cuando la misión terminó, ambos accesos quedan visualmente inactivos.
        if self.mission_finished:
            plus_background = theme.BORDER
            plus_color = theme.MUTED_TEXT
            send_background = theme.BORDER
            send_color = theme.MUTED_TEXT
        else:
            plus_background = theme.PRIMARY_SOFT
            plus_color = theme.PRIMARY
            send_background = theme.PRIMARY
            send_color = theme.PANEL

        pygame.draw.circle(
            screen,
            plus_background,
            plus_rect.center,
            18,
        )

        plus = self.text_font.render(
            "+",
            True,
            plus_color,
        )

        screen.blit(
            plus,
            plus.get_rect(
                center=plus_rect.center,
            ),
        )

        pygame.draw.circle(
            screen,
            send_background,
            send_rect.center,
            18,
        )

        send = self.text_font.render(
            "→",
            True,
            send_color,
        )

        screen.blit(
            send,
            send.get_rect(
                center=send_rect.center,
            ),
        )

        display_text = (
            self.command_text
            or self.command_placeholder
        )

        display_color = (
            theme.TEXT
            if self.command_text
            else theme.MUTED_TEXT
        )

        available_width = (
            send_rect.left
            - plus_rect.right
            - 32
        )

        while (
            self.text_font.size(display_text)[0]
            > available_width
            and len(display_text) > 3
        ):
            display_text = display_text[:-4] + "..."

        command_surface = self.text_font.render(
            display_text,
            True,
            display_color,
        )

        screen.blit(
            command_surface,
            (
                plus_rect.right + 12,
                prompt_rect.centery
                - command_surface.get_height() // 2,
            ),
        )

    def get_next_screen(self) -> str | None:
        """
        Devuelve la transición solicitada.
        """

        return self.next_screen

    def get_mission_text(self) -> str:
        """
        Conserva la descripción de la misión actual.
        """

        return self.mission_text