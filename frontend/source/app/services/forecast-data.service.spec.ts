import { provideHttpClient } from '@angular/common/http';
import { provideHttpClientTesting, HttpTestingController } from '@angular/common/http/testing';
import { TestBed } from '@angular/core/testing';

import { sampleRegionalForecastDocument } from '../testing/sample-forecast.fixture';
import { ForecastDataService } from './forecast-data.service';

describe('ForecastDataService', () => {
  it('loads the latest regional forecast from the public data directory', () => {
    TestBed.configureTestingModule({
      providers: [provideHttpClient(), provideHttpClientTesting(), ForecastDataService]
    });

    const forecastDataService = TestBed.inject(ForecastDataService);
    const httpTestingController = TestBed.inject(HttpTestingController);

    let receivedRegionName = '';

    forecastDataService.loadRegionalForecast().subscribe((regionalForecastDocument) => {
      receivedRegionName = regionalForecastDocument.regionName;
    });

    const pendingRequest = httpTestingController.expectOne('/data/new-england-forecast-sample.json');
    pendingRequest.flush(sampleRegionalForecastDocument);
    httpTestingController.verify();

    expect(receivedRegionName).toBe('New England');
  });
});
