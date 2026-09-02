"""Cálculo de ventanas desktop, independiente de las aplicaciones MSI."""

from __future__ import annotations

import ctypes
from dataclasses import dataclass


@dataclass(frozen=True)
class WindowPlacement:
    x: int
    y: int
    width: int
    height: int


@dataclass(frozen=True)
class DesktopLayout:
    work_area: WindowPlacement
    monitor: WindowPlacement
    studio: WindowPlacement


class Rect(ctypes.Structure):
    _fields_ = [("left", ctypes.c_long), ("top", ctypes.c_long),
                ("right", ctypes.c_long), ("bottom", ctypes.c_long)]


def get_windows_work_area() -> WindowPlacement:
    """Consulta el área útil, excluyendo la barra de tareas de Windows."""

    rect = Rect()
    success = ctypes.windll.user32.SystemParametersInfoW(0x0030, 0, ctypes.byref(rect), 0)
    if not success:
        raise OSError("Windows work area could not be detected")
    return WindowPlacement(rect.left, rect.top, rect.right - rect.left, rect.bottom - rect.top)


def get_windows_chrome() -> tuple[int, int]:
    """Estima bordes y barra de título para ubicar ventanas sin solaparlas."""

    get_metric = ctypes.windll.user32.GetSystemMetrics
    horizontal_frame = get_metric(32) + get_metric(92)
    vertical_frame = get_metric(33) + get_metric(92)
    return horizontal_frame * 2, get_metric(4) + vertical_frame * 2


def calculate_layout(
    work_area: WindowPlacement,
    mode: str = "vertical",
    window_chrome: tuple[int, int] = (0, 0),
) -> DesktopLayout:
    """Distribuye ventanas sin introducir dependencias entre Studio y Monitor."""

    gap = 6
    chrome_width, chrome_height = window_chrome
    if mode == "vertical":
        monitor_outer_height = round(work_area.height * 0.34)
        studio_outer_height = work_area.height - monitor_outer_height - gap
        client_width = work_area.width - chrome_width
        monitor = WindowPlacement(
            work_area.x,
            work_area.y,
            client_width,
            monitor_outer_height - chrome_height,
        )
        studio = WindowPlacement(
            work_area.x,
            work_area.y + monitor_outer_height + gap,
            client_width,
            studio_outer_height - chrome_height,
        )
    elif mode == "horizontal":
        studio_outer_width = (work_area.width - gap) // 2
        monitor_outer_width = work_area.width - gap - studio_outer_width
        client_height = work_area.height - chrome_height
        studio = WindowPlacement(
            work_area.x,
            work_area.y,
            studio_outer_width - chrome_width,
            client_height,
        )
        monitor = WindowPlacement(
            work_area.x + studio_outer_width + gap,
            work_area.y,
            monitor_outer_width - chrome_width,
            client_height,
        )
    else:
        raise ValueError(f"Unsupported desktop layout: {mode}")

    return DesktopLayout(work_area=work_area, monitor=monitor, studio=studio)
