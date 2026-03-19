"""Defines the default New England locations covered by the system."""

from __future__ import annotations

from .weather_data_models import RegionalLocation


def load_default_new_england_locations() -> list[RegionalLocation]:
    """Returns one representative location per New England state."""

    return [
        RegionalLocation(
            state_name="Massachusetts",
            location_name="Boston",
            latitude_degrees=42.3601,
            longitude_degrees=-71.0589,
            altitude_meters=43.0,
        ),
        RegionalLocation(
            state_name="Maine",
            location_name="Portland",
            latitude_degrees=43.6591,
            longitude_degrees=-70.2568,
            altitude_meters=19.0,
        ),
        RegionalLocation(
            state_name="New Hampshire",
            location_name="Concord",
            latitude_degrees=43.2081,
            longitude_degrees=-71.5376,
            altitude_meters=88.0,
        ),
        RegionalLocation(
            state_name="Vermont",
            location_name="Burlington",
            latitude_degrees=44.4759,
            longitude_degrees=-73.2121,
            altitude_meters=61.0,
        ),
        RegionalLocation(
            state_name="Rhode Island",
            location_name="Providence",
            latitude_degrees=41.8240,
            longitude_degrees=-71.4128,
            altitude_meters=23.0,
        ),
        RegionalLocation(
            state_name="Connecticut",
            location_name="Hartford",
            latitude_degrees=41.7658,
            longitude_degrees=-72.6734,
            altitude_meters=18.0,
        ),
    ]

