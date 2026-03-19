import type { Routes } from '@angular/router';

import { RegionalForecastDashboardComponent } from './components/regional-forecast-dashboard.component';

/**
 * The application is intentionally simple, so a single dashboard route is enough.
 */
export const applicationRoutes: Routes = [
  {
    path: '',
    component: RegionalForecastDashboardComponent
  }
];

