import { of } from 'rxjs';
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
});
