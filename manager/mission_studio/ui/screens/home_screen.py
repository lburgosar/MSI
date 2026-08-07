"""
===============================================================================
MSI Mission Studio - Home Screen
===============================================================================

Implementa la conversación inicial de misión.

Flujo:

1. MSI espera una intención.
2. Reconoce saludos y acciones compatibles.
3. Pregunta dónde se realizará la misión.
4. Publica cada cambio en MissionState.
5. Solo después abre la pantalla de planificación.

===============================================================================
"""

from __future__ import annotations

import unicodedata

import pygame

from core import layout
from core import theme
from core.mission_state import MissionState


class HomeScreen:
    """
    Pantalla conversacional de precarga.
    """

    ACTION_KEYWORDS = {
        "pulverizar": {
            "pulverizar",
            "pulverizacion",
            "fumigar",
            "fumigacion",
            "aplicar",
            "aplicacion",
        },
        "patrullar": {
            "patrullar",
            "patrullaje",
            "inspeccionar",
            "inspeccion",
            "recorrer",
            "recorrido",
        },
    }

    ACTION_LABELS = {
        "pulverizar": "Pulverización",
        "patrullar": "Patrullaje",
    }

    GREETINGS = {
        "hola",
        "buen dia",
        "buenas",
        "buenas tardes",
        "buenas noches",
        "como estas",
        "que tal",
    }

    def __init__(self) -> None:
        self.next_screen: str | None = None

        self.conversation_stage = "action"
        self.input_focused = True
        self.input_text = ""

        self.mission_action: str | None = None
        self.mission_location: str | None = None

        # Estado compartido con Mission Monitor.
        self.mission_state = MissionState()
        self.mission_state.start_interview()

        self.question_text = "¿Qué querés lograr?"

        self.feedback_text = (
            "Podés comenzar con: pulverizar, patrullar, "
            "inspeccionar o recorrer."
        )

        self.cursor_visible = True
        self.cursor_timer = 0.0

        self.title_font = pygame.font.SysFont(
            "Segoe UI",
            theme.TITLE_SIZE,
            bold=True,
        )

        self.prompt_font = pygame.font.SysFont(
            "Segoe UI",
            theme.PROMPT_SIZE,
        )

        self.feedback_font = pygame.font.SysFont(
            "Segoe UI",
            theme.TEXT_SIZE,
        )

    @staticmethod
    def normalize_text(
        text: str,
    ) -> str:
        normalized = unicodedata.normalize(
            "NFD",
            text.lower().strip(),
        )

        return "".join(
            character
            for character in normalized
            if unicodedata.category(character) != "Mn"
        )

    def detect_action(
        self,
        text: str,
    ) -> str | None:
        normalized_text = self.normalize_text(text)
        words = set(normalized_text.split())

        for action, keywords in self.ACTION_KEYWORDS.items():
            if words.intersection(keywords):
                return action

        return None

    @staticmethod
    def get_pointer_position(
        event: pygame.event.Event,
        screen_size: tuple[int, int],
    ) -> tuple[int, int] | None:
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
        screen = pygame.display.get_surface()

        if screen is None:
            return

        screen_size = screen.get_size()

        prompt_rect = layout.get_home_prompt_rect(
            *screen_size
        )

        send_rect = layout.get_send_button_rect(
            prompt_rect
        )

        plus_rect = layout.get_plus_button_rect(
            prompt_rect
        )

        pointer = self.get_pointer_position(
            event,
            screen_size,
        )

        if pointer is not None:
            if send_rect.collidepoint(pointer):
                self.input_focused = True
                self.submit_input()
                return

            if plus_rect.collidepoint(pointer):
                self.input_focused = True
                self.feedback_text = (
                    "Próximamente podrás adjuntar mapas, "
                    "coordenadas, planos e imágenes."
                )
                return

            self.input_focused = (
                prompt_rect.collidepoint(pointer)
            )

            return

        if event.type != pygame.KEYDOWN:
            return

        if not self.input_focused:
            return

        if event.key == pygame.K_RETURN:
            self.submit_input()
            return

        if event.key == pygame.K_BACKSPACE:
            self.input_text = self.input_text[:-1]
            return

        if event.key == pygame.K_ESCAPE:
            self.reset_conversation()
            return

        if (
            event.unicode
            and event.unicode.isprintable()
            and len(self.input_text) < 90
        ):
            self.input_text += event.unicode

    def submit_input(self) -> None:
        user_text = self.input_text.strip()

        if not user_text:
            self.feedback_text = (
                "Necesito que escribas una indicación."
            )
            return

        if self.conversation_stage == "action":
            self.process_action_input(user_text)
            return

        if self.conversation_stage == "location":
            self.process_location_input(user_text)

    def process_action_input(
        self,
        user_text: str,
    ) -> None:
        normalized_text = self.normalize_text(
            user_text
        )

        if normalized_text in self.GREETINGS:
            self.question_text = (
                "Hola, ¿qué puedo hacer por vos?"
            )

            self.feedback_text = (
                "Puedo ayudarte a preparar una misión "
                "de pulverización, patrullaje, "
                "inspección o recorrido."
            )

            self.mission_state.set_decision(
                summary="Conversando con el operador",
                reason="El operador inició la interacción con un saludo",
                impact="Esperando una intención de misión",
                intervention_required=True,
            )

            self.input_text = ""
            return

        detected_action = self.detect_action(
            user_text
        )

        if detected_action is None:
            self.feedback_text = (
                "Todavía no reconozco esa misión. "
                "Probá con pulverizar, patrullar, "
                "inspeccionar o recorrer."
            )

            self.mission_state.set_decision(
                summary="Intención no reconocida",
                reason=f'MSI no pudo interpretar: "{user_text}"',
                impact="La misión no avanzará hasta reconocer una acción",
                intervention_required=True,
            )

            self.input_text = ""
            return

        self.mission_action = detected_action

        action_label = self.ACTION_LABELS[
            detected_action
        ]

        self.conversation_stage = "location"
        self.question_text = "¿Dónde trabajamos hoy?"

        self.feedback_text = (
            f"Entendí que querés realizar una misión "
            f"de {action_label.lower()}."
        )

        self.mission_state.set_action(
            action_label
        )

        self.input_text = ""

    def process_location_input(
        self,
        user_text: str,
    ) -> None:
        self.mission_location = user_text.strip()

        self.feedback_text = (
            f"Preparando el análisis para "
            f"{self.mission_location}..."
        )

        self.mission_state.set_location(
            self.mission_location
        )

        self.next_screen = "mission"

    def reset_conversation(self) -> None:
        self.next_screen = None
        self.conversation_stage = "action"

        self.input_focused = True
        self.input_text = ""

        self.mission_action = None
        self.mission_location = None

        self.question_text = "¿Qué querés lograr?"

        self.feedback_text = (
            "Podés comenzar con: pulverizar, patrullar, "
            "inspeccionar o recorrer."
        )

        self.mission_state = MissionState()
        self.mission_state.start_interview()

    def update(
        self,
        delta_time: float,
    ) -> None:
        self.cursor_timer += delta_time

        if self.cursor_timer >= 0.5:
            self.cursor_visible = not self.cursor_visible
            self.cursor_timer = 0.0

    def render(
        self,
        screen: pygame.Surface,
    ) -> None:
        screen.fill(theme.BACKGROUND)

        screen_width, screen_height = screen.get_size()

        prompt_rect = layout.get_home_prompt_rect(
            screen_width,
            screen_height,
        )

        question_y = layout.get_home_question_y(
            screen_height
        )

        question = self.title_font.render(
            self.question_text,
            True,
            theme.TEXT,
        )

        screen.blit(
            question,
            question.get_rect(
                center=(
                    screen_width // 2,
                    question_y,
                )
            ),
        )

        pygame.draw.rect(
            screen,
            theme.SHADOW,
            prompt_rect.move(0, 3),
            border_radius=theme.PROMPT_RADIUS,
        )

        pygame.draw.rect(
            screen,
            theme.PANEL,
            prompt_rect,
            border_radius=theme.PROMPT_RADIUS,
        )

        border_color = (
            theme.PRIMARY
            if self.input_focused
            else theme.BORDER
        )

        pygame.draw.rect(
            screen,
            border_color,
            prompt_rect,
            width=1,
            border_radius=theme.PROMPT_RADIUS,
        )

        plus_rect = layout.get_plus_button_rect(
            prompt_rect
        )

        send_rect = layout.get_send_button_rect(
            prompt_rect
        )

        pygame.draw.circle(
            screen,
            theme.PRIMARY_SOFT,
            plus_rect.center,
            19,
        )

        plus = self.prompt_font.render(
            "+",
            True,
            theme.PRIMARY,
        )

        screen.blit(
            plus,
            plus.get_rect(center=plus_rect.center),
        )

        pygame.draw.circle(
            screen,
            theme.PRIMARY,
            send_rect.center,
            19,
        )

        send = self.prompt_font.render(
            "→",
            True,
            theme.PANEL,
        )

        screen.blit(
            send,
            send.get_rect(center=send_rect.center),
        )

        placeholder = (
            "Describí la misión que querés realizar..."
            if self.conversation_stage == "action"
            else "Escribí el establecimiento, lote o cuadrante..."
        )

        display_text = self.input_text or placeholder

        display_color = (
            theme.TEXT
            if self.input_text
            else theme.MUTED_TEXT
        )

        available_width = (
            send_rect.left
            - plus_rect.right
            - 32
        )

        while (
            self.prompt_font.size(display_text)[0]
            > available_width
            and len(display_text) > 3
        ):
            display_text = display_text[:-4] + "..."

        text_surface = self.prompt_font.render(
            display_text,
            True,
            display_color,
        )

        text_position = (
            plus_rect.right + 12,
            prompt_rect.centery
            - text_surface.get_height() // 2,
        )

        screen.blit(
            text_surface,
            text_position,
        )

        if (
            self.input_text
            and self.input_focused
            and self.cursor_visible
        ):
            cursor_x = (
                text_position[0]
                + text_surface.get_width()
                + 3
            )

            pygame.draw.line(
                screen,
                theme.TEXT,
                (
                    cursor_x,
                    prompt_rect.centery - 14,
                ),
                (
                    cursor_x,
                    prompt_rect.centery + 14,
                ),
                width=2,
            )

        feedback = self.feedback_font.render(
            self.feedback_text,
            True,
            theme.SECONDARY_TEXT,
        )

        screen.blit(
            feedback,
            feedback.get_rect(
                center=(
                    screen_width // 2,
                    prompt_rect.bottom + 42,
                )
            ),
        )

    def get_next_screen(self) -> str | None:
        return self.next_screen

    def get_mission_text(self) -> str:
        if (
            not self.mission_action
            or not self.mission_location
        ):
            return ""

        action_label = self.ACTION_LABELS[
            self.mission_action
        ]

        return (
            f"{action_label} · "
            f"{self.mission_location}"
        )

    def get_mission_state(self) -> MissionState:
        """
        Entrega el mismo estado vivo a MissionScreen.
        """

        return self.mission_state