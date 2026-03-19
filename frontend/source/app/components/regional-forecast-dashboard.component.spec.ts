import { of } from 'rxjs';
import { TestBed } from '@angular/core/testing';

import { ForecastDataService } from '../services/forecast-data.service';
import { sampleRegionalForecastDocument } from '../testing/sample-forecast.fixture';
import { RegionalForecastDashboardComponent } from './regional-forecast-dashboard.component';

describe('RegionalForecastDashboardComponent', () => {
  it('renders location cards for the supplied forecast document', async (): Promise<void> => {
    const forecastDataServiceStub: Pick<ForecastDataService, 'loadRegionalForecast'> = {
      loadRegionalForecast(): ReturnType<ForecastDataService['loadRegionalForecast']> {
        return of(sampleRegionalForecastDocument);
      }
    };

    await TestBed.configureTestingModule({
      imports: [RegionalForecastDashboardComponent],
      providers: [
        {
          provide: ForecastDataService,
          useValue: forecastDataServiceStub
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
});
