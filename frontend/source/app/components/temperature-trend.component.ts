import { CommonModule } from '@angular/common';
import { ChangeDetectionStrategy, Component, computed, input } from '@angular/core';

import type { HourlyForecast } from '../models/regional-forecast';

/**
 * Renders a tiny SVG temperature trend so the dashboard remains visual without a charting dependency.
 */
@Component({
  selector: 'umboni-temperature-trend',
  standalone: true,
  imports: [CommonModule],
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    <figure class="trend-figure">
      <svg
        class="trend-graphic"
        viewBox="0 0 240 100"
        preserveAspectRatio="none"
        role="img"
        aria-label="Temperature trend over the next several forecast hours"
      >
        <defs>
          <linearGradient id="temperatureTrendGradient" x1="0%" x2="100%" y1="0%" y2="0%">
            <stop offset="0%" stop-color="#0a7a9f" />
            <stop offset="100%" stop-color="#f08c3a" />
          </linearGradient>
        </defs>
        <polyline
          [attr.points]="polylinePoints()"
          fill="none"
          stroke="url(#temperatureTrendGradient)"
          stroke-width="4"
          stroke-linejoin="round"
          stroke-linecap="round"
        />
      </svg>
      <figcaption class="trend-caption">
        {{ minimumTemperatureCelsius() | number: '1.0-1' }} to
        {{ maximumTemperatureCelsius() | number: '1.0-1' }} degrees Celsius
      </figcaption>
    </figure>
  `,
  styles: [
    `
      .trend-figure {
        margin: 0;
      }

      .trend-graphic {
        width: 100%;
        height: 110px;
        border-radius: 18px;
        background: linear-gradient(180deg, rgba(216, 239, 247, 0.85), rgba(255, 255, 255, 0.45));
      }

      .trend-caption {
        margin-top: 0.5rem;
        font-size: 0.95rem;
      }
    `
  ]
})
export class TemperatureTrendComponent {
  readonly hourlyForecasts = input.required<readonly HourlyForecast[]>();

  /**
   * Computes SVG points by scaling forecast temperatures into a compact sparkline.
   */
  protected readonly polylinePoints = computed(() => {
    const hourlyForecasts = this.hourlyForecasts();
    if (hourlyForecasts.length === 0) {
      return '0,50 240,50';
    }

    const temperatureValues = hourlyForecasts.map(
      (hourlyForecast) => hourlyForecast.ensembleAirTemperatureCelsius
    );
    const minimumTemperatureCelsius = Math.min(...temperatureValues);
    const maximumTemperatureCelsius = Math.max(...temperatureValues);
    const temperatureRange = Math.max(maximumTemperatureCelsius - minimumTemperatureCelsius, 1);

    return hourlyForecasts
      .map((hourlyForecast, currentIndex) => {
        const xCoordinate = (240 / Math.max(hourlyForecasts.length - 1, 1)) * currentIndex;
        const normalizedTemperature =
          (hourlyForecast.ensembleAirTemperatureCelsius - minimumTemperatureCelsius) / temperatureRange;
        const yCoordinate = 88 - normalizedTemperature * 76;
        return `${xCoordinate},${yCoordinate}`;
      })
      .join(' ');
  });

  protected readonly minimumTemperatureCelsius = computed(() =>
    this.hourlyForecasts().length === 0
      ? 0
      : Math.min(
          ...this.hourlyForecasts().map(
            (hourlyForecast) => hourlyForecast.ensembleAirTemperatureCelsius
          )
        )
  );

  protected readonly maximumTemperatureCelsius = computed(() =>
    this.hourlyForecasts().length === 0
      ? 0
      : Math.max(
          ...this.hourlyForecasts().map(
            (hourlyForecast) => hourlyForecast.ensembleAirTemperatureCelsius
          )
        )
  );
}
