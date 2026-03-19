# Contributing

Thank you for considering a contribution to Umboni.

## Development principles

- Prefer clarity over cleverness.
- Use fully self-descriptive names instead of abbreviations.
- Write comments and documentation as if the reader is intelligent but brand new to the codebase.
- Add or update tests for every behavior change.
- Keep logs structured and easy to inspect.

## Local quality gates

### Repository-wide checks

```bash
npm install
npm run prepare
npm run validate:repository
```

### Python fetcher checks

```bash
cd python
python -m unittest discover -s tests -t .
```

### Fortran checks

```bash
cmake --preset default
cmake --build --preset default
ctest --preset default --output-on-failure
```

### Angular checks

```bash
cd frontend
npm install
npm run validate
```

## Pull request expectations

- Explain the problem, not just the code change.
- Link to the relevant tutorial or wiki page if beginner-facing behavior changed.
- Include screenshots for Angular UI changes.
- Call out changes to provider logic because external APIs evolve over time.
- Update both formal docs and wiki content when architecture or workflow changes.
