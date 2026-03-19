import { of } from 'rxjs';
import { TestBed } from '@angular/core/testing';

import { ForecastDataService } from '../services/forecast-data.service';
import { sampleRegionalForecastDocument } from '../testing/sample-forecast.fixture';
import { RegionalForecastDashboardComponent } from './regional-forecast-dashboard.component';

describe('RegionalForecastDashboardComponent', () => {
  it('renders location cards for the supplied forecast document', async () => {
    await TestBed.configureTestingModule({
      imports: [RegionalForecastDashboardComponent],
      providers: [
        {
          provide: ForecastDataService,
          useValue: {
            loadRegionalForecast: () => of(sampleRegionalForecastDocument)
          }
        }
      ]
    }).compileComponents();

    const fixture = TestBed.createComponent(RegionalForecastDashboardComponent);
    fixture.detectChanges();

    const renderedText = fixture.nativeElement.textContent as string;
    expect(renderedText).toContain('24-hour ensemble weather forecast for New England');
    expect(renderedText).toContain('Boston');
    expect(renderedText).toContain('Portland');
  });
});

