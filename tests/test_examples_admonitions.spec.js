import { test, expect } from '@playwright/test';

test('examples admonitions page loads', async ({ page }) => {
  await page.goto('http://localhost:3000/examples/admonitions.html');
  const admonition = await page.$('.admonition, .note, .warning, .alert');
  expect(admonition).not.toBeNull();
});

test('examples admonitions page has at least one note', async ({ page }) => {
  await page.goto('http://localhost:3000/examples/admonitions.html');
  const notes = await page.$$('.note');
  expect(notes.length).toBeGreaterThan(0);
});

test('examples admonitions page has at least one warning', async ({ page }) => {
  await page.goto('http://localhost:3000/examples/admonitions.html');
  const warnings = await page.$$('.warning');
  expect(warnings.length).toBeGreaterThan(0);
});

test('examples admonitions page has at least one alert', async ({ page }) => {
  await page.goto('http://localhost:3000/examples/admonitions.html');
  const alerts = await page.$$('.alert');
  expect(alerts.length).toBeGreaterThan(0);
});
