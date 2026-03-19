# Umboni New England Weather Intelligence Platform

Umboni is a deliberately over-documented, beginner-friendly weather intelligence monorepo. It combines a Fortran simulation engine, a Python free-weather-data fetcher, and an Angular visualization application to collect multi-source forecast data for New England and generate a 24-hour regional ensemble forecast.

## What this repository contains

- A **Fortran 2018** application that reads normalized provider data, simulates the next 24 hours, and writes a richly structured JSON forecast artifact.
- A **Python 3.12+** weather data fetcher that talks to multiple free providers, normalizes their responses, and writes deterministic comma-separated-value input for the Fortran engine.
- An **Angular 21** web application that visualizes hourly regional conditions, provider coverage, and forecast confidence.
- A **Doxygen + MkDocs Material** documentation site for formal API reference, tutorials, and beginner-oriented walkthroughs.
- A separate **Wiki.js** knowledge base that can be self-hosted for collaborative, beginner-first explainer content.
- A local **Grafana + Loki + Promtail** observability stack for browsing structured logs in familiar tools.

## Free forecast providers currently wrapped

- Open-Meteo
- United States National Weather Service (`api.weather.gov`)
- MET Norway (`api.met.no`)
- 7Timer!

## New England coverage model

The default regional catalog spans one representative location per state:

- Boston, Massachusetts
- Portland, Maine
- Concord, New Hampshire
- Burlington, Vermont
- Providence, Rhode Island
- Hartford, Connecticut

The fetch layer is extensible, so additional cities, stations, or providers can be added without changing the Angular UI contract.

## Repository map

- [`fortran/source`](fortran/source) contains the simulation engine.
- [`python/new_england_weather_data_fetcher`](python/new_england_weather_data_fetcher) contains the provider clients and normalization logic.
- [`frontend`](frontend) contains the Angular application.
- [`docs`](docs) contains the GitHub Pages documentation content.
- [`wiki`](wiki) contains the Wiki.js deployment and starter pages.
- [`observability`](observability) contains Grafana, Loki, and Promtail configuration.
- [`samples`](samples) contains deterministic test and demo fixtures.

## Quick start

### Repository hygiene tooling

```bash
npm install
npm run prepare
npm run validate:repository
```

### Python fetcher

```bash
python scripts/run_weather_fetcher.py --output-csv artifacts/generated/provider-observations.csv
```

### Fortran simulator

```bash
cmake --preset default
cmake --build --preset default
ctest --preset default --output-on-failure
python scripts/synchronize_generated_forecast_to_frontend.py
```

### Angular dashboard

```bash
cd frontend
npm install
npm run validate
```

## Documentation experience

- Beginner tutorials: [`docs/getting-started.md`](docs/getting-started.md)
- Architecture overview: [`docs/architecture-overview.md`](docs/architecture-overview.md)
- Testing strategy: [`docs/testing-strategy.md`](docs/testing-strategy.md)
- External library guide: [`docs/external-libraries.md`](docs/external-libraries.md)
- Wiki deployment guide: [`wiki/README.md`](wiki/README.md)

## Branch protection recommendations

After the repository is pushed, require these checks on the default branch:

- `repository-hygiene`
- `python-fetcher`
- `fortran-engine`
- `frontend-quality`
- `documentation-build`
- `dependency-review`
- `Analyze (javascript-typescript)`
- `Analyze (python)`
- `secret-scan`
- `scorecards`

Also require at least one approving review, dismiss stale approvals after new commits, require CODEOWNERS review, and prevent force pushes.
