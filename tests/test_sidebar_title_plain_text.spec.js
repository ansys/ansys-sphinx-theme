import { test, expect } from "@playwright/test";

// Deeply nested autoapi-generated pages are a good stress test for the
// plain-text sidebar-title invariant, because their titles come from Python
// symbol names that may contain characters requiring escaping.
const API_PAGES = [
  "http://localhost:8000/examples/api/examples/sample_func/index.html",
  "http://localhost:8000/examples/api/examples/samples/ExamplePydanticClass.html",
];

test("sidebar section title renders plain text on API pages", async ({
  page,
}) => {
  for (const url of API_PAGES) {
    await page.goto(url);
    const title = page.locator(".bd-docs-nav .bd-links__title");
    await expect(title).toHaveCount(1);

    const sidebarTitleState = await title.evaluate((el) => ({
      text: (el.textContent || "").trim(),
      html: el.innerHTML,
      ariaLabel:
        el.closest(".bd-docs-nav")?.getAttribute("aria-label")?.trim() || "",
      hasChildElements: el.children.length > 0,
      hasCodeTag: !!el.querySelector("code"),
    }));

    expect(sidebarTitleState.text).toBeTruthy();
    expect(sidebarTitleState.ariaLabel).toBe(sidebarTitleState.text);
    // Keep the title as plain text: no nested markup should be injected.
    expect(sidebarTitleState.hasChildElements).toBe(false);
    expect(sidebarTitleState.hasCodeTag).toBe(false);
    // If title text contains literal angle brackets, HTML serialization may
    // include escaped entities (for example, "&lt;"), which is expected.
    expect(sidebarTitleState.html).not.toContain("<code");
  }
});

test("sidebar section title is always non-empty on docs pages", async ({
  page,
}) => {
  const urls = [
    "http://localhost:8000/user-guide/options.html",
    "http://localhost:8000/getting-started/index.html",
  ];

  for (const url of urls) {
    await page.goto(url);
    const title = page.locator(".bd-docs-nav .bd-links__title");
    await expect(title).toHaveCount(1);
    await expect(title).not.toHaveText(/^\s*$/);
  }
});
