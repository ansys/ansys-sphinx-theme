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
  const searchInput = await page.waitForSelector(
    'input[type="search"]:visible, input[placeholder*="Search" i]:visible',
    { timeout: 5000 },
  );
  expect(searchInput).not.toBeNull();
  await searchInput.fill("theme");
  await page.waitForTimeout(1500);
  const results = await page.$$(".result-item");
  expect(results.length).toBeGreaterThan(0);
});

test("search functionality works", async ({ page }) => {
  await page.goto("http://localhost:3000");
  // Try to open the search bar/dialog if needed
  const searchBtn = await page.$(
    'button[aria-label*="search" i], .search-bar .fa-magnifying-glass, .search-button, [data-bs-toggle="search"]',
  );
  if (searchBtn) {
    await searchBtn.click();
  } else {
    // Try keyboard shortcut (Ctrl+K or Cmd+K)
    await page.keyboard.press(
      process.platform === "darwin" ? "Meta+K" : "Control+K",
    );
  }
  // Now try to find a visible search input
  const searchInput = await page.waitForSelector(
    'input[type="search"]:visible, input[placeholder*="Search the docs ..." i]:visible',
    { timeout: 5000 },
  );
  if (!searchInput) test.skip("Search input not visible after opening search");
  await searchInput.fill("theme");
  console.log('Filled search input with query "theme"');
  console.log(`${await searchInput.evaluate((el) => el.value)}`);
  // console search input
  console.log(`${searchInput}`);
  // Wait longer for instant search to update results
  await page.waitForTimeout(1500);
  const results = await page.$$(".static-search-results .result-item");
  console.log(`Found ${results.length} search results.`);
  console.log(
    "Search results:",
    await Promise.all(results.map(async (r) => await r.textContent())),
  );
  expect(results.length).toBeGreaterThan(0);
});
