import { test, expect } from "@playwright/test";

// Deeply nested autoapi-generated pages are a good stress test for the
// plain-text sidebar-title invariant, because their titles come from Python
// symbol names that may contain characters requiring escaping.
const API_PAGES = [
  "http://localhost:8000/examples/api/examples/sample_func/index.html",
  "http://localhost:8000/examples/api/examples/samples/ExamplePydanticClass.html",
];

test("sidebar section title renders plain text on API pages", async ({ page }) => {
  for (const url of API_PAGES) {
    await page.goto(url);
    const title = page.locator(".bd-docs-nav .bd-links__title");
    await expect(title).toHaveCount(1);

    const sidebarTitleState = await title.evaluate((el) => ({
      text: (el.textContent || "").trim(),
      html: el.innerHTML,
      ariaLabel:
        el.closest(".bd-docs-nav")?.getAttribute("aria-label")?.trim() || "",
    }));

    expect(sidebarTitleState.text).toBeTruthy();
    expect(sidebarTitleState.text).not.toMatch(/[<>]/);
    expect(sidebarTitleState.ariaLabel).toBe(sidebarTitleState.text);
    expect(sidebarTitleState.html).toBe(sidebarTitleState.text);
    expect(sidebarTitleState.html).not.toContain("<code");
    expect(sidebarTitleState.html).not.toContain("&lt;");
  }
});
