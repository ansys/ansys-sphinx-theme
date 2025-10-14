import { test, expect } from "@playwright/test";

test("contribute developer page loads", async ({ page }) => {
  await page.goto("http://localhost:3000/contribute/developer.html");
  const header = await page.$("h1");
  expect(header).not.toBeNull();
});
