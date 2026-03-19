# Data Flow

This page explains how information moves through the system.

## Step 1: External providers

The fetcher reaches out to multiple free sources:

- Open-Meteo
- National Weather Service
- MET Norway
- 7Timer

Each provider uses its own response shape, units, time conventions, and field names.

## Step 2: Normalization

The Python fetcher converts all providers into one shared record structure with these fields:

- Provider name
- State name
- Location name
- Latitude and longitude
- Forecast hour offset
- Forecast timestamp
- Temperature
- Humidity
- Wind speed
- Precipitation probability
- Surface pressure
- Cloud cover

## Step 3: Numerical combination

The Fortran engine reads all normalized rows and groups them by location and hour. It then:

1. Applies provider weights.
2. Ignores missing values using a sentinel number.
3. Computes weighted averages.
4. Applies gentle smoothing to avoid unrealistic jumps.
5. Calculates a basic confidence score from provider coverage.

## Step 4: Visualization

The Angular application reads the generated JSON and turns it into:

- A regional summary panel
- Per-location cards
- A temperature sparkline
- A beginner-friendly hourly table

