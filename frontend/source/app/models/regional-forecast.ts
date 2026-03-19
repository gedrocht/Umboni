/**
 * Describes one hourly forecast that the Angular dashboard can visualize.
 */
export type HourlyForecast = {
  readonly forecastHourOffset: number;
  readonly forecastTimestampUtc: string;
  readonly ensembleAirTemperatureCelsius: number;
  readonly ensembleRelativeHumidityPercentage: number;
  readonly ensembleWindSpeedKilometersPerHour: number;
  readonly ensemblePrecipitationProbabilityPercentage: number;
  readonly ensembleSurfacePressureHectopascals: number;
  readonly ensembleCloudCoverPercentage: number;
  readonly providerCoverageCount: number;
  readonly confidencePercentage: number;
};

/**
 * Summarizes the temperature range for one location over the next day.
 */
export type DailySummary = {
  readonly minimumTemperatureCelsius: number;
  readonly maximumTemperatureCelsius: number;
};

/**
 * Represents the full set of hourly forecasts for one New England location.
 */
export type LocationForecast = {
  readonly stateName: string;
  readonly locationName: string;
  readonly latitudeDegrees: number;
  readonly longitudeDegrees: number;
  readonly dailySummary: DailySummary;
  readonly hourlyForecasts: readonly HourlyForecast[];
};

/**
 * Represents the exact JSON document shape written by the Fortran engine.
 */
export type RegionalForecastDocument = {
  readonly regionName: string;
  readonly locationCount: number;
  readonly locations: readonly LocationForecast[];
};

