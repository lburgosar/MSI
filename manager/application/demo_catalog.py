"""Catálogo reproducible de recursos y escenarios para Simulator V2."""

from __future__ import annotations

from domain.geography import Altitude, AltitudeReference, GeoPoint, GeoPolygon, MapBounds
from domain.mission import MissionConfiguration, MissionIntent
from domain.resources import (
    CommunicationState,
    ConsumableState,
    EnergyState,
    Resource,
    ResourceType,
    Sensor,
)


DEMO_BOUNDS = MapBounds(-34.6120, -58.4220, -34.5920, -58.3820)


def point(latitude: float, longitude: float, altitude_m: float = 3.0) -> GeoPoint:
    return GeoPoint(
        latitude,
        longitude,
        Altitude(altitude_m, AltitudeReference.ABOVE_CANOPY, uncertainty_m=0.3),
    )


def demo_area() -> GeoPolygon:
    return GeoPolygon(
        (
            point(-34.5950, -58.4160),
            point(-34.5950, -58.3880),
            point(-34.6085, -58.3880),
            point(-34.6085, -58.4160),
        )
    )


def demo_geofence() -> GeoPolygon:
    return GeoPolygon(
        (
            point(DEMO_BOUNDS.north, DEMO_BOUNDS.west),
            point(DEMO_BOUNDS.north, DEMO_BOUNDS.east),
            point(DEMO_BOUNDS.south, DEMO_BOUNDS.east),
            point(DEMO_BOUNDS.south, DEMO_BOUNDS.west),
        )
    )


def demo_resources() -> list[Resource]:
    """Flota heterogénea; sus diferencias afectan selección y preflight."""

    return [
        Resource(
            "D1", "Aquila Spray 20", ResourceType.AERIAL,
            point(-34.6095, -58.4180),
            capabilities={"flight", "precision_spraying", "rgb_imaging"},
            payloads={"spray_payload"},
            sensors=[Sensor("D1-RGB", "rgb_camera", data_kind="video")],
            energy=EnergyState(92, 920, 22),
            consumable=ConsumableState("spray_product", 18.5, 20),
            communication=CommunicationState(97, 24),
            endurance_minutes=34,
            max_speed_m_s=8,
        ),
        Resource(
            "D2", "Aquila Spray 16", ResourceType.AERIAL,
            point(-34.6102, -58.4145),
            capabilities={"flight", "precision_spraying", "multispectral_imaging"},
            payloads={"spray_payload"},
            sensors=[Sensor("D2-MS", "multispectral", data_kind="image")],
            energy=EnergyState(78, 760, 22),
            consumable=ConsumableState("spray_product", 13.0, 16),
            communication=CommunicationState(91, 31),
            endurance_minutes=27,
            max_speed_m_s=7,
        ),
        Resource(
            "D3", "Tero Thermal", ResourceType.AERIAL,
            point(-34.6097, -58.4110),
            capabilities={"flight", "area_patrol", "thermal_imaging", "incident_assessment"},
            sensors=[Sensor("D3-TH", "thermal_camera", data_kind="thermal")],
            energy=EnergyState(87, 640, 18),
            communication=CommunicationState(94, 28),
            endurance_minutes=38,
            max_speed_m_s=11,
        ),
        Resource(
            "D4", "Hornero Endurance", ResourceType.AERIAL,
            point(-34.6104, -58.4075),
            capabilities={"flight", "area_patrol", "rgb_imaging", "communications_relay", "incident_assessment"},
            sensors=[Sensor("D4-RGB", "rgb_camera", data_kind="video")],
            energy=EnergyState(68, 1200, 20),
            communication=CommunicationState(99, 19),
            endurance_minutes=58,
            max_speed_m_s=13,
        ),
    ]


def demo_configuration(intent: MissionIntent) -> MissionConfiguration:
    common: dict[str, object] = {
        "wind_m_s": 2.7,
        "wind_direction_deg": 235.0,
        "temperature_c": 21.0,
    }
    if intent is MissionIntent.PRECISION_SPRAYING:
        parameters = {
            **common,
            "area_hectares": 3.6,
            "dose_l_ha": 7.5,
            "swath_width_m": 5.0,
            "overlap_percent": 10.0,
            "flight_speed_m_s": 5.0,
            "altitude_above_canopy_m": 3.0,
            "max_wind_m_s": 5.0,
            "droplet_class": "medium",
            "product": "Demo Mix A",
        }
        name = "Pulverización de precisión · Las Marías"
    elif intent is MissionIntent.AUTONOMOUS_PATROL:
        parameters = {
            **common,
            "coverage_overlap_percent": 22.0,
            "flight_speed_m_s": 8.0,
            "altitude_agl_m": 35.0,
            "required_sensor": "rgb_imaging",
            "revisit_minutes": 12.0,
        }
        name = "Patrulla autónoma · Las Marías"
    else:
        parameters = {
            **common,
            "incident_lat": -34.6015,
            "incident_lon": -58.3970,
            "priority": "high",
            "required_capability": "incident_assessment",
            "authorization_required": True,
        }
        name = "Respuesta heterogénea · Las Marías"

    return MissionConfiguration(intent, name, demo_area(), demo_geofence(), parameters)
