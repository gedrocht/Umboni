# Umboni

A hardened TypeScript repository baseline with strict local tooling and GitHub enforcement for quality, testing, coverage, security, and review hygiene.

## Included guardrails

- TypeScript strict mode with `noUncheckedIndexedAccess` and `exactOptionalPropertyTypes`
- ESLint with type-aware rules and zero-warning tolerance
- Prettier formatting checks
- Vitest unit tests with 100% global coverage thresholds
- `npm audit` for dependency vulnerability checks
- Husky + lint-staged pre-commit automation
- GitHub Actions for CI, CodeQL, dependency review, and secret scanning
- CODEOWNERS, PR template, issue forms, and security policy

## Quick start

```bash
npm install
npm run prepare
npm run validate
```

If you want fully reproducible installs in CI, generate and commit `package-lock.json` after the first `npm install`.

## Branch protection recommendations

After pushing to GitHub, enable branch protection on your default branch and require these status checks:

- `quality`
- `test`
- `coverage`
- `dependency-review`
- `CodeQL`
- `secret-scan`

Also require at least one approving review and dismiss stale approvals on new commits.
