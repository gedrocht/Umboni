# Troubleshooting

This page covers the most common beginner problems.

## `python scripts/umboni.py doctor` says a tool is missing

That means the tool is not available on your shell `PATH`.

Do this:

1. install the missing tool from [Prerequisites](prerequisites.md)
2. close the terminal
3. open a new terminal
4. run `python scripts/umboni.py doctor` again

## `gfortran` is missing on Windows

The usual cause is that MSYS2 is installed but `C:\msys64\ucrt64\bin` is not on
your Windows `PATH`.

Add that folder to `PATH`, then open a new terminal and rerun `doctor`.

## `npm ci` fails

This usually means one of these things happened:

- Node.js is not installed correctly
- the frontend or root lockfile is missing
- you are running the command in the wrong folder

Use the beginner commands from the repository root instead of guessing:

```bash
python scripts/umboni.py bootstrap
python scripts/umboni.py test all --skip-end-to-end-tests
```

## The Angular app starts but shows stale data

Run:

```bash
python scripts/umboni.py pipeline
```

That regenerates the CSV, forecast JSON, and frontend sample data file.

## Playwright end-to-end tests fail because Chromium is missing

The full frontend test path installs Chromium automatically.

If you want a lighter path that skips browser tests, run:

```bash
python scripts/umboni.py test all --skip-end-to-end-tests
```

## Documentation build fails

The most common cause is that Doxygen is missing.

Run:

```bash
python scripts/umboni.py doctor
```

If Doxygen is missing, install it from the link shown in the prerequisite
report.

## You want to know whether the project is fundamentally healthy

Run this quick sequence:

```bash
python scripts/umboni.py doctor
python scripts/umboni.py bootstrap
python scripts/umboni.py pipeline
python scripts/umboni.py test all --skip-end-to-end-tests
```

If those commands pass, the project is in a good local state.
