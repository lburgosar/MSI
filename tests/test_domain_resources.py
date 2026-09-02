from __future__ import annotations

import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "manager"))

from domain.geography import Altitude, AltitudeReference, GeoPoint, MapBounds
from domain.resources import Availability, EnergyState, Resource, ResourceType
from providers.resources import SimulatedResourceProvider


def resource(resource_id: str, capability: str = "spraying") -> Resource:
    return Resource(
        resource_id=resource_id,
        display_name=resource_id,
        resource_type=ResourceType.AERIAL,
        position=GeoPoint(-34.60, -58.40, Altitude(5, AltitudeReference.AGL)),
        capabilities={"flight", capability},
        energy=EnergyState(82, 620),
    )


class ResourceDomainTests(unittest.TestCase):
    def test_provider_adds_updates_and_withdraws_real_resource_state(self) -> None:
        provider = SimulatedResourceProvider([resource("D1")])
        provider.add_resource(resource("D2", "thermal_imaging"))
        d2 = provider.get_resource("D2")
        d2.energy.percent = 41
        provider.update_resource(d2)
        provider.withdraw_resource("D1")

        self.assertEqual(provider.get_resource("D2").energy.percent, 41)
        self.assertEqual(provider.get_resource("D1").availability, Availability.WITHDRAWN)
        self.assertFalse(provider.get_resource("D1").can("spraying"))

    def test_map_bounds_round_trip_geographic_coordinates(self) -> None:
        bounds = MapBounds(-34.61, -58.42, -34.59, -58.38)
        point = GeoPoint(-34.60, -58.40, Altitude(4, AltitudeReference.ABOVE_CANOPY))
        x, y = bounds.to_normalized(point)
        restored = bounds.from_normalized(x, y, point.altitude)

        self.assertAlmostEqual(x, 0.5)
        self.assertAlmostEqual(y, 0.5)
        self.assertAlmostEqual(restored.latitude, point.latitude)
        self.assertEqual(restored.altitude.reference, AltitudeReference.ABOVE_CANOPY)


if __name__ == "__main__":
    unittest.main()
