import { test, expect } from '@playwright/test';

test('search bar appears and returns results', async ({ page }) => {
  await page.goto('http://localhost:3000');
  const searchBtn = await page.$('button[aria-label*="search" i], .search-bar .fa-magnifying-glass, .search-button, [data-bs-toggle="search"]');
  if (searchBtn) {
    await searchBtn.click();
  } else {
    await page.keyboard.press(process.platform === 'darwin' ? 'Meta+K' : 'Control+K');
  }
  const searchInput = await page.waitForSelector('input[type="search"]:visible, input[placeholder*="Search" i]:visible', { timeout: 5000 });
  expect(searchInput).not.toBeNull();
  await searchInput.fill('theme');
  await page.waitForTimeout(1500);
  const results = await page.$$('.result-item');
  expect(results.length).toBeGreaterThan(0);
});
