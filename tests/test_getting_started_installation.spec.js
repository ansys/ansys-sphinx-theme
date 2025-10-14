import { test, expect } from '@playwright/test';

test('getting started installation page loads', async ({ page }) => {
  await page.goto('http://localhost:3000/getting-started/installation.html');
  const header = await page.$('h1');
  expect(header).not.toBeNull();
});
