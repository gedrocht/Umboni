# Wiki.js Knowledge Base

This directory contains the self-hosted wiki layer for Umboni.

## Why a separate wiki exists

The formal docs in `docs/` are optimized for reference quality and GitHub Pages publishing.

The wiki exists for a different reason:

- slower, more narrative explanations
- collaborative editing
- onboarding notes
- internal teaching material

## Start the wiki locally

```bash
docker compose -f wiki/docker-compose.yml up -d
```

## Seed content

Starter pages live in [`wiki/seed`](seed). They are written so a complete beginner can read the wiki first and only then move into the source code and formal docs.
