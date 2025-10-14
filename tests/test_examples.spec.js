import { test, expect } from "@playwright/test";

test("example sphinx design page card", async ({ page }) => {
  await page.goto("http://localhost:3000/examples/sphinx-design.html");
  const card = await page.$(".sd-card, .card, div.sd-card");
  expect(card).not.toBeNull();
});

test("example sphinx design page grid", async ({ page }) => {
  await page.goto("http://localhost:3000/examples/sphinx-design.html");
  const grid = await page.$(".sd-row, .sd-grid, .row, .grid");
  expect(grid).not.toBeNull();
});

test("example sphinx design page badge", async ({ page }) => {
  await page.goto("http://localhost:3000/examples/sphinx-design.html");
  // Sphinx-design badges are usually rendered as span.sd-badge or similar
  const badge = await page.$(".sd-badge, span.sd-badge, button.sd-badge");
  expect(badge).not.toBeNull();
  // Only click if it's a button or has a click handler
  if (badge) {
    const tag = await badge.evaluate((el) => el.tagName.toLowerCase());
    if (tag === "button") {
      await badge.click();
    }
    // If not a button, just check it exists
  }
});

test("clickable card navigates to external link", async ({ page }) => {
  await page.goto("http://localhost:3000/examples/sphinx-design.html");
  // Find the stretched link inside the card
  const link = await page.$(
    '.sd-card:has(.sd-card-title:has-text("Clickable Card (external)")) a.sd-stretched-link',
  );
  expect(link).not.toBeNull();
  const href = await link.getAttribute("href");
  // Check if link opens in new tab
  const target = await link.getAttribute("target");
  if (target === "_blank") {
    const [newPage] = await Promise.all([
      page.context().waitForEvent("page"),
      link.click(),
    ]);
    await newPage.waitForLoadState();
    expect(newPage.url()).toContain(href);
  } else {
    await Promise.all([page.waitForNavigation(), link.click()]);
    expect(page.url()).toContain(href);
  }
});

test("examples admonitions page loads", async ({ page }) => {
  await page.goto("http://localhost:3000/examples/admonitions.html");
  const admonition = await page.$(".admonition, .note, .warning, .alert");
  expect(admonition).not.toBeNull();
});
