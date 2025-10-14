import { test, expect } from "@playwright/test";

test("homepage loads and shows main header", async ({ page }) => {
  await page.goto("http://localhost:3000/index.html");
  const header = await page.$("h1");
  expect(header).not.toBeNull();
  expect(await header.textContent()).toMatch(/Ansys Sphinx Theme|Welcome/i);
});
