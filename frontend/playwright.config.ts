import { defineConfig } from '@playwright/test';

export default defineConfig({
  testDir: './end-to-end',
  use: {
    baseURL: 'http://127.0.0.1:4200'
  },
  webServer: {
    command: 'npm run start -- --host 127.0.0.1 --port 4200',
    port: 4200,
    reuseExistingServer: !process.env.CI
  }
});
