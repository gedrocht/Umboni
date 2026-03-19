# Umboni Weather Intelligence Platform

Umboni is a teaching-oriented weather platform for New England.

The repository combines:

1. a Python fetcher for free weather APIs
2. a Fortran simulator for the 24-hour ensemble forecast
3. an Angular dashboard for the final visualization

## The shortest path for a beginner

If you do not know where to start, run these commands in order:

```bash
python scripts/umboni.py doctor
python scripts/umboni.py bootstrap
python scripts/umboni.py pipeline
python scripts/umboni.py run-frontend
```

That is the recommended first-run path.

## Read these pages in this order

1. [Prerequisites](prerequisites.md)
2. [Getting Started](getting-started.md)
3. [Build, Run, and Test](build-run-test.md)
4. [Troubleshooting](troubleshooting.md)

After that, move into the deeper reference material:

- [Architecture](architecture-overview.md)
- [Data Flow](data-flow.md)
- [Testing Strategy](testing-strategy.md)
- [Logging and Observability](logging-and-observability.md)
- [External Libraries](external-libraries.md)
- [Beginner Walkthrough](tutorials/beginner-walkthrough.md)

## What success looks like

You know the repository is working when all of these are true:

- `python scripts/umboni.py doctor` reports all required tools as present
- `python scripts/umboni.py pipeline` creates the forecast artifacts
- `python scripts/umboni.py run-frontend` serves the dashboard locally
- `python scripts/umboni.py test all --skip-end-to-end-tests` completes without
  errors
