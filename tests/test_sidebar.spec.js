import { test, expect } from '@playwright/test';

test('sidebar is present and contains links', async ({ page }) => {
  await page.goto('http://localhost:3000/user-guide.html');
  const sidebar = await page.$('.bd-sidebar-primary, .bd-sidebar-secondary, .sidebar, nav[role="navigation"]');
  expect(sidebar).not.toBeNull();
  const links = await sidebar.$$('a');
  expect(links.length).toBeGreaterThan(0);
});
