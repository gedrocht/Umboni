# Adding a Provider

This tutorial explains the safest way to add a new free weather API source.

## Step 1: Add a parser

Create a parser in [`python/new_england_weather_data_fetcher/provider_clients.py`](https://github.com/gedrocht/Umboni/blob/main/python/new_england_weather_data_fetcher/provider_clients.py) that converts the provider payload into `NormalizedWeatherRecord` objects.

## Step 2: Add tests before wiring it into production code

- Create a fixture under [`samples/provider-fixtures`](https://github.com/gedrocht/Umboni/tree/main/samples/provider-fixtures)
- Add parser tests under [`python/tests/test_provider_clients.py`](https://github.com/gedrocht/Umboni/blob/main/python/tests/test_provider_clients.py)

## Step 3: Add orchestration

Add a `fetch_..._records_for_location` function and call it inside `fetch_all_normalized_weather_records`.

## Step 4: Decide on provider weighting

If the provider should influence the Fortran consensus, update [`fortran/source/provider_weight_catalog.f90`](https://github.com/gedrocht/Umboni/blob/main/fortran/source/provider_weight_catalog.f90).

## Step 5: Update documentation

Update:

- The README
- This tutorial
- The external libraries page if a new dependency is introduced
- The Wiki.js seed pages if the new provider changes the beginner explanation
