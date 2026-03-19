import { Component } from '@angular/core';
import { RouterOutlet } from '@angular/router';

/**
 * Hosts the routed dashboard experience.
 */
@Component({
  selector: 'umboni-root',
  imports: [RouterOutlet],
  standalone: true,
  template: `
    <router-outlet />
  `
})
export class AppComponent {}

