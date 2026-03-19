import { CommonModule } from '@angular/common';
import { ChangeDetectionStrategy, Component, computed, inject } from '@angular/core';
import { toSignal } from '@angular/core/rxjs-interop';

import type { HourlyForecast, LocationForecast } from '../models/regional-forecast';
import { ForecastDataService } from '../services/forecast-data.service';
import { TemperatureTrendComponent } from './temperature-trend.component';

/**
 * Presents a beginner-friendly summary of regional weather conditions and confidence signals.
 */
@Component({
  selector: 'umboni-regional-forecast-dashboard',
  standalone: true,
  imports: [CommonModule, TemperatureTrendComponent],
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    <main class="page-shell">
      <section class="hero-panel">
        <p class="eyebrow">Umboni Weather Intelligence Platform</p>
        <h1>24-hour ensemble weather forecast for New England</h1>
        <p class="hero-copy">
          This dashboard visualizes the consensus output produced by the Python fetch layer and
          the Fortran simulation engine. Each location card shows the temperature trend,
          confidence level, and first several hourly forecasts.
        </p>

        @if (regionalForecastDocument(); as regionalForecastDocumentValue) {
          <div class="summary-grid">
            <article class="summary-card">
              <h2>Locations</h2>
              <p>{{ regionalForecastDocumentValue.locationCount }}</p>
            </article>
            <article class="summary-card">
              <h2>Average starting temperature</h2>
              <p>{{ regionalAverageStartingTemperatureCelsius() | number: '1.0-1' }} C</p>
            </article>
            <article class="summary-card">
              <h2>Average confidence</h2>
              <p>{{ averageConfidencePercentage() | number: '1.0-0' }}%</p>
            </article>
          </div>
        }
      </section>

      @if (locationForecasts().length > 0) {
        <section class="location-grid">
          @for (locationForecast of locationForecasts(); track locationForecast.locationName) {
            <article class="location-card">
              <header class="location-card-header">
                <div>
                  <p class="location-eyebrow">{{ locationForecast.stateName }}</p>
                  <h2>{{ locationForecast.locationName }}</h2>
                </div>
                <div class="confidence-chip">
                  {{ startingConfidencePercentage(locationForecast) | number: '1.0-0' }}% confidence
                </div>
              </header>

              <umboni-temperature-trend [hourlyForecasts]="locationForecast.hourlyForecasts" />

              <div class="daily-range">
                <span>Minimum: {{ locationForecast.dailySummary.minimumTemperatureCelsius | number: '1.0-1' }} C</span>
                <span>Maximum: {{ locationForecast.dailySummary.maximumTemperatureCelsius | number: '1.0-1' }} C</span>
              </div>

              <div class="table-wrapper">
                <table class="forecast-table">
                  <thead>
                    <tr>
                      <th>Hour</th>
                      <th>Temperature</th>
                      <th>Rain chance</th>
                      <th>Wind</th>
                      <th>Coverage</th>
                    </tr>
                  </thead>
                  <tbody>
                    @for (hourlyForecast of firstSixHours(locationForecast); track hourlyForecast.forecastHourOffset) {
                      <tr>
                        <td>{{ hourlyForecast.forecastHourOffset }}</td>
                        <td>{{ hourlyForecast.ensembleAirTemperatureCelsius | number: '1.0-1' }} C</td>
                        <td>{{ hourlyForecast.ensemblePrecipitationProbabilityPercentage | number: '1.0-0' }}%</td>
                        <td>{{ hourlyForecast.ensembleWindSpeedKilometersPerHour | number: '1.0-1' }} km/h</td>
                        <td>{{ hourlyForecast.providerCoverageCount }}</td>
                      </tr>
                    }
                  </tbody>
                </table>
              </div>
            </article>
          }
        </section>
      } @else {
        <section class="hero-panel">
          <p>Loading forecast data...</p>
        </section>
      }
    </main>
  `,
  styles: [
    `
      .page-shell {
        padding: 2rem;
      }

      .hero-panel,
      .location-card {
        border: 1px solid var(--panel-border);
        border-radius: 28px;
        background: var(--panel-background);
        backdrop-filter: blur(10px);
        box-shadow: 0 18px 50px rgba(18, 44, 69, 0.08);
      }

      .hero-panel {
        padding: 2.5rem;
      }

      .eyebrow,
      .location-eyebrow {
        margin: 0 0 0.5rem;
        text-transform: uppercase;
        letter-spacing: 0.12em;
        font-size: 0.8rem;
        color: var(--accent-color);
      }

      .hero-copy {
        max-width: 60rem;
        line-height: 1.6;
      }

      .summary-grid,
      .location-grid {
        display: grid;
        gap: 1rem;
      }

      .summary-grid {
        margin-top: 1.75rem;
        grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
      }

      .summary-card {
        padding: 1rem 1.2rem;
        border-radius: 20px;
        background: rgba(216, 239, 247, 0.55);
      }

      .summary-card p {
        margin: 0;
        font-size: 1.8rem;
        font-weight: 700;
      }

      .location-grid {
        margin-top: 1.5rem;
        grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
      }

      .location-card {
        padding: 1.4rem;
      }

      .location-card-header {
        display: flex;
        justify-content: space-between;
        gap: 1rem;
        align-items: flex-start;
      }

      .confidence-chip {
        padding: 0.5rem 0.85rem;
        border-radius: 999px;
        background: var(--accent-soft-color);
        font-weight: 600;
      }

      .daily-range {
        display: flex;
        justify-content: space-between;
        gap: 1rem;
        margin: 1rem 0;
        font-size: 0.95rem;
      }

      .table-wrapper {
        overflow-x: auto;
      }

      .forecast-table {
        width: 100%;
      }

      .forecast-table th,
      .forecast-table td {
        padding: 0.75rem 0.5rem;
        border-bottom: 1px solid rgba(17, 38, 60, 0.08);
        text-align: left;
      }

      @media (max-width: 720px) {
        .page-shell {
          padding: 1rem;
        }

        .location-card-header,
        .daily-range {
          flex-direction: column;
        }
      }
    `
  ]
})
export class RegionalForecastDashboardComponent {
  private readonly forecastDataService = inject(ForecastDataService);

  /**
   * Converts the forecast stream to an Angular signal so templates can stay declarative.
   */
  protected readonly regionalForecastDocument = toSignal(this.forecastDataService.loadRegionalForecast(), {
    initialValue: null
  });

  protected readonly locationForecasts = computed(
    () => this.regionalForecastDocument()?.locations ?? []
  );

  protected readonly regionalAverageStartingTemperatureCelsius = computed(() => {
    const locationForecasts = this.locationForecasts();
    if (locationForecasts.length === 0) {
      return 0;
    }

    const totalStartingTemperature = locationForecasts.reduce((runningTotal, locationForecast) => {
      return runningTotal + (locationForecast.hourlyForecasts[0]?.ensembleAirTemperatureCelsius ?? 0);
    }, 0);

    return totalStartingTemperature / locationForecasts.length;
  });

  protected readonly averageConfidencePercentage = computed(() => {
    const locationForecasts = this.locationForecasts();
    if (locationForecasts.length === 0) {
      return 0;
    }

    const totalConfidence = locationForecasts.reduce((runningTotal, locationForecast) => {
      return runningTotal + this.startingConfidencePercentage(locationForecast);
    }, 0);

    return totalConfidence / locationForecasts.length;
  });

  /**
   * Returns the first forecast confidence number because it is the easiest summary signal for newcomers.
   */
  protected startingConfidencePercentage(locationForecast: LocationForecast): number {
    return locationForecast.hourlyForecasts[0]?.confidencePercentage ?? 0;
  }

  /**
   * Limits the table to six hours so each card remains readable on laptops and tablets.
   */
  protected firstSixHours(locationForecast: LocationForecast): readonly HourlyForecast[] {
    return locationForecast.hourlyForecasts.slice(0, 6);
  }
}
