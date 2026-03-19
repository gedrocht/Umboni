# Build, Run, and Test

This page gives you one obvious command for each common task.

## The easiest full flow

Use these commands in order:

```bash
python scripts/umboni.py doctor
python scripts/umboni.py bootstrap
python scripts/umboni.py pipeline
python scripts/umboni.py run-frontend
```

If you only remember one thing from this page, remember that sequence.

## Build everything needed for the forecast pipeline

Run:

```bash
python scripts/umboni.py pipeline
```

That single command does all of this:

- fetches provider data
- builds the Fortran simulator
- generates the forecast JSON
- synchronizes the forecast into the Angular app

## Run the Angular dashboard

Run:

```bash
python scripts/umboni.py run-frontend
```

Then open:

```text
http://127.0.0.1:4200
```

## Run only one part of the system

Use these if you want a smaller task:

```bash
python scripts/umboni.py fetch
python scripts/umboni.py build-fortran
python scripts/umboni.py simulate
```

Use `fetch` when you only want the normalized CSV.

Use `build-fortran` when you only want to compile the simulator.

Use `simulate` when you already have the CSV and only want the forecast JSON.

## Test everything

Run:

```bash
python scripts/umboni.py test all
```

That command runs:

- repository markdown and audit checks
- Python tests
- Fortran tests
- frontend linting
- frontend unit tests
- frontend coverage tests
- frontend build
- Playwright end-to-end smoke tests
- documentation build checks

If you want the same command without the browser tests, run:

```bash
python scripts/umboni.py test all --skip-end-to-end-tests
```

## Build or serve the documentation

Build the static docs:

```bash
python scripts/umboni.py build-docs
```

Serve the docs locally:

```bash
python scripts/umboni.py serve-docs
```

Then open:

```text
http://127.0.0.1:8000
```

## npm aliases

If you prefer npm commands and already ran `bootstrap`, these root aliases exist:

```bash
npm run doctor
npm run bootstrap
npm run run:pipeline
npm run run:frontend
npm run test:all
npm run build:docs
```

Those npm aliases call the same beginner task runner underneath.
