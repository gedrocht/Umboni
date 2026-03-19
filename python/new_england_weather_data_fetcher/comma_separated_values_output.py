"""Writes normalized provider records in the exact format required by Fortran."""

from __future__ import annotations

import csv
from pathlib import Path

from .weather_data_models import NormalizedWeatherRecord


def write_normalized_records_to_csv(
    output_csv_path: str,
    normalized_weather_records: list[NormalizedWeatherRecord],
) -> None:
    """Writes normalized provider records to a deterministic comma-separated-values file."""

    output_path = Path(output_csv_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    field_names = [
        "provider_name",
        "state_name",
        "location_name",
        "latitude_degrees",
        "longitude_degrees",
        "altitude_meters",
        "forecast_hour_offset",
        "forecast_timestamp_utc",
        "air_temperature_celsius",
        "relative_humidity_percentage",
        "wind_speed_kilometers_per_hour",
        "precipitation_probability_percentage",
        "surface_pressure_hectopascals",
        "cloud_cover_percentage",
    ]

    with output_path.open("w", encoding="utf-8", newline="") as output_stream:
        csv_writer = csv.DictWriter(output_stream, fieldnames=field_names)
        csv_writer.writeheader()
        for normalized_weather_record in normalized_weather_records:
            csv_writer.writerow(normalized_weather_record.to_csv_row())
