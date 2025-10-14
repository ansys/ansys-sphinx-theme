import { test, expect } from '@playwright/test';

test('user guide configuration page loads', async ({ page }) => {
  await page.goto('http://localhost:3000/user-guide/configuration.html');
  const header = await page.$('h1');
  expect(header).not.toBeNull();
});
