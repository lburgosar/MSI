"""
===============================================================================
MSI Mission Studio - Responsive Layout
===============================================================================

Calcula posiciones y tamaños en función de la superficie disponible.

Permite que la misma interfaz se reorganice para:

- escritorio;
- tablet;
- pantallas angostas.

Las pantallas consultan estas funciones en cada renderizado, por lo que
pueden responder inmediatamente al redimensionamiento de la ventana.

===============================================================================
"""

from __future__ import annotations

import pygame

from core import theme


def get_layout_mode(width: int) -> str:
    """
    Determina el modo de distribución según el ancho disponible.
    """

    if width < 680:
        return "mobile"

    if width < 1050:
        return "tablet"

    return "desktop"


def get_horizontal_margin(width: int) -> int:
    """
    Calcula un margen adaptable con límites razonables.
    """

    return max(20, min(72, int(width * 0.055)))


def get_home_prompt_rect(
    screen_width: int,
    screen_height: int,
) -> pygame.Rect:
    """
    Calcula el rectángulo del prompt central de HomeScreen.
    """

    mode = get_layout_mode(screen_width)
    margin = get_horizontal_margin(screen_width)

    if screen_height < 360:
        prompt_width = min(940, screen_width - margin * 2)
        prompt_height = theme.COMPACT_PROMPT_HEIGHT
        prompt_y = 82
    elif mode == "mobile":
        prompt_width = screen_width - margin * 2
        prompt_height = 64
        prompt_y = int(screen_height * 0.48)

    elif mode == "tablet":
        prompt_width = min(760, screen_width - margin * 2)
        prompt_height = theme.PROMPT_HEIGHT
        prompt_y = int(screen_height * 0.49)

    else:
        prompt_width = min(820, screen_width - margin * 2)
        prompt_height = theme.PROMPT_HEIGHT
        prompt_y = int(screen_height * 0.49)

    return pygame.Rect(
        (screen_width - prompt_width) // 2,
        prompt_y,
        prompt_width,
        prompt_height,
    )


def get_home_question_y(screen_height: int) -> int:
    """
    Posición vertical de la pregunta principal.
    """

    if screen_height < 360:
        return 42
    return max(135, int(screen_height * 0.34))


def get_mission_header_rect(
    screen_width: int,
    screen_height: int,
) -> pygame.Rect:
    """
    Área superior de información de la misión.
    """

    margin = get_horizontal_margin(screen_width)

    ultra_compact = screen_height < 360
    compact = screen_height < 560

    return pygame.Rect(
        margin,
        4 if ultra_compact else (12 if compact else 24),
        screen_width - margin * 2,
        58 if ultra_compact else (82 if compact else 104),
    )


def get_workspace_rect(
    screen_width: int,
    screen_height: int,
) -> pygame.Rect:
    """
    Calcula el área principal del workspace.

    Reserva espacio para el encabezado superior y el prompt inferior.
    """

    mode = get_layout_mode(screen_width)
    margin = get_horizontal_margin(screen_width)

    ultra_compact = screen_height < 360
    compact_height = screen_height < 560
    top = 72 if ultra_compact else (102 if compact_height else 145)

    if mode == "mobile":
        bottom_reserved = 110
        workspace_margin = 14

    else:
        bottom_reserved = 78 if ultra_compact else (88 if compact_height else 100)
        workspace_margin = margin

    return pygame.Rect(
        workspace_margin,
        top,
        screen_width - workspace_margin * 2,
        max(72 if ultra_compact else 220, screen_height - top - bottom_reserved),
    )


def get_bottom_prompt_rect(
    screen_width: int,
    screen_height: int,
) -> pygame.Rect:
    """
    Calcula el prompt compacto inferior.
    """

    mode = get_layout_mode(screen_width)
    margin = get_horizontal_margin(screen_width)

    if mode == "mobile":
        prompt_width = screen_width - margin * 2
    else:
        prompt_width = min(940, screen_width - margin * 2)

    prompt_height = theme.COMPACT_PROMPT_HEIGHT

    return pygame.Rect(
        (screen_width - prompt_width) // 2,
        screen_height - prompt_height - (8 if screen_height < 360 else 22),
        prompt_width,
        prompt_height,
    )


def get_send_button_rect(prompt_rect: pygame.Rect) -> pygame.Rect:
    """
    Botón de envío ubicado dentro del extremo derecho del prompt.
    """

    size = theme.TOUCH_TARGET_SIZE

    return pygame.Rect(
        prompt_rect.right - size - 10,
        prompt_rect.centery - size // 2,
        size,
        size,
    )


def get_plus_button_rect(prompt_rect: pygame.Rect) -> pygame.Rect:
    """
    Botón de entrada adicional ubicado a la izquierda del prompt.
    """

    size = theme.TOUCH_TARGET_SIZE

    return pygame.Rect(
        prompt_rect.left + 10,
        prompt_rect.centery - size // 2,
        size,
        size,
    )


def get_finish_button_rect(
    screen_width: int,
    screen_height: int,
) -> pygame.Rect:
    """
    Botón táctil para finalizar una misión.
    """

    margin = get_horizontal_margin(screen_width)

    return pygame.Rect(
        screen_width - margin - 150,
        8 if screen_height < 360 else (20 if screen_height < 560 else 36),
        150,
        44,
    )
