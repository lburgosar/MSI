"""
===============================================================================
MSI Mission Studio - Theme
===============================================================================

Centraliza la configuración visual general de Mission Studio.

No contiene posiciones absolutas de las pantallas. La distribución adaptable
se calcula en core/layout.py según el tamaño disponible.

===============================================================================
"""


# =============================================================================
# VENTANA
# =============================================================================

WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 800

MIN_WINDOW_WIDTH = 520
MIN_WINDOW_HEIGHT = 420

WINDOW_TITLE = "MSI Mission Studio"

FPS = 60


# =============================================================================
# COLORES
# =============================================================================

BACKGROUND = (245, 245, 247)
PANEL = (255, 255, 255)

BORDER = (220, 220, 224)
SHADOW = (232, 232, 235)

TEXT = (30, 30, 32)
SECONDARY_TEXT = (125, 125, 130)
MUTED_TEXT = (165, 165, 170)

PRIMARY = (0, 122, 255)
PRIMARY_SOFT = (232, 243, 255)
PRIMARY_HOVER = (0, 106, 224)

VINEYARD_ROW = (64, 92, 58)
GRID_LINE = (226, 226, 230)

SUCCESS = (52, 168, 83)
WARNING = (225, 156, 46)
DANGER = (205, 70, 70)


# =============================================================================
# TIPOGRAFÍA
# =============================================================================

SPLASH_TITLE_SIZE = 52
TITLE_SIZE = 38
SUBTITLE_SIZE = 20
PROMPT_SIZE = 21
TEXT_SIZE = 17
SMALL_TEXT_SIZE = 14


# =============================================================================
# COMPONENTES
# =============================================================================

PROMPT_HEIGHT = 68
COMPACT_PROMPT_HEIGHT = 58

PROMPT_RADIUS = 25
BUTTON_RADIUS = 20

TOUCH_TARGET_SIZE = 48
