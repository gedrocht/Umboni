import { NEVER, of } from 'rxjs';
import { TestBed } from '@angular/core/testing';

import { ForecastDataService } from '../services/forecast-data.service';
import type { RegionalForecastDocument } from '../models/regional-forecast';
import { sampleRegionalForecastDocument } from '../testing/sample-forecast.fixture';
import { RegionalForecastDashboardComponent } from './regional-forecast-dashboard.component';

describe('RegionalForecastDashboardComponent', () => {
  function buildForecastDataServiceStub(
    regionalForecastDocument: RegionalForecastDocument
  ): Pick<ForecastDataService, 'loadRegionalForecast'> {
    return {
      loadRegionalForecast(): ReturnType<ForecastDataService['loadRegionalForecast']> {
        return of(regionalForecastDocument);
      }
    };
  }

  it('renders location cards for the supplied forecast document', async (): Promise<void> => {
    await TestBed.configureTestingModule({
      imports: [RegionalForecastDashboardComponent],
      providers: [
        {
          provide: ForecastDataService,
          useValue: buildForecastDataServiceStub(sampleRegionalForecastDocument)
        }
      ]
    }).compileComponents();

    const fixture = TestBed.createComponent(RegionalForecastDashboardComponent);
    fixture.detectChanges();

    const renderedElement = fixture.nativeElement as HTMLElement;
    const renderedText = renderedElement.textContent ?? '';
    expect(renderedText).toContain('24-hour ensemble weather forecast for New England');
    expect(renderedText).toContain('Boston');
    expect(renderedText).toContain('Portland');
  });

  it('shows the loading fallback when the forecast document has no locations', async (): Promise<void> => {
    await TestBed.configureTestingModule({
      imports: [RegionalForecastDashboardComponent],
      providers: [
        {
          provide: ForecastDataService,
          useValue: buildForecastDataServiceStub({
            regionName: 'New England',
            locationCount: 0,
            locations: []
          })
        }
      ]
    }).compileComponents();

    const fixture = TestBed.createComponent(RegionalForecastDashboardComponent);
    fixture.detectChanges();

    const renderedElement = fixture.nativeElement as HTMLElement;
    const renderedText = renderedElement.textContent ?? '';

    expect(renderedText).toContain('Loading forecast data...');
  });

  it('keeps the loading fallback visible before the forecast service emits', async (): Promise<void> => {
    await TestBed.configureTestingModule({
      imports: [RegionalForecastDashboardComponent],
      providers: [
        {
          provide: ForecastDataService,
          useValue: {
            loadRegionalForecast(): ReturnType<ForecastDataService['loadRegionalForecast']> {
              return NEVER;
            }
          }
        }
      ]
    }).compileComponents();

    const fixture = TestBed.createComponent(RegionalForecastDashboardComponent);
    fixture.detectChanges();

    const renderedElement = fixture.nativeElement as HTMLElement;
    const renderedText = renderedElement.textContent ?? '';

    expect(renderedText).toContain('Loading forecast data...');
  });

  it('falls back to zero-valued summary signals when a location has no hourly forecast rows', async (): Promise<void> => {
    await TestBed.configureTestingModule({
      imports: [RegionalForecastDashboardComponent],
      providers: [
        {
          provide: ForecastDataService,
          useValue: buildForecastDataServiceStub({
            regionName: 'New England',
            locationCount: 1,
            locations: [
              {
                ...sampleRegionalForecastDocument.locations[0],
                hourlyForecasts: []
              }
            ]
          })
        }
      ]
    }).compileComponents();

    const fixture = TestBed.createComponent(RegionalForecastDashboardComponent);
    fixture.detectChanges();

    const renderedElement = fixture.nativeElement as HTMLElement;
    const renderedText = renderedElement.textContent ?? '';

    expect(renderedText).toContain('Average starting temperature');
    expect(renderedText).toContain('0.0 C');
    expect(renderedText).toContain('0% confidence');
  });
});
