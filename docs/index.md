# Umboni Weather Intelligence Platform

Umboni is a teaching-oriented weather platform for New England. The repository is intentionally verbose in its code comments, tutorials, and architecture notes so a beginner can learn how a multi-language system fits together.

## The big picture

The platform has three major runtime layers:

1. A Python fetcher gathers forecast data from multiple free providers.
2. A Fortran engine combines those sources into a 24-hour ensemble forecast.
3. An Angular application visualizes the result for people who prefer charts, cards, and tables.

## Why this project is useful for beginners

- It shows how a legacy-friendly systems language such as Fortran can still be productive in a modern stack.
- It demonstrates how to normalize several external APIs into one internal contract.
- It provides a real example of documentation, testing, observability, and GitHub automation living together in one repository.

## Start here

- Read [Getting Started](getting-started.md) if you want a gentle first run.
- Read [Architecture](architecture-overview.md) if you want the system-level overview first.
- Read [Beginner Walkthrough](tutorials/beginner-walkthrough.md) if you want a guided narrative explanation.

