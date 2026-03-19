"""Domain models shared across provider clients and output writers."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class RegionalLocation:
    """Describes one representative New England location."""

    state_name: str
    location_name: str
    latitude_degrees: float
    longitude_degrees: float
    altitude_meters: float


@dataclass(frozen=True, slots=True)
class NormalizedWeatherRecord:
    """Stores one normalized provider record in the format expected by Fortran."""

    provider_name: str
    state_name: str
    location_name: str
    latitude_degrees: float
    longitude_degrees: float
    altitude_meters: float
    forecast_hour_offset: int
    forecast_timestamp_utc: str
    air_temperature_celsius: float
    relative_humidity_percentage: float
    wind_speed_kilometers_per_hour: float
    precipitation_probability_percentage: float
    surface_pressure_hectopascals: float
    cloud_cover_percentage: float

    def to_csv_row(self) -> dict[str, str]:
        """Serializes the record to a CSV-ready dictionary with descriptive keys."""

        return {
            "provider_name": self.provider_name,
            "state_name": self.state_name,
            "location_name": self.location_name,
            "latitude_degrees": f"{self.latitude_degrees:.4f}",
            "longitude_degrees": f"{self.longitude_degrees:.4f}",
            "altitude_meters": f"{self.altitude_meters:.1f}",
            "forecast_hour_offset": str(self.forecast_hour_offset),
            "forecast_timestamp_utc": self.forecast_timestamp_utc,
            "air_temperature_celsius": f"{self.air_temperature_celsius:.2f}",
            "relative_humidity_percentage": f"{self.relative_humidity_percentage:.2f}",
            "wind_speed_kilometers_per_hour": f"{self.wind_speed_kilometers_per_hour:.2f}",
            "precipitation_probability_percentage": f"{self.precipitation_probability_percentage:.2f}",
            "surface_pressure_hectopascals": f"{self.surface_pressure_hectopascals:.2f}",
            "cloud_cover_percentage": f"{self.cloud_cover_percentage:.2f}",
        }

