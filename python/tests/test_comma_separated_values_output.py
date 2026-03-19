"""Tests for CSV serialization."""

from __future__ import annotations

import tempfile
from pathlib import Path
from unittest import TestCase

from new_england_weather_data_fetcher.comma_separated_values_output import (
    write_normalized_records_to_csv,
)
from new_england_weather_data_fetcher.weather_data_models import NormalizedWeatherRecord


class CommaSeparatedValuesOutputTestCase(TestCase):
    """Verifies that normalized records are written with the expected header and values."""

    def test_write_normalized_records_to_csv_writes_header_and_row(self) -> None:
        sample_record = NormalizedWeatherRecord(
            provider_name="Open-Meteo",
            state_name="Massachusetts",
            location_name="Boston",
            latitude_degrees=42.3601,
            longitude_degrees=-71.0589,
            altitude_meters=43.0,
            forecast_hour_offset=1,
            forecast_timestamp_utc="2026-03-18T13:00:00Z",
            air_temperature_celsius=10.0,
            relative_humidity_percentage=62.0,
            wind_speed_kilometers_per_hour=15.0,
            precipitation_probability_percentage=20.0,
            surface_pressure_hectopascals=1015.0,
            cloud_cover_percentage=55.0,
        )

        with tempfile.TemporaryDirectory() as temporary_directory:
            output_path = Path(temporary_directory) / "normalized-records.csv"
            write_normalized_records_to_csv(str(output_path), [sample_record])
            written_text = output_path.read_text(encoding="utf-8")

        self.assertIn("provider_name,state_name,location_name", written_text)
        self.assertIn("Open-Meteo,Massachusetts,Boston", written_text)

