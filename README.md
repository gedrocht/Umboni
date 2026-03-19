# Umboni New England Weather Intelligence Platform

Umboni is a beginner-friendly weather platform for New England.

The repository has three main runtime pieces:

1. A Python fetcher that downloads free weather data from several providers.
2. A Fortran simulator that combines those provider records into a 24-hour forecast.
3. An Angular dashboard that visualizes the forecast in a browser.

The project also contains a documentation site, a self-hosted wiki, and an
optional observability stack.

## Start here

If you are brand new to the project, use these commands in order:

```bash
python scripts/umboni.py doctor
python scripts/umboni.py bootstrap
python scripts/umboni.py pipeline
python scripts/umboni.py run-frontend
```

What each command does:

- `doctor` checks whether the required tools are installed.
- `bootstrap` installs the Python and Node dependencies used by the repository.
- `pipeline` fetches weather data, builds the Fortran simulator, generates a
  forecast JSON file, and copies that forecast into the Angular app.
- `run-frontend` starts the Angular dashboard at
  `http://127.0.0.1:4200`.

## Prerequisites

Read [docs/prerequisites.md](docs/prerequisites.md) for the beginner-friendly,
platform-specific setup guide.

The short version is:

- Python 3.10 or newer
- Node.js 22 or newer
- CMake 3.27 or newer
- Ninja
- GNU Fortran (`gfortran`)
- Doxygen
- Docker only if you want the optional wiki or observability stack

## One obvious command per common task

Use the repository root for every command below.

| Goal | Command |
| --- | --- |
| Check prerequisites | `python scripts/umboni.py doctor` |
| Install project dependencies | `python scripts/umboni.py bootstrap` |
| Fetch only the provider CSV | `python scripts/umboni.py fetch` |
| Build the Fortran simulator | `python scripts/umboni.py build-fortran` |
| Run the full fetch -> simulate -> sync pipeline | `python scripts/umboni.py pipeline` |
| Start the Angular dashboard | `python scripts/umboni.py run-frontend` |
| Run every major test suite | `python scripts/umboni.py test all` |
| Build the documentation site | `python scripts/umboni.py build-docs` |
| Serve the documentation site locally | `python scripts/umboni.py serve-docs` |

If you already ran `bootstrap`, you can also use the matching npm aliases such
as `npm run doctor`, `npm run bootstrap`, `npm run run:pipeline`, and
`npm run test:all`.

## What gets generated

After `python scripts/umboni.py pipeline` finishes successfully, the most
important files are:

- `artifacts/generated/provider-observations.csv`
- `artifacts/generated/new-england-forecast.json`
- `frontend/public/data/new-england-forecast-sample.json`
- `artifacts/logs/python-fetcher.log.jsonl`
- `artifacts/logs/fortran-simulator.log.jsonl`

## How to test everything

Run the full repository test flow with:

```bash
python scripts/umboni.py test all
```

That command runs:

- repository markdown and audit checks
- Python unit tests
- Fortran native tests
- Angular linting
- Angular unit tests
- Angular coverage tests
- Angular build
- Playwright end-to-end smoke tests
- documentation build checks

If you are on a constrained machine and want to skip the browser-based tests,
use this lighter command:

```bash
python scripts/umboni.py test all --skip-end-to-end-tests
```

## Documentation map

- Beginner home: [docs/index.md](docs/index.md)
- Prerequisites: [docs/prerequisites.md](docs/prerequisites.md)
- First run guide: [docs/getting-started.md](docs/getting-started.md)
- Build, run, and test guide: [docs/build-run-test.md](docs/build-run-test.md)
- Troubleshooting: [docs/troubleshooting.md](docs/troubleshooting.md)
- Architecture overview: [docs/architecture-overview.md](docs/architecture-overview.md)
- Testing strategy: [docs/testing-strategy.md](docs/testing-strategy.md)
- External libraries: [docs/external-libraries.md](docs/external-libraries.md)
- Wiki guide: see the `wiki/README.md` file in the repository root

## Repository map

- `fortran/source` contains the simulation engine.
- `python/new_england_weather_data_fetcher` contains the provider clients,
  normalization logic, and the beginner task runner.
- `frontend` contains the Angular application.
- `docs` contains the GitHub Pages documentation.
- `wiki` contains the Wiki.js deployment and starter pages.
- `observability` contains Grafana, Loki, and Promtail configuration.
- `samples` contains deterministic fixtures and sample data.
