import { test, expect } from '@playwright/test';

test('theme switch button toggles mode', async ({ page }) => {
  await page.goto('http://localhost:3000');
  const themeSwitcher = await page.$('button.theme-switch-button[aria-label="Color mode"]');
  expect(themeSwitcher).not.toBeNull();
  const getActiveMode = async () => {
    return await page.evaluate(() => {
      if (document.documentElement.dataset.theme) return document.documentElement.dataset.theme;
      if (document.body.dataset.theme) return document.body.dataset.theme;
      const svgs = Array.from(document.querySelectorAll('button.theme-switch-button svg.theme-switch[data-mode]'));
      for (const svg of svgs) {
        const style = window.getComputedStyle(svg);
        if (style.display !== 'none' && style.visibility !== 'hidden' && style.opacity !== '0') {
          return svg.getAttribute('data-mode');
        }
      }
      return svgs.length ? svgs[0].getAttribute('data-mode') : null;
    });
  };
  const currentMode = await getActiveMode();
  await themeSwitcher.click();
  await page.waitForTimeout(500);
  const newMode = await getActiveMode();
  expect(newMode).not.toBe(currentMode);
});
