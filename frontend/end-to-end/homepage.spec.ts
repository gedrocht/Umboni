import { test, expect } from '@playwright/test';

test('homepage shows the main New England weather heading', async ({ page }) => {
  await page.goto('/');

  await expect(
    page.getByRole('heading', { name: '24-hour ensemble weather forecast for New England' })
  ).toBeVisible();
});

