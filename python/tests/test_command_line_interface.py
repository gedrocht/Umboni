"""Tests for the command-line entry point."""

from __future__ import annotations

from io import StringIO
from unittest import TestCase
from unittest.mock import patch
from contextlib import redirect_stderr

from new_england_weather_data_fetcher.command_line_interface import build_argument_parser, main
from new_england_weather_data_fetcher.weather_data_models import NormalizedWeatherRecord


class CommandLineInterfaceTestCase(TestCase):
    """Exercises the main command-line flow."""

    def test_build_argument_parser_uses_expected_defaults(self) -> None:
        parsed_arguments = build_argument_parser().parse_args([])

        self.assertEqual("artifacts/generated/provider-observations.csv", parsed_arguments.output_csv)
        self.assertEqual(24, parsed_arguments.maximum_hours)

    @patch("new_england_weather_data_fetcher.command_line_interface.append_structured_log")
    @patch("new_england_weather_data_fetcher.command_line_interface.write_normalized_records_to_csv")
    @patch("new_england_weather_data_fetcher.command_line_interface.fetch_all_normalized_weather_records")
    @patch("sys.argv", ["weather-fetcher"])
    def test_main_returns_zero_when_fetch_succeeds(
        self,
        mocked_fetch_all_normalized_weather_records,
        mocked_write_normalized_records_to_csv,
        mocked_append_structured_log,
    ) -> None:
        mocked_fetch_all_normalized_weather_records.return_value = [
            NormalizedWeatherRecord(
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
        ]

        exit_code = main()

        self.assertEqual(0, exit_code)
        mocked_write_normalized_records_to_csv.assert_called_once()
        self.assertEqual(2, mocked_append_structured_log.call_count)

    @patch("new_england_weather_data_fetcher.command_line_interface.append_structured_log")
    @patch("new_england_weather_data_fetcher.command_line_interface.fetch_all_normalized_weather_records")
    @patch("sys.argv", ["weather-fetcher"])
    def test_main_returns_one_when_fetch_raises_exception(
        self,
        mocked_fetch_all_normalized_weather_records,
        mocked_append_structured_log,
    ) -> None:
        mocked_fetch_all_normalized_weather_records.side_effect = RuntimeError("simulated failure")

        with redirect_stderr(StringIO()):
            exit_code = main()

        self.assertEqual(1, exit_code)
        self.assertEqual(2, mocked_append_structured_log.call_count)

    @patch("new_england_weather_data_fetcher.command_line_interface.append_structured_log")
    @patch("sys.argv", ["weather-fetcher", "--maximum-hours", "0"])
    def test_main_returns_one_when_maximum_hours_is_not_positive(
        self,
        mocked_append_structured_log,
    ) -> None:
        with redirect_stderr(StringIO()):
            exit_code = main()

        self.assertEqual(1, exit_code)
        self.assertEqual(2, mocked_append_structured_log.call_count)
