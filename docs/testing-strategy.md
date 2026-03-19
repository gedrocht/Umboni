# Testing Strategy

Umboni treats testing as a first-class feature rather than a final cleanup step.

## Repository hygiene tests

Repository-level tests and checks catch non-code regressions:

- Markdown formatting
- Markdown linting
- YAML formatting
- Commit message conventions

## Python tests

Python tests use `unittest` so contributors do not need an additional framework just to understand the fetcher.

They cover:

- Unit conversion helpers
- Provider response parsing
- Orchestration and sorting
- CSV output
- Command-line behavior
- Structured logging

## Fortran tests

Fortran tests are compiled executables run through `ctest`.

They cover:

- CSV parsing
- Weighted forecast aggregation
- Provider coverage counts

## Angular tests

Angular tests are split into several layers:

- Service tests for data loading
- Component rendering tests
- Visualization component tests
- Playwright end-to-end smoke coverage

## GitHub checks

GitHub Actions enforce:

- Build success
- Unit tests
- Code coverage
- Documentation builds
- Dependency review
- Secret scanning
- CodeQL analysis
- Scorecards analysis
