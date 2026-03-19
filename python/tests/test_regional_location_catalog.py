"""Tests for the default location catalog."""

from __future__ import annotations

from unittest import TestCase

from new_england_weather_data_fetcher.regional_location_catalog import load_default_new_england_locations


class RegionalLocationCatalogTestCase(TestCase):
    """Verifies that one representative location exists for each New England state."""

    def test_load_default_new_england_locations_returns_six_locations(self) -> None:
        regional_locations = load_default_new_england_locations()

        self.assertEqual(6, len(regional_locations))
        self.assertEqual("Massachusetts", regional_locations[0].state_name)
        self.assertEqual("Hartford", regional_locations[-1].location_name)
