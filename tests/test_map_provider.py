from __future__ import annotations

import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "manager"))

from application.demo_catalog import DEMO_BOUNDS, point
from maps.providers import LocalMapProvider


class MapProviderTests(unittest.TestCase):
    def test_local_provider_exposes_status_and_world_projection(self) -> None:
        provider = LocalMapProvider(DEMO_BOUNDS)
        x, y = provider.world_to_map(point(-34.602, -58.402))
        self.assertGreaterEqual(x, 0)
        self.assertLessEqual(x, 1)
        self.assertEqual(provider.descriptor()["cartography_status"], "demo_local_not_certified")


if __name__ == "__main__":
    unittest.main()
