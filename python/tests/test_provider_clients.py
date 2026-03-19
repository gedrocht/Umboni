"""Tests for weather provider normalization and orchestration."""

from __future__ import annotations

import json
from pathlib import Path
from unittest import TestCase
from unittest.mock import MagicMock, patch

from new_england_weather_data_fetcher.provider_clients import (
    convert_fahrenheit_to_celsius,
    convert_miles_per_hour_to_kilometers_per_hour,
    convert_seven_timer_wind_scale_to_kilometers_per_hour,
    fetch_all_normalized_weather_records,
    fetch_met_norway_records_for_location,
    fetch_national_weather_service_records_for_location,
    fetch_open_meteo_records_for_location,
    fetch_seven_timer_records_for_location,
    infer_precipitation_probability_from_weather_code,
    load_json_from_endpoint,
    normalize_timestamp_to_utc,
    parse_met_norway_response,
    parse_national_weather_service_hourly_response,
    parse_open_meteo_response,
    parse_seven_timer_response,
)
from new_england_weather_data_fetcher.weather_data_models import (
    NormalizedWeatherRecord,
    RegionalLocation,
)


class ProviderClientsTestCase(TestCase):
    """Exercises every normalization path in the provider module."""

    def setUp(self) -> None:
        self.sample_location = RegionalLocation(
            state_name="Massachusetts",
            location_name="Boston",
            latitude_degrees=42.3601,
            longitude_degrees=-71.0589,
            altitude_meters=43.0,
        )

    def load_fixture_json(self, fixture_file_name: str) -> dict[str, object]:
        fixture_path = Path(__file__).resolve().parents[2] / "samples" / "provider-fixtures" / fixture_file_name
        return json.loads(fixture_path.read_text(encoding="utf-8"))

    def test_helper_conversions_return_expected_values(self) -> None:
        self.assertAlmostEqual(10.0, convert_fahrenheit_to_celsius(50.0), places=2)
        self.assertAlmostEqual(16.0934, convert_miles_per_hour_to_kilometers_per_hour(10.0), places=4)
        self.assertEqual("2026-03-18T13:00:00Z", normalize_timestamp_to_utc("2026-03-18T13:00"))
        self.assertEqual(80.0, infer_precipitation_probability_from_weather_code("Chance Rain Showers"))
        self.assertEqual(29.0, convert_seven_timer_wind_scale_to_kilometers_per_hour(5))

    def test_fetch_all_normalized_weather_records_rejects_non_positive_hour_counts(self) -> None:
        with self.assertRaises(ValueError):
            fetch_all_normalized_weather_records(0, "artifacts/logs/test.log.jsonl")

    def test_parse_open_meteo_response_returns_two_records(self) -> None:
        response_payload = self.load_fixture_json("open-meteo-response.json")

        normalized_records = parse_open_meteo_response(self.sample_location, response_payload, maximum_hours=2)

        self.assertEqual(2, len(normalized_records))
        self.assertEqual("Open-Meteo", normalized_records[0].provider_name)
        self.assertEqual("2026-03-18T13:00:00Z", normalized_records[0].forecast_timestamp_utc)
        self.assertAlmostEqual(1015.0, normalized_records[0].surface_pressure_hectopascals)

    @patch("urllib.request.urlopen")
    def test_load_json_from_endpoint_reads_and_parses_json(self, mocked_urlopen: MagicMock) -> None:
        mocked_response_stream = MagicMock()
        mocked_response_stream.read.return_value = b'{"status":"ok"}'
        mocked_urlopen.return_value.__enter__.return_value = mocked_response_stream

        response_payload = load_json_from_endpoint("https://example.com/weather.json")

        self.assertEqual({"status": "ok"}, response_payload)

    def test_parse_national_weather_service_response_converts_units(self) -> None:
        response_payload = self.load_fixture_json("national-weather-service-hourly-response.json")

        normalized_records = parse_national_weather_service_hourly_response(
            self.sample_location,
            response_payload,
            maximum_hours=2,
        )

        self.assertEqual(2, len(normalized_records))
        self.assertEqual("National Weather Service", normalized_records[0].provider_name)
        self.assertAlmostEqual(10.0, normalized_records[0].air_temperature_celsius, places=1)
        self.assertAlmostEqual(16.0934, normalized_records[0].wind_speed_kilometers_per_hour, places=4)
        self.assertEqual("2026-03-18T13:00:00Z", normalized_records[0].forecast_timestamp_utc)

    def test_parse_met_norway_response_infers_precipitation_probability(self) -> None:
        response_payload = self.load_fixture_json("met-norway-response.json")

        normalized_records = parse_met_norway_response(self.sample_location, response_payload, maximum_hours=2)

        self.assertEqual(2, len(normalized_records))
        self.assertEqual(10.0, normalized_records[0].precipitation_probability_percentage)
        self.assertEqual(70.0, normalized_records[1].precipitation_probability_percentage)
        self.assertAlmostEqual(14.4, normalized_records[0].wind_speed_kilometers_per_hour, places=1)

    def test_parse_seven_timer_response_maps_wind_scale_and_weather_codes(self) -> None:
        response_payload = self.load_fixture_json("seven-timer-response.json")

        normalized_records = parse_seven_timer_response(self.sample_location, response_payload, maximum_hours=2)

        self.assertEqual(2, len(normalized_records))
        self.assertEqual("2026-03-18T15:00:00Z", normalized_records[0].forecast_timestamp_utc)
        self.assertEqual(12.0, normalized_records[0].wind_speed_kilometers_per_hour)
        self.assertEqual(80.0, normalized_records[1].precipitation_probability_percentage)

    @patch("new_england_weather_data_fetcher.provider_clients.load_json_from_endpoint")
    def test_fetch_open_meteo_records_for_location_uses_the_provider_wrapper(self, mocked_load_json_from_endpoint) -> None:
        mocked_load_json_from_endpoint.return_value = self.load_fixture_json("open-meteo-response.json")

        normalized_records = fetch_open_meteo_records_for_location(self.sample_location, maximum_hours=2)

        self.assertEqual(2, len(normalized_records))
        mocked_load_json_from_endpoint.assert_called_once()

    @patch("new_england_weather_data_fetcher.provider_clients.load_json_from_endpoint")
    def test_fetch_national_weather_service_records_for_location_calls_points_then_hourly(
        self,
        mocked_load_json_from_endpoint,
    ) -> None:
        mocked_load_json_from_endpoint.side_effect = [
            self.load_fixture_json("national-weather-service-points-response.json"),
            self.load_fixture_json("national-weather-service-hourly-response.json"),
        ]

        normalized_records = fetch_national_weather_service_records_for_location(
            self.sample_location,
            maximum_hours=2,
        )

        self.assertEqual(2, len(normalized_records))
        self.assertEqual(2, mocked_load_json_from_endpoint.call_count)

    @patch("new_england_weather_data_fetcher.provider_clients.load_json_from_endpoint")
    def test_fetch_met_norway_records_for_location_uses_the_provider_wrapper(self, mocked_load_json_from_endpoint) -> None:
        mocked_load_json_from_endpoint.return_value = self.load_fixture_json("met-norway-response.json")

        normalized_records = fetch_met_norway_records_for_location(self.sample_location, maximum_hours=2)

        self.assertEqual(2, len(normalized_records))
        mocked_load_json_from_endpoint.assert_called_once()

    @patch("new_england_weather_data_fetcher.provider_clients.load_json_from_endpoint")
    def test_fetch_seven_timer_records_for_location_uses_the_provider_wrapper(
        self,
        mocked_load_json_from_endpoint,
    ) -> None:
        mocked_load_json_from_endpoint.return_value = self.load_fixture_json("seven-timer-response.json")

        normalized_records = fetch_seven_timer_records_for_location(self.sample_location, maximum_hours=2)

        self.assertEqual(2, len(normalized_records))
        mocked_load_json_from_endpoint.assert_called_once()

    @patch("new_england_weather_data_fetcher.provider_clients.append_structured_log")
    @patch("new_england_weather_data_fetcher.provider_clients.fetch_seven_timer_records_for_location")
    @patch("new_england_weather_data_fetcher.provider_clients.fetch_met_norway_records_for_location")
    @patch("new_england_weather_data_fetcher.provider_clients.fetch_national_weather_service_records_for_location")
    @patch("new_england_weather_data_fetcher.provider_clients.fetch_open_meteo_records_for_location")
    @patch("new_england_weather_data_fetcher.provider_clients.load_default_new_england_locations")
    def test_fetch_all_normalized_weather_records_sorts_records(
        self,
        mocked_load_default_new_england_locations,
        mocked_fetch_open_meteo_records_for_location,
        mocked_fetch_national_weather_service_records_for_location,
        mocked_fetch_met_norway_records_for_location,
        mocked_fetch_seven_timer_records_for_location,
        mocked_append_structured_log,
    ) -> None:
        mocked_load_default_new_england_locations.return_value = [self.sample_location]
        mocked_fetch_open_meteo_records_for_location.return_value = [
            NormalizedWeatherRecord(
                provider_name="Open-Meteo",
                state_name="Massachusetts",
                location_name="Boston",
                latitude_degrees=42.3601,
                longitude_degrees=-71.0589,
                altitude_meters=43.0,
                forecast_hour_offset=2,
                forecast_timestamp_utc="2026-03-18T14:00:00Z",
                air_temperature_celsius=11.0,
                relative_humidity_percentage=60.0,
                wind_speed_kilometers_per_hour=10.0,
                precipitation_probability_percentage=20.0,
                surface_pressure_hectopascals=1014.0,
                cloud_cover_percentage=55.0,
            )
        ]
        mocked_fetch_national_weather_service_records_for_location.return_value = [
            NormalizedWeatherRecord(
                provider_name="National Weather Service",
                state_name="Massachusetts",
                location_name="Boston",
                latitude_degrees=42.3601,
                longitude_degrees=-71.0589,
                altitude_meters=43.0,
                forecast_hour_offset=1,
                forecast_timestamp_utc="2026-03-18T13:00:00Z",
                air_temperature_celsius=10.0,
                relative_humidity_percentage=61.0,
                wind_speed_kilometers_per_hour=12.0,
                precipitation_probability_percentage=30.0,
                surface_pressure_hectopascals=-9999.0,
                cloud_cover_percentage=35.0,
            )
        ]
        mocked_fetch_met_norway_records_for_location.return_value = []
        mocked_fetch_seven_timer_records_for_location.return_value = []

        normalized_records = fetch_all_normalized_weather_records(24, "artifacts/logs/test.log.jsonl")

        self.assertEqual(2, len(normalized_records))
        self.assertEqual(1, normalized_records[0].forecast_hour_offset)
        self.assertEqual("National Weather Service", normalized_records[0].provider_name)
        self.assertGreaterEqual(mocked_append_structured_log.call_count, 1)

    @patch("new_england_weather_data_fetcher.provider_clients.append_structured_log")
    @patch("new_england_weather_data_fetcher.provider_clients.fetch_seven_timer_records_for_location")
    @patch("new_england_weather_data_fetcher.provider_clients.fetch_met_norway_records_for_location")
    @patch("new_england_weather_data_fetcher.provider_clients.fetch_national_weather_service_records_for_location")
    @patch("new_england_weather_data_fetcher.provider_clients.fetch_open_meteo_records_for_location")
    @patch("new_england_weather_data_fetcher.provider_clients.load_default_new_england_locations")
    def test_fetch_all_normalized_weather_records_continues_after_one_provider_failure(
        self,
        mocked_load_default_new_england_locations,
        mocked_fetch_open_meteo_records_for_location,
        mocked_fetch_national_weather_service_records_for_location,
        mocked_fetch_met_norway_records_for_location,
        mocked_fetch_seven_timer_records_for_location,
        mocked_append_structured_log,
    ) -> None:
        mocked_load_default_new_england_locations.return_value = [self.sample_location]
        mocked_fetch_open_meteo_records_for_location.return_value = []
        mocked_fetch_national_weather_service_records_for_location.side_effect = RuntimeError("temporary failure")
        mocked_fetch_met_norway_records_for_location.return_value = [
            NormalizedWeatherRecord(
                provider_name="MET Norway",
                state_name="Massachusetts",
                location_name="Boston",
                latitude_degrees=42.3601,
                longitude_degrees=-71.0589,
                altitude_meters=43.0,
                forecast_hour_offset=1,
                forecast_timestamp_utc="2026-03-18T13:00:00Z",
                air_temperature_celsius=10.0,
                relative_humidity_percentage=61.0,
                wind_speed_kilometers_per_hour=10.0,
                precipitation_probability_percentage=20.0,
                surface_pressure_hectopascals=1014.0,
                cloud_cover_percentage=45.0,
            )
        ]
        mocked_fetch_seven_timer_records_for_location.return_value = []

        normalized_records = fetch_all_normalized_weather_records(24, "artifacts/logs/test.log.jsonl")

        self.assertEqual(1, len(normalized_records))
        self.assertEqual("MET Norway", normalized_records[0].provider_name)
        self.assertGreaterEqual(mocked_append_structured_log.call_count, 2)
