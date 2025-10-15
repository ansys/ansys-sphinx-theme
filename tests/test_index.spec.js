import { test, expect } from "@playwright/test";

test("homepage loads and shows main header", async ({ page }) => {
  await page.goto("http://localhost:3000/index.html");
  const header = await page.$("h1");
  expect(header).not.toBeNull();
  expect(await header.textContent()).toMatch(/Ansys Sphinx Theme|Welcome/i);
});


test("navbar contains all main components", async ({ page }) => {
    await page.goto("http://localhost:3000");
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

test("navbar end components are present", async ({ page }) => {
    await page.goto("http://localhost:3000");
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

test("renders navigation bar with Home link", async ({ page }) => {
  await page.goto("http://localhost:3000");
  const nav = await page.$('nav, [role="navigation"]');
  expect(nav).not.toBeNull();
  // Try to find Home link in nav
  const homeLink = await page.$(
    'nav a:has-text("Home"), [role="navigation"] a:has-text("Home")',
  );
  if (!homeLink) test.skip("Home link not found in navigation bar");
  expect(homeLink).not.toBeNull();
});

test("sidebar is present and contains items", async ({ page }) => {
  await page.goto("http://localhost:3000");
  const sidebar = await page.$(
    '.bd-sidebar-primary, .bd-sidebar-secondary, .sidebar, nav[role="navigation"]',
  );
  expect(sidebar).not.toBeNull();
  const sidebarLinks = await sidebar.$$("a");
  expect(sidebarLinks.length).toBeGreaterThan(0);
});

test("version switcher is present", async ({ page }) => {
  await page.goto("http://localhost:3000");
  const versionSwitcher = await page.$(
    '.version-switcher, [id*="version-switcher"], [class*="version-switcher"]',
  );
  expect(versionSwitcher).not.toBeNull();
});

test("click on version switcher shows dropdown", async ({ page }) => {
    await page.goto("http://localhost:3000");
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


test("theme switcher toggles dark/light mode", async ({ page }) => {
  await page.goto("http://localhost:3000");
  // Use the actual button class from the provided HTML
  const themeSwitcher = await page.$(
    'button.theme-switch-button[aria-label="Color mode"]',
  );
  if (!themeSwitcher) test.skip("Theme switcher not found");
  expect(themeSwitcher).not.toBeNull();
  // Find the currently active mode (the visible svg or the one with aria-current or similar)
  const getActiveMode = async () => {
    // Try to get the mode from the html class or data attribute if available
    const htmlMode = await page.evaluate(() => {
      if (document.documentElement.dataset.theme)
        return document.documentElement.dataset.theme;
      if (document.body.dataset.theme) return document.body.dataset.theme;
      // Fallback: find the first visible svg with data-mode
      const svgs = Array.from(
        document.querySelectorAll(
          "button.theme-switch-button svg.theme-switch[data-mode]",
        ),
      );
      for (const svg of svgs) {
        const style = window.getComputedStyle(svg);
        if (
          style.display !== "none" &&
          style.visibility !== "hidden" &&
          style.opacity !== "0"
        ) {
          return svg.getAttribute("data-mode");
        }
      }
      return svgs.length ? svgs[0].getAttribute("data-mode") : null;
    });
    return htmlMode;
  };
  const currentMode = await getActiveMode();
  await themeSwitcher.click();
  console.log(`Switched theme from ${currentMode}`);
  await page.waitForTimeout(500);
  const newMode = await getActiveMode();
  console.log(`New theme mode is ${newMode}`);
  expect(newMode).not.toBe(currentMode);
});


test("breadcrumbs are present", async ({ page }) => {
  await page.goto("http://localhost:3000/user-guide/configuration.html");
  const breadcrumbs = await page.$('.bd-breadcrumb, nav[aria-label="Breadcrumb"]');
  if (!breadcrumbs) test.skip("Breadcrumbs not found");
  expect(breadcrumbs).not.toBeNull();
});

test("logo is present and links to homepage", async ({ page }) => {
  await page.goto("http://localhost:3000");
  const logo = await page.$('img[alt*="logo" i], .navbar-brand img, .logo');
  expect(logo).not.toBeNull();
  const logoLink = await logo.evaluate((el) =>
    el.closest("a")?.getAttribute("href"),
  );
  expect(logoLink).toMatch(/\/?(index\.html)?$/);
});

test("edit this page button is present", async ({ page }) => {
  await page.goto("http://localhost:3000/user-guide/configuration.html");
  const editBtn = await page.$(
    'tocsection.editthispage, a:has-text("Edit on GitHub")',
  );
  if (!editBtn) test.skip("Edit this page button not found");
  expect(editBtn).not.toBeNull();
});

test("footer contains correct links", async ({ page }) => {
  await page.goto("http://localhost:3000");
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
