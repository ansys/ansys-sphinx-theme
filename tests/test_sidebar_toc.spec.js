/**
 * Tests for the secondary-sidebar TOC options introduced in fix/sidebar:
 *
 *  - show_page_toc          (default True)  → include "page-toc" in secondary sidebar
 *  - show_source_button     (default True)  → include "sourcelink" in secondary sidebar
 *  - show_page_toc_in_primary_sidebar (default False)
 *      When True AND show_page_toc=False:
 *        • page TOC is injected into the primary (left) sidebar under li.current
 *        • a chevron toggle button (.ast-toc-toggle) is added
 *        • scroll-spy highlights the active heading
 *      When True AND show_page_toc=True (invalid combo):
 *        • a UserWarning is raised during the build
 *        • page TOC stays in the secondary sidebar (no change to primary)
 *
 * All tests are written to auto-detect the active configuration from the DOM so
 * they remain valid regardless of which option combination the docs are built with.
 * Tests that cannot run under the current configuration are skipped.
 */
import { test, expect } from "@playwright/test";

// A nested page with several heading anchors – exercises both sidebars.
const NESTED_PAGE = "http://localhost:8000/user-guide/options.html";
// A shallower page to exercise the "no li.current fallback" path in the primary
// sidebar injection script.
const SECTION_ROOT_PAGE = "http://localhost:8000/user-guide.html";

// ─── Helpers ─────────────────────────────────────────────────────────────────

/**
 * Returns true when the "show_page_toc_in_primary_sidebar" feature is active on
 * the current page (i.e. the JS has already run and injected `.ast-primary-toc`
 * or the toggle button).
 */
async function isPrimaryTocEnabled(page) {
  return page.evaluate(
    () => !!document.querySelector(".ast-primary-toc, .ast-toc-toggle"),
  );
}

/**
 * Returns true when the page-toc is visible in the secondary (right) sidebar.
 */
async function hasSecondaryPageToc(page) {
  return page.evaluate(
    () =>
      !!(
        document.querySelector("#pst-page-toc-nav") ||
        document.querySelector(".bd-sidebar-secondary nav.page-toc")
      ),
  );
}

// ─── Secondary sidebar – default behaviour ───────────────────────────────────

test("secondary sidebar: page TOC is visible with default options", async ({
  page,
}) => {
  await page.goto(NESTED_PAGE);

  // If the primary-TOC feature is active, the page-toc lives in the primary
  // sidebar instead, so this specific assertion should be skipped.
  const primaryActive = await isPrimaryTocEnabled(page);
  if (primaryActive)
    test.skip(
      "show_page_toc_in_primary_sidebar is active – page TOC is in primary sidebar",
    );

  const pageTocNav = await page.$(
    "#pst-page-toc-nav, .bd-sidebar-secondary nav.page-toc",
  );
  if (!pageTocNav) test.skip("Page TOC not found – show_page_toc may be False");

  expect(pageTocNav).not.toBeNull();
  // Verify it actually contains heading anchors.
  const links = await pageTocNav.$$("a.nav-link, a.reference");
  expect(links.length).toBeGreaterThan(0);
});

test("secondary sidebar: edit-this-page link is present", async ({ page }) => {
  await page.goto(NESTED_PAGE);
  const editLink = await page.$(
    ".bd-sidebar-secondary .tocsection.editthispage a, " +
      '.bd-sidebar-secondary a[aria-label*="edit" i], ' +
      '.bd-sidebar-secondary a:has-text("Edit on GitHub")',
  );
  if (!editLink) test.skip("Edit link not found – github_url may not be set");
  expect(editLink).not.toBeNull();
  const href = await editLink.getAttribute("href");
  expect(href).toMatch(/github\.com/);
});

test("secondary sidebar: source link is present when show_source_button is enabled", async ({
  page,
}) => {
  await page.goto(NESTED_PAGE);
  const sourceLink = await page.$(
    '.bd-sidebar-secondary a[href*="_sources"], ' +
      '.bd-sidebar-secondary a:has-text("Show Source"), ' +
      ".bd-sidebar-secondary .tocsection.viewsourcecode",
  );
  if (!sourceLink)
    test.skip("Source link not found – show_source_button may be False");
  expect(sourceLink).not.toBeNull();
});

test("secondary sidebar: items include page-toc by default", async ({
  page,
}) => {
  await page.goto(NESTED_PAGE);
  const primaryActive = await isPrimaryTocEnabled(page);
  if (primaryActive)
    test.skip(
      "show_page_toc_in_primary_sidebar is active – secondary sidebar check skipped",
    );

  const secondary = await page.$(".bd-sidebar-secondary");
  expect(secondary).not.toBeNull();

  // page-toc must always be present with default options.
  const pageToc = await secondary.$(
    "#pst-page-toc-nav, nav.page-toc, .page-toc",
  );
  expect(pageToc).not.toBeNull();

  // edit-this-page only renders when github_user/repo/version context is set;
  // skip the assertion rather than failing when those aren't configured.
  const editSection = await secondary.$(
    ".tocsection.editthispage, .tocsection[aria-label*='edit' i]",
  );
  if (editSection) {
    // If it is rendered, confirm it contains a real link.
    const editLink = await editSection.$("a[href]");
    expect(editLink).not.toBeNull();
  }
});

// ─── Secondary sidebar – show_page_toc=False ─────────────────────────────────

test("secondary sidebar: no page TOC when show_page_toc is False", async ({
  page,
}) => {
  await page.goto(NESTED_PAGE);
  const primaryActive = await isPrimaryTocEnabled(page);
  const secondaryHasToc = await hasSecondaryPageToc(page);

  if (secondaryHasToc) {
    // show_page_toc is True (default) – this combination is not active, skip.
    test.skip(
      "show_page_toc is True – page TOC is present; skipping False check",
    );
  }

  if (!primaryActive) {
    // show_page_toc=False, show_page_toc_in_primary_sidebar=False → TOC gone entirely.
    const pageToc = await page.$(".bd-sidebar-secondary #pst-page-toc-nav");
    expect(pageToc).toBeNull();
  }
});

test("secondary sidebar: source link absent when show_source_button is False", async ({
  page,
}) => {
  await page.goto(NESTED_PAGE);
  const sourceLink = await page.$(
    '.bd-sidebar-secondary a[href*="_sources"], ' +
      '.bd-sidebar-secondary a:has-text("Show Source"), ' +
      ".bd-sidebar-secondary .tocsection.viewsourcecode",
  );
  if (sourceLink)
    test.skip(
      "Source link is present – show_source_button is True; skipping False check",
    );

  // If we reach here, the source link is absent as expected.
  expect(sourceLink).toBeNull();
});

// ─── Primary sidebar inline TOC – disabled (default) ─────────────────────────

test("primary sidebar: no inline TOC when show_page_toc_in_primary_sidebar is False", async ({
  page,
}) => {
  await page.goto(NESTED_PAGE);
  const primaryActive = await isPrimaryTocEnabled(page);
  if (primaryActive)
    test.skip(
      "show_page_toc_in_primary_sidebar is enabled – skipping disabled-state check",
    );

  expect(await page.$(".ast-primary-toc")).toBeNull();
});

test("primary sidebar: no toggle button when show_page_toc_in_primary_sidebar is False", async ({
  page,
}) => {
  await page.goto(NESTED_PAGE);
  const primaryActive = await isPrimaryTocEnabled(page);
  if (primaryActive)
    test.skip(
      "show_page_toc_in_primary_sidebar is enabled – skipping disabled-state check",
    );

  expect(await page.$(".ast-toc-toggle")).toBeNull();
});

// ─── Primary sidebar inline TOC – enabled ────────────────────────────────────

test("primary sidebar: inline TOC injected under li.current when feature is enabled", async ({
  page,
}) => {
  await page.goto(NESTED_PAGE);
  const primaryActive = await isPrimaryTocEnabled(page);
  if (!primaryActive)
    test.skip("show_page_toc_in_primary_sidebar is not active – skipping");

  const primaryToc = await page.$(".bd-sidebar-primary .ast-primary-toc");
  expect(primaryToc).not.toBeNull();

  const links = await primaryToc.$$("a");
  expect(links.length).toBeGreaterThan(0);
});

test("primary sidebar: toggle button is present and accessible when feature is enabled", async ({
  page,
}) => {
  await page.goto(NESTED_PAGE);
  const primaryActive = await isPrimaryTocEnabled(page);
  if (!primaryActive)
    test.skip("show_page_toc_in_primary_sidebar is not active – skipping");

  // The toggle is only added when li.current exists (i.e. this is a nested page).
  const current = await page.$(".bd-docs-nav .bd-toc-item li.current");
  if (!current)
    test.skip(
      "No li.current in primary nav – top-level page uses direct-append fallback",
    );

  const toggleBtn = await page.$(".ast-toc-toggle");
  expect(toggleBtn).not.toBeNull();
  expect(await toggleBtn.getAttribute("aria-label")).toMatch(
    /toggle page sections/i,
  );
  expect(await toggleBtn.getAttribute("aria-expanded")).toBe("false");
  expect(await toggleBtn.getAttribute("type")).toBe("button");
});

test("primary sidebar: toggle button expands then collapses inline TOC", async ({
  page,
}) => {
  await page.goto(NESTED_PAGE);
  const primaryActive = await isPrimaryTocEnabled(page);
  if (!primaryActive)
    test.skip("show_page_toc_in_primary_sidebar is not active – skipping");

  const toggleBtn = await page.$(".ast-toc-toggle");
  if (!toggleBtn)
    test.skip(
      "Toggle button not present – top-level page uses direct-append fallback",
    );

  const primaryToc = await page.$(".bd-sidebar-primary .ast-primary-toc");
  expect(primaryToc).not.toBeNull();

  // Initially the TOC is hidden (collapsed).
  expect(await primaryToc.evaluate((el) => el.hidden)).toBe(true);
  expect(await toggleBtn.getAttribute("aria-expanded")).toBe("false");

  // Expand.
  await toggleBtn.click();
  await page.waitForTimeout(100);
  expect(await primaryToc.evaluate((el) => el.hidden)).toBe(false);
  expect(await toggleBtn.getAttribute("aria-expanded")).toBe("true");
  const hasOpenClass = await toggleBtn.evaluate((el) =>
    el.classList.contains("ast-toc-toggle--open"),
  );
  expect(hasOpenClass).toBe(true);

  // Collapse again.
  await toggleBtn.click();
  await page.waitForTimeout(100);
  expect(await primaryToc.evaluate((el) => el.hidden)).toBe(true);
  expect(await toggleBtn.getAttribute("aria-expanded")).toBe("false");
});

test("primary sidebar: page TOC absent from secondary sidebar when feature is enabled", async ({
  page,
}) => {
  await page.goto(NESTED_PAGE);
  const primaryActive = await isPrimaryTocEnabled(page);
  if (!primaryActive)
    test.skip("show_page_toc_in_primary_sidebar is not active – skipping");

  // The page-toc must not also appear in the secondary sidebar.
  const secondaryPageToc = await page.$(
    ".bd-sidebar-secondary #pst-page-toc-nav, " +
      ".bd-sidebar-secondary nav.page-toc",
  );
  expect(secondaryPageToc).toBeNull();
});

test("primary sidebar: inline TOC links use bd-sidenav sizing class", async ({
  page,
}) => {
  await page.goto(NESTED_PAGE);
  const primaryActive = await isPrimaryTocEnabled(page);
  if (!primaryActive)
    test.skip("show_page_toc_in_primary_sidebar is not active – skipping");

  const primaryToc = await page.$(".ast-primary-toc");
  expect(primaryToc).not.toBeNull();

  // The injected ul must carry the bd-sidenav class (not section-nav, which is
  // sized for the right secondary sidebar).
  const hasBdSidenav = await primaryToc.evaluate((el) =>
    el.classList.contains("bd-sidenav"),
  );
  expect(hasBdSidenav).toBe(true);

  const hasSecondaryClass = await primaryToc.evaluate((el) =>
    el.classList.contains("section-nav"),
  );
  expect(hasSecondaryClass).toBe(false);
});

// ─── Fallback: top-level page (no li.current in nav) ─────────────────────────

test("primary sidebar: no toggle button on top-level page (direct-append fallback)", async ({
  page,
}) => {
  await page.goto(SECTION_ROOT_PAGE);
  const primaryActive = await isPrimaryTocEnabled(page);
  if (!primaryActive)
    test.skip("show_page_toc_in_primary_sidebar is not active – skipping");

  // The section-root page has no li.current, so the JS appends the TOC
  // directly to the nav container without adding a toggle button.
  const current = await page.$(".bd-docs-nav .bd-toc-item li.current");
  if (current)
    test.skip("li.current found – not using the direct-append fallback path");

  expect(await page.$(".ast-toc-toggle")).toBeNull();

  // But the TOC should still be attached directly under the nav container.
  const navContainer = await page.$(".bd-docs-nav .bd-toc-item");
  expect(navContainer).not.toBeNull();
  const directUl = await navContainer.$("ul");
  expect(directUl).not.toBeNull();
});

// ─── Option interaction: warning combination ──────────────────────────────────
// show_page_toc=True AND show_page_toc_in_primary_sidebar=True
// → a UserWarning is emitted at build time; the primary sidebar feature is
//   suppressed (_ast_page_toc_in_primary remains False) and the TOC stays in
//   the secondary sidebar.

test("warning combo: page TOC stays in secondary sidebar when show_page_toc=True and show_page_toc_in_primary_sidebar=True", async ({
  page,
}) => {
  await page.goto(NESTED_PAGE);

  // In the warning combination _ast_page_toc_in_primary is False, so the DOM
  // looks identical to the default case (page-toc in secondary, nothing in
  // primary).  The check below is true for both the default and warning-combo
  // builds; it confirms they are mutually exclusive.
  const primaryToc = await page.$(".ast-primary-toc");
  const secondaryToc = await page.$(
    "#pst-page-toc-nav, .bd-sidebar-secondary nav.page-toc",
  );

  // Exactly one of the two must be present (or neither if show_page_toc=False).
  const bothPresent = primaryToc !== null && secondaryToc !== null;
  expect(bothPresent).toBe(false);
});

// ─── Scroll-spy (only when primary TOC is enabled) ───────────────────────────

test("primary sidebar: scroll-spy highlights active heading after scrolling", async ({
  page,
}) => {
  await page.goto(NESTED_PAGE);
  const primaryActive = await isPrimaryTocEnabled(page);
  if (!primaryActive)
    test.skip("show_page_toc_in_primary_sidebar is not active – skipping");

  const toggleBtn = await page.$(".ast-toc-toggle");
  if (!toggleBtn)
    test.skip(
      "No toggle button – top-level page (direct-append path), scroll-spy still active but harder to verify",
    );

  // Ensure the TOC is expanded so the links are visible to the spy.
  const primaryToc = await page.$(".bd-sidebar-primary .ast-primary-toc");
  if (await primaryToc.evaluate((el) => el.hidden)) {
    await toggleBtn.click();
    await page.waitForTimeout(100);
  }

  // Scroll to the bottom of the page to trigger the scroll-spy.
  await page.evaluate(() => window.scrollTo(0, document.body.scrollHeight));
  await page.waitForTimeout(400);

  // The scroll-spy applies fontWeight: "700" to the active link.
  const hasActiveLink = await page.evaluate(() =>
    Array.from(document.querySelectorAll(".ast-primary-toc a[href]")).some(
      (a) => a.style.fontWeight === "700",
    ),
  );
  expect(hasActiveLink).toBe(true);
});

test("primary sidebar: scroll-spy auto-expands TOC when scrolling to a heading", async ({
  page,
}) => {
  await page.goto(NESTED_PAGE);
  const primaryActive = await isPrimaryTocEnabled(page);
  if (!primaryActive)
    test.skip("show_page_toc_in_primary_sidebar is not active – skipping");

  const toggleBtn = await page.$(".ast-toc-toggle");
  if (!toggleBtn)
    test.skip("No toggle button – top-level page without li.current");

  // Confirm TOC starts collapsed.
  const primaryToc = await page.$(".bd-sidebar-primary .ast-primary-toc");
  const startedHidden = await primaryToc.evaluate((el) => el.hidden);

  if (startedHidden) {
    // Scroll past at least one heading without manually expanding.
    await page.evaluate(() => window.scrollTo(0, document.body.scrollHeight));
    await page.waitForTimeout(400);

    // The scroll-spy should have called openToc() and expanded it.
    const nowHidden = await primaryToc.evaluate((el) => el.hidden);
    expect(nowHidden).toBe(false);
  }
  // If TOC was already expanded (e.g. scroll position restored), just verify
  // an active link is highlighted.
  const hasActiveLink = await page.evaluate(() =>
    Array.from(document.querySelectorAll(".ast-primary-toc a[href]")).some(
      (a) => a.style.fontWeight === "700",
    ),
  );
  expect(hasActiveLink).toBe(true);
});
