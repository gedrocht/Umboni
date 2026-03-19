import { bootstrapApplication } from '@angular/platform-browser';

import { applicationConfiguration } from './app/app.config';
import { AppComponent } from './app/app.component';

void bootstrapApplication(AppComponent, applicationConfiguration).catch((bootstrapError: unknown) => {
  // The browser console is still the fastest place to inspect catastrophic startup failures.
  console.error('The Umboni Angular application failed to bootstrap.', bootstrapError);
});

