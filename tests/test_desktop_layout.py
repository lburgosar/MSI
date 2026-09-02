from __future__ import annotations

import sys
import unittest
from pathlib import Path


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPOSITORY_ROOT / "manager"))

from desktop_layout import WindowPlacement, calculate_layout


class DesktopLayoutTests(unittest.TestCase):
    def setUp(self) -> None:
        self.area = WindowPlacement(0, 0, 1366, 720)

    def test_vertical_layout_uses_full_area_without_overlap(self) -> None:
        layout = calculate_layout(self.area, "vertical", (16, 39))

        self.assertEqual(layout.monitor, WindowPlacement(0, 0, 1350, 206))
        self.assertEqual(layout.studio, WindowPlacement(0, 251, 1350, 430))
        self.assertEqual(layout.studio.y + layout.studio.height + 39, 720)

    def test_horizontal_layout_keeps_independent_equal_height_windows(self) -> None:
        layout = calculate_layout(self.area, "horizontal", (16, 39))

        self.assertEqual(layout.studio.height, 681)
        self.assertEqual(layout.monitor.height, 681)
        self.assertEqual(layout.studio.width + layout.monitor.width + 6 + 32, 1366)

    def test_unknown_layout_is_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "Unsupported desktop layout"):
            calculate_layout(self.area, "diagonal")


if __name__ == "__main__":
    unittest.main()
