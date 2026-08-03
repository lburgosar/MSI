"""
===============================================================================
MSI Theme
===============================================================================

Este módulo centraliza toda la configuración visual de MSI Mission Studio.

¿Por qué existe?

Queremos mantener separados:

- el diseño visual;
- la lógica de la aplicación;
- el comportamiento de las pantallas.

De esta forma, si más adelante cambiamos colores, tamaños o tipografías,
solo será necesario modificar este archivo.

===============================================================================
"""


# =============================================================================
# CONFIGURACIÓN DE LA VENTANA
# =============================================================================

# Ancho de la ventana principal, expresado en píxeles.
WINDOW_WIDTH = 1280

# Alto de la ventana principal, expresado en píxeles.
WINDOW_HEIGHT = 800

# Texto mostrado en la barra de título del sistema operativo.
WINDOW_TITLE = "MSI Mission Studio"

# Cantidad máxima de cuadros por segundo.
FPS = 60


# =============================================================================
# PALETA DE COLORES
# =============================================================================

# Fondo principal de la aplicación.
# Es un gris muy claro para evitar el blanco puro y mantener una estética suave.
BACKGROUND = (245, 245, 247)

# Fondo de paneles, tarjetas y componentes destacados.
PANEL = (255, 255, 255)

# Bordes sutiles para separar componentes sin generar ruido visual.
BORDER = (228, 228, 230)

# Color principal del texto.
TEXT = (32, 32, 32)

# Color utilizado en acciones principales, estados activos y controles.
PRIMARY = (0, 122, 255)

# Color utilizado en descripciones, ayudas y textos secundarios.
SECONDARY_TEXT = (120, 120, 120)


# =============================================================================
# TIPOGRAFÍA
# =============================================================================

# Tamaño del título principal.
TITLE_SIZE = 42

# Tamaño de los subtítulos.
SUBTITLE_SIZE = 22

# Tamaño del texto general.
TEXT_SIZE = 18