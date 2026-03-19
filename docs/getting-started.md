# Getting Started

This guide is written for someone who has never run Umboni before.

If you follow the steps in order, you will:

1. check your prerequisites
2. install the project dependencies
3. generate forecast data
4. start the Angular dashboard
5. confirm that the main tests work

## Step 1: Open a terminal in the repository root

Every command in this guide assumes your current directory is the repository
root.

You should be able to see files such as:

- `README.md`
- `package.json`
- `pyproject.toml`
- `CMakeLists.txt`

## Step 2: Check your prerequisites

Run:

```bash
python scripts/umboni.py doctor
```

What this command does:

- checks whether Python is available
- checks whether Node.js and npm are available
- checks whether CMake, CTest, Ninja, and GNU Fortran are available
- checks whether Doxygen is available for documentation builds
- tells you exactly what is missing and how to install it

What good looks like:

- every required tool is shown as `[OK]`
- the command ends by telling you to run `python scripts/umboni.py bootstrap`

If a tool is missing, go to [Prerequisites](prerequisites.md), install it, and
run `doctor` again.

## Step 3: Install the repository dependencies

Run:

```bash
python scripts/umboni.py bootstrap
```

What this command does:

- creates the common artifact and log directories
- installs the Python package plus its development and documentation tools
- installs the root repository Node dependencies
- installs the frontend Node dependencies

What good looks like:

- the command ends by telling you that bootstrap finished successfully
- you can now run the fetch, pipeline, test, and documentation commands

## Step 4: Generate a forecast

Run:

```bash
python scripts/umboni.py pipeline
```

What this command does:

- fetches provider data from the New England catalog
- writes `artifacts/generated/provider-observations.csv`
- configures and builds the Fortran simulator
- runs the simulator against the fetched CSV
- writes `artifacts/generated/new-england-forecast.json`
- copies the latest forecast into
  `frontend/public/data/new-england-forecast-sample.json`

What good looks like:

- the command ends with `Pipeline finished successfully.`
- the Angular app now has fresh sample forecast data to display

## Step 5: Start the dashboard

Run:

```bash
python scripts/umboni.py run-frontend
```

Then open:

```text
http://127.0.0.1:4200
```

What good looks like:

- the Angular development server starts without errors
- the dashboard shows a regional forecast instead of an empty page

## Step 6: Run the tests

If you want the full suite, run:

```bash
python scripts/umboni.py test all
```

That full test flow includes:

- repository validation
- Python unit tests
- Fortran tests
- frontend linting
- frontend unit tests
- frontend coverage tests
- frontend build
- Playwright browser smoke tests
- documentation build checks

If you want a lighter first pass that skips the browser tests, run:

```bash
python scripts/umboni.py test all --skip-end-to-end-tests
```

## Step 7: Build the documentation

Run:

```bash
python scripts/umboni.py build-docs
```

This creates the static documentation site in the `site/` directory.

If you want to browse the docs locally instead, run:

```bash
python scripts/umboni.py serve-docs
```

Then open:

```text
http://127.0.0.1:8000
```

## Common follow-up commands

Use these if you want one smaller task instead of the full pipeline:

```bash
python scripts/umboni.py fetch
python scripts/umboni.py build-fortran
python scripts/umboni.py simulate
```

The `fetch` command only creates the normalized provider CSV.

The `build-fortran` command only configures and compiles the simulator.

The `simulate` command expects a CSV that already exists and turns it into the
forecast JSON used by the Angular app.

## If something goes wrong

Go to [Troubleshooting](troubleshooting.md).
