import { test, expect } from "@playwright/test";

// MCP Server admonition is configured in doc/source/conf.py for the demo site.
// These tests verify the admonition renders correctly on the landing page and
// is absent on other pages.

test("MCP server admonition is visible on the landing page", async ({
  page,
}) => {
  await page.goto("http://localhost:8000/index.html");
  const admonition = await page.$(".admonition.ast-mcp-server-banner");
  expect(admonition).not.toBeNull();
});

test("MCP server admonition contains the configured project name", async ({
  page,
}) => {
  await page.goto("http://localhost:8000/index.html");
  const admonition = await page.$(".admonition.ast-mcp-server-banner");
  expect(admonition).not.toBeNull();
  const text = await admonition.textContent();
  expect(text).toMatch(/Ansys Sphinx Theme MCP Server/i);
});

test("MCP server admonition has a working learn-more link", async ({
  page,
}) => {
  await page.goto("http://localhost:8000/index.html");
  const link = await page.$(".ast-mcp-server-banner__link");
  expect(link).not.toBeNull();
  const href = await link.getAttribute("href");
  expect(href).toBeTruthy();
  // Link must open in a new tab (target="_blank")
  const target = await link.getAttribute("target");
  expect(target).toBe("_blank");
});

test("MCP server admonition is NOT shown on non-landing pages", async ({
  page,
}) => {
  await page.goto("http://localhost:8000/user-guide/options.html");
  const admonition = await page.$(".admonition.ast-mcp-server-banner");
  expect(admonition).toBeNull();
});
