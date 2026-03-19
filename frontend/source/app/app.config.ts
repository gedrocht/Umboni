import { provideHttpClient } from '@angular/common/http';
import { ApplicationConfig } from '@angular/core';
import { provideRouter } from '@angular/router';

import { applicationRoutes } from './app.routes';

/**
 * Centralizes top-level providers so bootstrap code stays minimal and easy to scan.
 */
export const applicationConfiguration: ApplicationConfig = {
  providers: [provideHttpClient(), provideRouter(applicationRoutes)]
};

