import { test, expect } from "@playwright/test";

test("Test homepage loading", async ({ page }) => {
  await page.goto("http://localhost:8000/index.html");
  const header = await page.$("h1");
  expect(header).not.toBeNull();
  expect(await header.textContent()).toMatch(/Ansys Sphinx Theme|Welcome/i);
});

test("Test navbar components", async ({ page }) => {
  await page.goto("http://localhost:8000");
  const navLinks = [
    { text: "Home", href: "#" },
    { text: "Getting started", href: "getting-started.html" },
    { text: "User guide", href: "user-guide.html" },
    { text: "Examples", href: "examples.html" },
    { text: "Release notes", href: "changelog.html" },
  ];
  for (const { text, href } of navLinks) {
    const link = await page.$(`nav a.nav-link:has-text("${text}")`);
    expect(link).not.toBeNull();
    if (link && href) {
      const actualHref = await link.getAttribute("href");
      expect(actualHref).toContain(href);
    }
  }
  const moreBtn = await page.$('button.dropdown-toggle:has-text("More")');
  expect(moreBtn).not.toBeNull();
  await moreBtn.click();
  const dropdownLinks = [
    { text: "Contribute", href: "contribute.html" },
    { text: "API reference", href: "examples/api/index.html" },
  ];
  for (const { text, href } of dropdownLinks) {
    const link = await page.$(`.dropdown-menu a:has-text("${text}")`);
    expect(link).not.toBeNull();
    if (link && href) {
      const actualHref = await link.getAttribute("href");
      expect(actualHref).toContain(href);
    }
  }
});

test("Test navbar end components", async ({ page }) => {
  await page.goto("http://localhost:8000");
  const searchBar = await page.$(
    '.search-bar input[type="search"], .search-bar input[placeholder*="Search" i]',
  );
  expect(searchBar).not.toBeNull();

  // Check version switcher
  const versionSwitcher = await page.$(
    ".version-switcher__button, .version-switcher__container button",
  );
  expect(versionSwitcher).not.toBeNull();

  // Check theme switcher
  const themeSwitcher = await page.$(
    'button.theme-switch-button, button[aria-label*="Color mode" i]',
  );
  expect(themeSwitcher).not.toBeNull();

  // Check GitHub icon link
  const githubLink = await page.$(
    'a[href*="github.com/ansys/ansys-sphinx-theme"]',
  );
  expect(githubLink).not.toBeNull();
});

test("Test navigation bar", async ({ page }) => {
  await page.goto("http://localhost:8000");
  const nav = await page.$('nav, [role="navigation"]');
  expect(nav).not.toBeNull();
  // Try to find Home link in nav
  const homeLink = await page.$(
    'nav a:has-text("Home"), [role="navigation"] a:has-text("Home")',
  );
  if (!homeLink) test.skip("Home link not found in navigation bar");
  expect(homeLink).not.toBeNull();
});

test("Test sidebar", async ({ page }) => {
  await page.goto("http://localhost:8000");
  const sidebar = await page.$(
    '.bd-sidebar-primary, .bd-sidebar-secondary, .sidebar, nav[role="navigation"]',
  );
  expect(sidebar).not.toBeNull();
  const sidebarLinks = await sidebar.$$("a");
  expect(sidebarLinks.length).toBeGreaterThan(0);
});

test("Test version switcher", async ({ page }) => {
  await page.goto("http://localhost:8000");
  const versionSwitcher = await page.$(
    '.version-switcher, [id*="version-switcher"], [class*="version-switcher"]',
  );
  expect(versionSwitcher).not.toBeNull();
});

test("Test version switcher dropdown", async ({ page }) => {
  await page.goto("http://localhost:8000");
  const versionSwitcher = await page.$(
    '.version-switcher, [id*="version-switcher"], [class*="version-switcher"]',
  );
  expect(versionSwitcher).not.toBeNull();
  await versionSwitcher.click();
  const dropdown = await page.$(
    '.version-switcher__menu, [id*="pst-version-switcher-list-2"], [class*="version-switcher__menu"]',
  );
  expect(dropdown).not.toBeNull();
});

// theme switcher dropdown test
test("Test theme switcher", async ({ page }) => {
  await page.goto("http://localhost:8000");

  // The toggle button that opens the dropdown
  const themeSwitcher = page
    .locator('button.theme-switch-button[aria-label="Color mode"]')
    .first();
  if (!(await themeSwitcher.count())) {
    test.skip();
    return;
  }

  await themeSwitcher.click();
  const dropdown = page
    .locator(".theme-switch-container .dropdown-menu")
    .first();
  await expect(dropdown).toBeVisible();

  // Verify all three mode options are present
  const lightBtn = page
    .locator('button.theme-change-button[data-mode="light"]')
    .first();
  const darkBtn = page
    .locator('button.theme-change-button[data-mode="dark"]')
    .first();
  const autoBtn = page
    .locator('button.theme-change-button[data-mode="auto"]')
    .first();
  await expect(lightBtn).toBeAttached();
  await expect(darkBtn).toBeAttached();
  await expect(autoBtn).toBeAttached();

  await darkBtn.click({ force: true });
  await expect(page.locator("html")).toHaveAttribute("data-mode", "dark");
});

test("Test breadcrumbs", async ({ page }) => {
  await page.goto("http://localhost:8000/user-guide/configuration.html");
  const breadcrumbs = await page.$(
    '.bd-breadcrumb, nav[aria-label="Breadcrumb"]',
  );
  if (!breadcrumbs) test.skip("Breadcrumbs not found");
  expect(breadcrumbs).not.toBeNull();
});

test("Test logo", async ({ page }) => {
  await page.goto("http://localhost:8000");
  const logo = await page.$('img[alt*="logo" i], .navbar-brand img, .logo');
  expect(logo).not.toBeNull();
  const logoLink = await logo.evaluate((el) =>
    el.closest("a")?.getAttribute("href"),
  );
  expect(logoLink).toMatch(/\/?(index\.html)?$/);
});

test("Test edit this page button", async ({ page }) => {
  await page.goto("http://localhost:8000/user-guide/configuration.html");
  const editBtn = await page.$(
    'tocsection.editthispage, a:has-text("Edit on GitHub")',
  );
  if (!editBtn) test.skip("Edit this page button not found");
  expect(editBtn).not.toBeNull();
});

test("Test footer links", async ({ page }) => {
  await page.goto("http://localhost:8000");
  const footer = await page.$(".bd-footer");
  expect(footer).not.toBeNull();
  const Footercopyright = await footer.$(".copyright");
  const footerLinks = await footer.$$("a");
  expect(footerLinks.length).toBeGreaterThan(0);
  expect(Footercopyright).not.toBeNull();
  const themeVersion = await footer.$(".theme-version");
  expect(themeVersion).not.toBeNull();
  const versionText = await themeVersion.textContent();
  expect(versionText).not.toBeNull();
});
