import { test, expect } from "@playwright/test";

// MCP Server banner is configured in doc/source/conf.py for the demo site.
// These tests verify the banner renders correctly on the landing page and
// is absent on other pages.

test("MCP server banner is visible on the landing page", async ({ page }) => {
  await page.goto("http://localhost:8000/index.html");
  const banner = await page.$(".ast-mcp-server-banner");
  expect(banner).not.toBeNull();
});

test("MCP server banner contains the configured project name", async ({
  page,
}) => {
  await page.goto("http://localhost:8000/index.html");
  const banner = await page.$(".ast-mcp-server-banner");
  expect(banner).not.toBeNull();
  const text = await banner.textContent();
  expect(text).toMatch(/Ansys Sphinx Theme MCP Server/i);
});

test("MCP server banner has a working learn-more link", async ({ page }) => {
  await page.goto("http://localhost:8000/index.html");
  const link = await page.$(".ast-mcp-server-banner__link");
  expect(link).not.toBeNull();
  const href = await link.getAttribute("href");
  expect(href).toBeTruthy();
  // Link must open in a new tab (target="_blank")
  const target = await link.getAttribute("target");
  expect(target).toBe("_blank");
});

test("MCP server banner is NOT shown on non-landing pages", async ({
  page,
}) => {
  await page.goto("http://localhost:8000/user-guide/options.html");
  const banner = await page.$(".ast-mcp-server-banner");
  expect(banner).toBeNull();
});
