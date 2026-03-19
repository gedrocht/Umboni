# Beginner Walkthrough

This tutorial assumes you are new to at least one of the following:

- Weather APIs
- Fortran
- Angular
- Build automation

## First mental model

Imagine the platform as a relay race:

1. Python gathers many opinions about the weather.
2. Fortran combines those opinions into one forecast.
3. Angular explains that forecast visually.

That is the whole system.

## Why not put everything in one language

You absolutely could. We do not here, because this repository is also a teaching resource. By splitting responsibilities, the project shows where each tool shines.

## Read the data from the outside in

If the codebase feels overwhelming, follow this order:

1. Read the sample JSON forecast in [`frontend/public/data/new-england-forecast-sample.json`](https://github.com/gedrocht/Umboni/blob/main/frontend/public/data/new-england-forecast-sample.json)
2. Read the Fortran JSON writer that produces that shape.
3. Read the Python CSV writer that feeds the Fortran engine.
4. Read the provider parsers one at a time.

## A concrete beginner exercise

Try changing one Open-Meteo fixture value in [`samples/provider-fixtures/open-meteo-response.json`](https://github.com/gedrocht/Umboni/blob/main/samples/provider-fixtures/open-meteo-response.json), then run the relevant Python tests and see how the expected data changes.
