"""Fetches and normalizes free weather provider responses for New England."""

from __future__ import annotations

import json
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone

from .regional_location_catalog import load_default_new_england_locations
from .structured_logging import append_structured_log
from .weather_data_models import NormalizedWeatherRecord, RegionalLocation

MISSING_NUMERIC_VALUE = -9999.0
DEFAULT_REQUEST_HEADERS = {
    "Accept": "application/json",
    "User-Agent": "UmboniWeatherPlatform/0.1 (https://github.com/gedrocht/Umboni)",
}


def load_json_from_endpoint(
    endpoint_url: str,
    request_headers: dict[str, str] | None = None,
) -> dict[str, object]:
    """Loads a JSON payload from a remote endpoint using the Python standard library."""

    merged_request_headers = dict(DEFAULT_REQUEST_HEADERS)
    if request_headers:
        merged_request_headers.update(request_headers)

    request = urllib.request.Request(endpoint_url, headers=merged_request_headers)
    with urllib.request.urlopen(request, timeout=30) as response_stream:
        response_text = response_stream.read().decode("utf-8")
    return json.loads(response_text)


def normalize_timestamp_to_utc(raw_timestamp: str) -> str:
    """Converts a provider timestamp into a UTC timestamp with a trailing `Z`."""

    if raw_timestamp.endswith("Z"):
        return raw_timestamp
    if len(raw_timestamp) == 16:
        return f"{raw_timestamp}:00Z"
    parsed_timestamp = datetime.fromisoformat(raw_timestamp.replace("Z", "+00:00"))
    return parsed_timestamp.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def convert_fahrenheit_to_celsius(temperature_fahrenheit: float) -> float:
    """Converts Fahrenheit to Celsius."""

    return (temperature_fahrenheit - 32.0) * 5.0 / 9.0


def convert_miles_per_hour_to_kilometers_per_hour(speed_miles_per_hour: float) -> float:
    """Converts miles per hour to kilometers per hour."""

    return speed_miles_per_hour * 1.60934


def infer_precipitation_probability_from_weather_code(weather_code: str) -> float:
    """Maps textual weather descriptions to a rough precipitation probability."""

    lowered_weather_code = weather_code.lower()
    if any(keyword in lowered_weather_code for keyword in ("rain", "snow", "storm", "thunder")):
        return 80.0
    if any(keyword in lowered_weather_code for keyword in ("cloud", "overcast")):
        return 35.0
    return 10.0


def convert_seven_timer_wind_scale_to_kilometers_per_hour(beaufort_scale_value: int) -> float:
    """Approximates the center of each Beaufort range in kilometers per hour."""

    beaufort_scale_midpoints = {
        1: 1.0,
        2: 6.0,
        3: 12.0,
        4: 20.0,
        5: 29.0,
        6: 39.0,
        7: 50.0,
        8: 62.0,
    }
    return beaufort_scale_midpoints.get(beaufort_scale_value, 0.0)


def parse_open_meteo_response(
    regional_location: RegionalLocation,
    response_payload: dict[str, object],
    maximum_hours: int,
) -> list[NormalizedWeatherRecord]:
    """Normalizes an Open-Meteo hourly forecast response."""

    hourly_payload = response_payload["hourly"]
    timestamps = hourly_payload["time"][:maximum_hours]
    normalized_records: list[NormalizedWeatherRecord] = []

    for current_hour_index, timestamp_value in enumerate(timestamps, start=1):
        normalized_records.append(
            NormalizedWeatherRecord(
                provider_name="Open-Meteo",
                state_name=regional_location.state_name,
                location_name=regional_location.location_name,
                latitude_degrees=regional_location.latitude_degrees,
                longitude_degrees=regional_location.longitude_degrees,
                altitude_meters=regional_location.altitude_meters,
                forecast_hour_offset=current_hour_index,
                forecast_timestamp_utc=normalize_timestamp_to_utc(str(timestamp_value)),
                air_temperature_celsius=float(hourly_payload["temperature_2m"][current_hour_index - 1]),
                relative_humidity_percentage=float(hourly_payload["relative_humidity_2m"][current_hour_index - 1]),
                wind_speed_kilometers_per_hour=float(hourly_payload["wind_speed_10m"][current_hour_index - 1]),
                precipitation_probability_percentage=float(
                    hourly_payload["precipitation_probability"][current_hour_index - 1]
                ),
                surface_pressure_hectopascals=float(hourly_payload["surface_pressure"][current_hour_index - 1]),
                cloud_cover_percentage=float(hourly_payload["cloud_cover"][current_hour_index - 1]),
            )
        )

    return normalized_records


def parse_national_weather_service_hourly_response(
    regional_location: RegionalLocation,
    response_payload: dict[str, object],
    maximum_hours: int,
) -> list[NormalizedWeatherRecord]:
    """Normalizes a National Weather Service hourly forecast response."""

    normalized_records: list[NormalizedWeatherRecord] = []
    hourly_periods = response_payload["properties"]["periods"][:maximum_hours]

    for current_hour_index, hourly_period in enumerate(hourly_periods, start=1):
        temperature_value = float(hourly_period["temperature"])
        if hourly_period.get("temperatureUnit") == "F":
            temperature_value = convert_fahrenheit_to_celsius(temperature_value)

        raw_wind_speed_text = str(hourly_period["windSpeed"]).split(" ")[0]
        wind_speed_kilometers_per_hour = convert_miles_per_hour_to_kilometers_per_hour(float(raw_wind_speed_text))

        normalized_records.append(
            NormalizedWeatherRecord(
                provider_name="National Weather Service",
                state_name=regional_location.state_name,
                location_name=regional_location.location_name,
                latitude_degrees=regional_location.latitude_degrees,
                longitude_degrees=regional_location.longitude_degrees,
                altitude_meters=regional_location.altitude_meters,
                forecast_hour_offset=current_hour_index,
                forecast_timestamp_utc=normalize_timestamp_to_utc(str(hourly_period["startTime"])),
                air_temperature_celsius=temperature_value,
                relative_humidity_percentage=float(
                    hourly_period.get("relativeHumidity", {}).get("value") or MISSING_NUMERIC_VALUE
                ),
                wind_speed_kilometers_per_hour=wind_speed_kilometers_per_hour,
                precipitation_probability_percentage=float(
                    hourly_period.get("probabilityOfPrecipitation", {}).get("value") or 0.0
                ),
                surface_pressure_hectopascals=MISSING_NUMERIC_VALUE,
                cloud_cover_percentage=infer_precipitation_probability_from_weather_code(
                    str(hourly_period.get("shortForecast", ""))
                ),
            )
        )

    return normalized_records


def parse_met_norway_response(
    regional_location: RegionalLocation,
    response_payload: dict[str, object],
    maximum_hours: int,
) -> list[NormalizedWeatherRecord]:
    """Normalizes a MET Norway location forecast response."""

    normalized_records: list[NormalizedWeatherRecord] = []
    time_series_entries = response_payload["properties"]["timeseries"][:maximum_hours]

    for current_hour_index, time_series_entry in enumerate(time_series_entries, start=1):
        instantaneous_details = time_series_entry["data"]["instant"]["details"]
        one_hour_details = time_series_entry["data"].get("next_1_hours", {}).get("details", {})
        precipitation_amount = float(one_hour_details.get("precipitation_amount", 0.0))

        normalized_records.append(
            NormalizedWeatherRecord(
                provider_name="MET Norway",
                state_name=regional_location.state_name,
                location_name=regional_location.location_name,
                latitude_degrees=regional_location.latitude_degrees,
                longitude_degrees=regional_location.longitude_degrees,
                altitude_meters=regional_location.altitude_meters,
                forecast_hour_offset=current_hour_index,
                forecast_timestamp_utc=normalize_timestamp_to_utc(str(time_series_entry["time"])),
                air_temperature_celsius=float(instantaneous_details["air_temperature"]),
                relative_humidity_percentage=float(instantaneous_details["relative_humidity"]),
                wind_speed_kilometers_per_hour=float(instantaneous_details["wind_speed"]) * 3.6,
                precipitation_probability_percentage=70.0 if precipitation_amount > 0.0 else 10.0,
                surface_pressure_hectopascals=float(
                    instantaneous_details.get("air_pressure_at_sea_level", MISSING_NUMERIC_VALUE)
                ),
                cloud_cover_percentage=float(
                    instantaneous_details.get("cloud_area_fraction", MISSING_NUMERIC_VALUE)
                ),
            )
        )

    return normalized_records


def parse_seven_timer_response(
    regional_location: RegionalLocation,
    response_payload: dict[str, object],
    maximum_hours: int,
) -> list[NormalizedWeatherRecord]:
    """Normalizes a 7Timer response."""

    normalized_records: list[NormalizedWeatherRecord] = []
    initialization_time = datetime.strptime(str(response_payload["init"]), "%Y%m%d%H").replace(
        tzinfo=timezone.utc
    )
    data_series_entries = response_payload["dataseries"][:maximum_hours]

    for current_hour_index, data_series_entry in enumerate(data_series_entries, start=1):
        forecast_timestamp = initialization_time + timedelta(hours=int(data_series_entry["timepoint"]))
        wind_payload = data_series_entry.get("wind10m", {})

        normalized_records.append(
            NormalizedWeatherRecord(
                provider_name="7Timer",
                state_name=regional_location.state_name,
                location_name=regional_location.location_name,
                latitude_degrees=regional_location.latitude_degrees,
                longitude_degrees=regional_location.longitude_degrees,
                altitude_meters=regional_location.altitude_meters,
                forecast_hour_offset=current_hour_index,
                forecast_timestamp_utc=forecast_timestamp.strftime("%Y-%m-%dT%H:%M:%SZ"),
                air_temperature_celsius=float(data_series_entry.get("temp2m", MISSING_NUMERIC_VALUE)),
                relative_humidity_percentage=float(data_series_entry.get("rh2m", MISSING_NUMERIC_VALUE)),
                wind_speed_kilometers_per_hour=convert_seven_timer_wind_scale_to_kilometers_per_hour(
                    int(wind_payload.get("speed", 0))
                ),
                precipitation_probability_percentage=infer_precipitation_probability_from_weather_code(
                    str(data_series_entry.get("weather", ""))
                ),
                surface_pressure_hectopascals=MISSING_NUMERIC_VALUE,
                cloud_cover_percentage=(float(data_series_entry.get("cloudcover", 0)) / 8.0) * 100.0,
            )
        )

    return normalized_records


def fetch_all_normalized_weather_records(
    maximum_hours: int,
    log_file_path: str,
) -> list[NormalizedWeatherRecord]:
    """Fetches every provider for every default New England location."""

    if maximum_hours < 1:
        raise ValueError("maximum_hours must be at least 1.")

    normalized_records: list[NormalizedWeatherRecord] = []
    provider_fetch_functions = [
        ("Open-Meteo", fetch_open_meteo_records_for_location),
        ("National Weather Service", fetch_national_weather_service_records_for_location),
        ("MET Norway", fetch_met_norway_records_for_location),
        ("7Timer", fetch_seven_timer_records_for_location),
    ]

    for regional_location in load_default_new_england_locations():
        append_structured_log(
            log_file_path,
            "INFO",
            "Fetching provider data for one regional location.",
            state_name=regional_location.state_name,
            location_name=regional_location.location_name,
        )

        for provider_name, provider_fetch_function in provider_fetch_functions:
            try:
                normalized_records.extend(provider_fetch_function(regional_location, maximum_hours))
            except Exception as raised_exception:
                append_structured_log(
                    log_file_path,
                    "ERROR",
                    "One provider failed for one regional location, but the run will continue.",
                    provider_name=provider_name,
                    state_name=regional_location.state_name,
                    location_name=regional_location.location_name,
                    exception_type=type(raised_exception).__name__,
                    exception_message=str(raised_exception),
                )

    normalized_records.sort(
        key=lambda normalized_record: (
            normalized_record.state_name,
            normalized_record.location_name,
            normalized_record.forecast_hour_offset,
            normalized_record.provider_name,
        )
    )

    if not normalized_records:
        raise RuntimeError("Every provider failed, so no normalized weather records were produced.")

    return normalized_records


def fetch_open_meteo_records_for_location(
    regional_location: RegionalLocation,
    maximum_hours: int,
) -> list[NormalizedWeatherRecord]:
    """Calls Open-Meteo and normalizes the result."""

    query_string = urllib.parse.urlencode(
        {
            "latitude": regional_location.latitude_degrees,
            "longitude": regional_location.longitude_degrees,
            "timezone": "UTC",
            "forecast_days": 2,
            "hourly": (
                "temperature_2m,relative_humidity_2m,wind_speed_10m,"
                "precipitation_probability,surface_pressure,cloud_cover"
            ),
        }
    )
    endpoint_url = f"https://api.open-meteo.com/v1/forecast?{query_string}"
    response_payload = load_json_from_endpoint(endpoint_url)
    return parse_open_meteo_response(regional_location, response_payload, maximum_hours)


def fetch_national_weather_service_records_for_location(
    regional_location: RegionalLocation,
    maximum_hours: int,
) -> list[NormalizedWeatherRecord]:
    """Calls the United States National Weather Service and normalizes the result."""

    points_endpoint_url = (
        f"https://api.weather.gov/points/{regional_location.latitude_degrees},{regional_location.longitude_degrees}"
    )
    points_payload = load_json_from_endpoint(points_endpoint_url)
    forecast_endpoint_url = str(points_payload["properties"]["forecastHourly"])
    forecast_payload = load_json_from_endpoint(forecast_endpoint_url)
    return parse_national_weather_service_hourly_response(regional_location, forecast_payload, maximum_hours)


def fetch_met_norway_records_for_location(
    regional_location: RegionalLocation,
    maximum_hours: int,
) -> list[NormalizedWeatherRecord]:
    """Calls MET Norway and normalizes the result."""

    endpoint_url = (
        "https://api.met.no/weatherapi/locationforecast/2.0/compact"
        f"?lat={regional_location.latitude_degrees}&lon={regional_location.longitude_degrees}"
        f"&altitude={regional_location.altitude_meters}"
    )
    response_payload = load_json_from_endpoint(endpoint_url)
    return parse_met_norway_response(regional_location, response_payload, maximum_hours)


def fetch_seven_timer_records_for_location(
    regional_location: RegionalLocation,
    maximum_hours: int,
) -> list[NormalizedWeatherRecord]:
    """Calls 7Timer and normalizes the result."""

    endpoint_url = (
        "https://www.7timer.info/bin/api.pl"
        f"?lon={regional_location.longitude_degrees}&lat={regional_location.latitude_degrees}"
        "&product=civil&output=json"
    )
    response_payload = load_json_from_endpoint(endpoint_url)
    return parse_seven_timer_response(regional_location, response_payload, maximum_hours)
