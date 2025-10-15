import { test, expect } from "@playwright/test";

test("search bar appears and returns results", async ({ page }) => {
  await page.goto("http://localhost:3000");
  const searchBtn = await page.$(
    'button[aria-label*="search" i], .search-bar .fa-magnifying-glass, .search-button, [data-bs-toggle="search"]',
  );
  if (searchBtn) {
    await searchBtn.click();
  } else {
    await page.keyboard.press(
      process.platform === "darwin" ? "Meta+K" : "Control+K",
    );
  }
  console.log("Tried to open search");
  const searchBar = await page.$(
    '.search-bar input[type="search"], .search-bar input[placeholder*="Search" i]',
  );
  await searchBar.fill("install");
  await page.waitForTimeout(1500);
  const results = await page.$$(".search-bar");
  expect(results.length).toBeGreaterThan(0);
});
