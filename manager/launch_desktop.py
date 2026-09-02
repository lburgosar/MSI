"""Inicia las interfaces independientes y las organiza para evaluación desktop."""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
import time
from pathlib import Path

from desktop_layout import (
    WindowPlacement,
    calculate_layout,
    get_windows_chrome,
    get_windows_work_area,
)


MANAGER_ROOT = Path(__file__).resolve().parent


def window_environment(placement: WindowPlacement) -> dict[str, str]:
    environment = os.environ.copy()
    environment["SDL_VIDEO_WINDOW_POS"] = f"{placement.x},{placement.y}"
    environment["MSI_WINDOW_WIDTH"] = str(placement.width)
    environment["MSI_WINDOW_HEIGHT"] = str(placement.height)
    return environment


def launch(script_directory: Path, placement: WindowPlacement) -> subprocess.Popen[bytes]:
    return subprocess.Popen(
        [sys.executable, str(script_directory / "main.py")],
        cwd=script_directory,
        env=window_environment(placement),
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Organiza MSI Studio y Monitor")
    parser.add_argument(
        "layout", nargs="?", choices=("vertical", "horizontal"), default="vertical"
    )
    arguments = parser.parse_args()
    layout = calculate_layout(
        get_windows_work_area(), arguments.layout, get_windows_chrome()
    )

    # Monitor se inicia primero para ignorar cualquier estado de una misión vieja.
    launch(MANAGER_ROOT / "mission_monitor", layout.monitor)
    time.sleep(0.8)
    launch(MANAGER_ROOT / "mission_studio", layout.studio)

    area = layout.work_area
    print(f"Área útil: {area.width}x{area.height} en ({area.x}, {area.y})")
    print(f"Monitor: {layout.monitor.width}x{layout.monitor.height}")
    print(f"Studio: {layout.studio.width}x{layout.studio.height}")
    print(f"Layout: {arguments.layout}")


if __name__ == "__main__":
    main()
