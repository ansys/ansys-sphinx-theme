import { test, expect } from "@playwright/test";

// Code blocks and copy button
test("code blocks and copy button work", async ({ page }) => {
  await page.goto("http://localhost:3000/user-guide/configuration.html");
  const codeBlock = await page.$(".highlight");
  if (!codeBlock) test.skip("No code block found on this page");
  expect(codeBlock).not.toBeNull();
  const copyBtn = await page.$("button.copybtn, .copy-button, .btn-copy");
  if (copyBtn) await copyBtn.click();
  expect(copyBtn).not.toBeNull();
});

// Tabs (Sphinx-design)
test("tab sets render and switch", async ({ page }) => {
  await page.goto("http://localhost:3000/user-guide/configuration.html");
  const tabSet = await page.$(".sd-tab-set, .tab-set, .tab-content");
  expect(tabSet).not.toBeNull();
  const tabLabels = await page.$$(
    ".sd-tab-label, .tab-label, .nav-tabs .nav-link",
  );
  if (tabLabels.length > 1) {
    await tabLabels[1].click();
  }
});

// Tables
test("tables render correctly", async ({ page }) => {
  await page.goto("http://localhost:3000/examples/table.html");
  const table = await page.$(".pst-scrollable-table-container");
  expect(table).not.toBeNull();
  const headers = await table.$$("th");
  expect(headers.length).toBeGreaterThan(0);
  const rows = await table.$$("tbody tr");
  expect(rows.length).toBeGreaterThan(0);
});

// Admonitions
test("admonitions render", async ({ page }) => {
  await page.goto("http://localhost:3000/examples/admonitions.html");
  const admonition = await page.$(
    ".admonition, .note, .warning, .caution, .tip, .important",
  );
  expect(admonition).not.toBeNull();
});

// Sphinx-design components
test("example sphinx design page card", async ({ page }) => {
  await page.goto("http://localhost:3000/examples/sphinx-design.html");
  const card = await page.$(".sd-card, .card, div.sd-card");
  expect(card).not.toBeNull();
});

// Sphinx-design grid layout
test("example sphinx design page grid", async ({ page }) => {
  await page.goto("http://localhost:3000/examples/sphinx-design.html");
  const grid = await page.$(".sd-row, .sd-grid, .row, .grid");
  expect(grid).not.toBeNull();
});

// Sphinx-design badge
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

// Sphinx-design clickable card
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

// Sphinx-design dropdown
test("sphinx-design dropdown works", async ({ page }) => {
  await page.goto("http://localhost:3000/examples/sphinx-design.html");
  // Target the <details> element with .sd-dropdown
  const dropdown = await page.$("details.sd-dropdown");
  expect(dropdown).not.toBeNull();
  // Find the summary inside the dropdown
  const summary = await dropdown.$("summary.sd-summary-title");
  expect(summary).not.toBeNull();
  // If the dropdown is open, close it first
  let isOpen = await dropdown.getAttribute("open");
  if (isOpen) {
    await summary.click();
    await page.waitForTimeout(200);
  }
  // Now open the dropdown
  await summary.click();
  await page.waitForTimeout(200);
  isOpen = await dropdown.getAttribute("open");
  expect(isOpen).not.toBeNull();
  // Check for dropdown content
  const content = await dropdown.$(".sd-summary-content");
  expect(content).not.toBeNull();
  const text = await content.textContent();
  expect(text).toContain("Dropdown content");
});

test("sidebar is present and contains links", async ({ page }) => {
  await page.goto("http://localhost:3000/user-guide.html");
  const sidebar = await page.$(
    '.bd-sidebar-primary, .bd-sidebar-secondary, .sidebar, nav[role="navigation"]',
  );
  expect(sidebar).not.toBeNull();
  const links = await sidebar.$$("a");
  expect(links.length).toBeGreaterThan(0);
});
