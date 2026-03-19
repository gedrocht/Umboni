import { TestBed } from '@angular/core/testing';

import { sampleRegionalForecastDocument } from '../testing/sample-forecast.fixture';
import { TemperatureTrendComponent } from './temperature-trend.component';

describe('TemperatureTrendComponent', () => {
  it('renders an SVG polyline based on hourly temperatures', async (): Promise<void> => {
    await TestBed.configureTestingModule({
      imports: [TemperatureTrendComponent]
    }).compileComponents();

    const fixture = TestBed.createComponent(TemperatureTrendComponent);
    fixture.componentInstance.hourlyForecasts =
      sampleRegionalForecastDocument.locations[0].hourlyForecasts;
    fixture.detectChanges();

    const renderedElement = fixture.nativeElement as HTMLElement;
    const renderedPolyline = renderedElement.querySelector('polyline');
    const renderedCaption = renderedElement.querySelector('figcaption');

    expect(renderedPolyline).not.toBeNull();
    expect(renderedPolyline?.getAttribute('points') ?? '').toContain(',');
    expect(renderedCaption?.textContent ?? '').toContain('10.4');
    expect(renderedCaption?.textContent ?? '').toContain('12.8');
  });

  it('renders a flat fallback line when no hourly forecasts are provided', async (): Promise<void> => {
    await TestBed.configureTestingModule({
      imports: [TemperatureTrendComponent]
    }).compileComponents();

    const fixture = TestBed.createComponent(TemperatureTrendComponent);
    fixture.componentInstance.hourlyForecasts =
      undefined as unknown as typeof fixture.componentInstance.hourlyForecasts;
    fixture.detectChanges();

    const renderedElement = fixture.nativeElement as HTMLElement;
    const renderedPolyline = renderedElement.querySelector('polyline');
    const renderedCaption = renderedElement.querySelector('figcaption');

    expect(renderedPolyline?.getAttribute('points')).toBe('0,50 240,50');
    expect(renderedCaption?.textContent ?? '').toContain('0 to 0');
  });
});
