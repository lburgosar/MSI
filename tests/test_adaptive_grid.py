from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from experiments.msi_next_geospatial import AdaptiveGrid, SpatialSelection
from experiments.msi_next_geospatial.adaptive_grid import GeographicPoint


class AdaptiveGridTests(unittest.TestCase):
    def test_zoom_changes_intent_resolution(self) -> None:
        self.assertEqual(AdaptiveGrid.resolution_m(10), 500.0)
        self.assertEqual(AdaptiveGrid.resolution_m(15), 50.0)
        self.assertEqual(AdaptiveGrid.resolution_m(19), 5.0)

    def test_selection_exports_geographic_geometry_not_visual_ids(self) -> None:
        selection = SpatialSelection()
        cell = AdaptiveGrid.cell_at(GeographicPoint(-34.601, -58.401), 15)
        selection.paint(cell)

        result = selection.to_geojson()

        self.assertEqual(result["type"], "MultiPolygon")
        self.assertEqual(len(result["coordinates"]), 1)
        self.assertNotIn("row", result)
        self.assertNotIn("column", result)

    def test_existing_geometry_survives_zoom_resolution_change(self) -> None:
        selection = SpatialSelection()
        point = GeographicPoint(-34.601, -58.401)
        coarse = AdaptiveGrid.cell_at(point, 11)
        fine = AdaptiveGrid.cell_at(point, 17)
        selection.paint(coarse)
        selection.paint(fine)

        self.assertEqual(len(selection.polygons), 2)
        self.assertNotEqual(coarse.size_m, fine.size_m)

    def test_erase_only_removes_matching_resolution_cell(self) -> None:
        selection = SpatialSelection()
        point = GeographicPoint(-34.601, -58.401)
        coarse = AdaptiveGrid.cell_at(point, 11)
        fine = AdaptiveGrid.cell_at(point, 17)
        selection.paint(coarse); selection.paint(fine)
        selection.erase(fine)

        self.assertEqual(list(selection.polygons.values()), [coarse.polygon])


if __name__ == "__main__":
    unittest.main()
