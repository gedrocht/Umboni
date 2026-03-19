# Architecture Overview

Umboni uses a pipeline architecture so that each language does the job it is best suited for.

## Python fetch layer

The Python layer exists because HTTP requests and JSON normalization are much easier in Python than in raw Fortran.

Responsibilities:

- Call multiple free weather APIs.
- Convert different provider payloads into one shared schema.
- Write a deterministic CSV file for the Fortran engine.
- Emit structured JSON-line logs.

Key files:

- [`python/new_england_weather_data_fetcher/provider_clients.py`](https://github.com/gedrocht/Umboni/blob/main/python/new_england_weather_data_fetcher/provider_clients.py)
- [`python/new_england_weather_data_fetcher/command_line_interface.py`](https://github.com/gedrocht/Umboni/blob/main/python/new_england_weather_data_fetcher/command_line_interface.py)

## Fortran simulation engine

The Fortran layer exists to demonstrate a strongly structured numerical engine in a language still used in scientific computing.

Responsibilities:

- Read normalized CSV rows.
- Apply provider weights.
- Smooth abrupt hour-to-hour jumps.
- Produce a single JSON forecast artifact for the frontend.

Key files:

- [`fortran/source/normalized_weather_csv_reader.f90`](https://github.com/gedrocht/Umboni/blob/main/fortran/source/normalized_weather_csv_reader.f90)
- [`fortran/source/forecast_consensus_engine.f90`](https://github.com/gedrocht/Umboni/blob/main/fortran/source/forecast_consensus_engine.f90)
- [`fortran/source/json_forecast_writer.f90`](https://github.com/gedrocht/Umboni/blob/main/fortran/source/json_forecast_writer.f90)

## Angular visualization layer

The Angular layer exists because weather data is easier to understand when it is visual.

Responsibilities:

- Fetch the latest forecast document.
- Present summary cards for beginners.
- Render per-location mini visualizations and hourly tables.
- Keep the UI type-safe and testable.

Key files:

- [`frontend/source/app/services/forecast-data.service.ts`](https://github.com/gedrocht/Umboni/blob/main/frontend/source/app/services/forecast-data.service.ts)
- [`frontend/source/app/components/regional-forecast-dashboard.component.ts`](https://github.com/gedrocht/Umboni/blob/main/frontend/source/app/components/regional-forecast-dashboard.component.ts)
- [`frontend/source/app/components/temperature-trend.component.ts`](https://github.com/gedrocht/Umboni/blob/main/frontend/source/app/components/temperature-trend.component.ts)
