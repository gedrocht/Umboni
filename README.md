# Umboni New England Weather Intelligence Platform

[![Repository Hygiene](https://github.com/gedrocht/Umboni/actions/workflows/repository-hygiene.yml/badge.svg?branch=main)](https://github.com/gedrocht/Umboni/actions/workflows/repository-hygiene.yml)
[![Backend Quality](https://github.com/gedrocht/Umboni/actions/workflows/backend-quality.yml/badge.svg?branch=main)](https://github.com/gedrocht/Umboni/actions/workflows/backend-quality.yml)
[![Frontend Quality](https://github.com/gedrocht/Umboni/actions/workflows/frontend-quality.yml/badge.svg?branch=main)](https://github.com/gedrocht/Umboni/actions/workflows/frontend-quality.yml)
[![Documentation Build](https://github.com/gedrocht/Umboni/actions/workflows/documentation.yml/badge.svg?branch=main)](https://github.com/gedrocht/Umboni/actions/workflows/documentation.yml)
[![CodeQL](https://github.com/gedrocht/Umboni/actions/workflows/codeql.yml/badge.svg?branch=main)](https://github.com/gedrocht/Umboni/actions/workflows/codeql.yml)

Umboni is a deliberately over-documented, beginner-friendly weather intelligence monorepo. It combines a Fortran simulation engine, a Python free-weather-data fetcher, and an Angular visualization application to collect multi-source forecast data for New England and generate a 24-hour regional ensemble forecast.

- Live documentation: [gedrocht.github.io/Umboni](https://gedrocht.github.io/Umboni/)
- Beginner walkthrough: [docs/getting-started.md](docs/getting-started.md)
- Beginner command runner: [`python scripts/umboni.py --help`](scripts/umboni.py)

## Start here first

If you are new to the repository, use the beginner workflow instead of memorizing individual build commands:

```bash
python scripts/umboni.py doctor
python scripts/umboni.py bootstrap
python scripts/umboni.py pipeline
python scripts/umboni.py run-frontend
python scripts/umboni.py test all --skip-end-to-end-tests
```

That sequence checks prerequisites, installs dependencies, generates forecast data, launches the Angular dashboard, and runs the repo-wide validation path.

## What success looks like

- `doctor` confirms the required local tools are installed.
- `bootstrap` installs the Python and Node dependencies used by the repository.
- `pipeline` writes normalized provider data and a generated forecast into `artifacts/generated`.
- `run-frontend` starts the Angular dashboard so you can inspect the forecast visually.
- `test all` exercises the repository, Python, Fortran, frontend, and documentation quality gates.

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

### One-command beginner flow

```bash
python scripts/umboni.py doctor
python scripts/umboni.py bootstrap
python scripts/umboni.py pipeline
python scripts/umboni.py run-frontend
```

### If you prefer the lower-level commands

#### Repository hygiene tooling

```bash
npm ci
npm run prepare
npm run validate:repository
```

#### Python fetcher

```bash
python scripts/run_weather_fetcher.py --output-csv artifacts/generated/provider-observations.csv
```

#### Fortran simulator

```bash
cmake --preset default
cmake --build --preset default
ctest --preset default --output-on-failure
python scripts/synchronize_generated_forecast_to_frontend.py
```

#### Angular dashboard

```bash
cd frontend
npm ci
npm run validate
```

## Documentation experience

- Beginner tutorials: [`docs/getting-started.md`](docs/getting-started.md)
- Build, run, and test guide: [`docs/build-run-test.md`](docs/build-run-test.md)
- Prerequisites guide: [`docs/prerequisites.md`](docs/prerequisites.md)
- Architecture overview: [`docs/architecture-overview.md`](docs/architecture-overview.md)
- Testing strategy: [`docs/testing-strategy.md`](docs/testing-strategy.md)
- Troubleshooting guide: [`docs/troubleshooting.md`](docs/troubleshooting.md)
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
