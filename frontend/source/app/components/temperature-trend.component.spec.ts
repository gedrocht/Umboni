import { TestBed } from '@angular/core/testing';

import { sampleRegionalForecastDocument } from '../testing/sample-forecast.fixture';
import { TemperatureTrendComponent } from './temperature-trend.component';

describe('TemperatureTrendComponent', () => {
  it('renders an SVG polyline based on hourly temperatures', async (): Promise<void> => {
    await TestBed.configureTestingModule({
      imports: [TemperatureTrendComponent]
    }).compileComponents();

    const fixture = TestBed.createComponent(TemperatureTrendComponent);
    fixture.componentRef.setInput(
      'hourlyForecasts',
      sampleRegionalForecastDocument.locations[0].hourlyForecasts
    );
    fixture.detectChanges();

    const renderedElement = fixture.nativeElement as HTMLElement;
    const renderedPolyline = renderedElement.querySelector('polyline');

    expect(renderedPolyline).not.toBeNull();
    expect(renderedPolyline?.getAttribute('points') ?? '').toContain(',');
  });
});
