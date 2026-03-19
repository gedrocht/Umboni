# Getting Started

This page walks through the platform in the order most beginners find easiest to understand.

## 1. Understand the folder layout

- `python/` contains the free weather API fetcher.
- `fortran/` contains the simulation and forecast engine.
- `frontend/` contains the Angular visualization app.
- `docs/` contains the GitHub Pages documentation site.
- `wiki/` contains the Wiki.js deployment for a collaborative beginner guide.
- `observability/` contains the Grafana, Loki, and Promtail stack.

## 2. Run the repository-level checks

```bash
npm install
npm run prepare
npm run validate:repository
```

These commands validate markdown, formatting, and repository hygiene.

## 3. Run the Python fetcher

From the repository root:

```bash
python scripts/run_weather_fetcher.py --output-csv artifacts/generated/provider-observations.csv
```

What happens:

- The fetcher visits each default New England location.
- It requests data from Open-Meteo, the National Weather Service, MET Norway, and 7Timer.
- It writes one normalized CSV file that the Fortran engine can read without caring which provider produced the data.

## 4. Build the Fortran engine

```bash
cmake --preset default
cmake --build --preset default
ctest --preset default --output-on-failure
python scripts/synchronize_generated_forecast_to_frontend.py
```

What happens:

- CMake configures a strict Fortran build.
- The engine compiles with warnings treated as errors when GNU Fortran is used.
- Native executable tests verify CSV parsing and weighted consensus logic.
- The synchronization script copies the latest generated forecast into the Angular public data directory.

## 5. Run the Angular dashboard

```bash
cd frontend
npm install
npm run validate
```

The Angular application reads a forecast JSON document from `frontend/public/data/new-england-forecast-sample.json`.

## 6. Browse logs visually

If you want a friendlier log experience:

```bash
docker compose -f observability/docker-compose.yml up -d
```

Grafana will let you inspect structured JSON logs through a familiar interface.
