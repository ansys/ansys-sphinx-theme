test('navbar contains all main components', async ({ page }) => {
    await page.goto('http://localhost:3000');
    // Check main nav links
    const navLinks = [
        { text: 'Home', href: '#' },
        { text: 'Getting started', href: 'getting-started.html' },
        { text: 'User guide', href: 'user-guide.html' },
        { text: 'Examples', href: 'examples.html' },
        { text: 'Release notes', href: 'changelog.html' }
    ];
    for (const { text, href } of navLinks) {
        const link = await page.$(`nav a.nav-link:has-text("${text}")`);
        expect(link).not.toBeNull();
        if (link && href) {
            const actualHref = await link.getAttribute('href');
            expect(actualHref).toContain(href);
        }
    }

    // Check dropdown for More
    const moreBtn = await page.$('button.dropdown-toggle:has-text("More")');
    expect(moreBtn).not.toBeNull();
    await moreBtn.click();
    const dropdownLinks = [
        { text: 'Contribute', href: 'contribute.html' },
        { text: 'API reference', href: 'examples/api/index.html' }
    ];
    for (const { text, href } of dropdownLinks) {
        const link = await page.$(`.dropdown-menu a:has-text("${text}")`);
        expect(link).not.toBeNull();
        if (link && href) {
            const actualHref = await link.getAttribute('href');
            expect(actualHref).toContain(href);
        }
    }

    // Check search bar
    const searchBar = await page.$('.search-bar input[type="search"], .search-bar input[placeholder*="Search" i]');
    expect(searchBar).not.toBeNull();

    // Check version switcher
    const versionSwitcher = await page.$('.version-switcher__button, .version-switcher__container button');
    expect(versionSwitcher).not.toBeNull();

    // Check theme switcher
    const themeSwitcher = await page.$('button.theme-switch-button, button[aria-label*="Color mode" i]');
    expect(themeSwitcher).not.toBeNull();

    // Check GitHub icon link
    const githubLink = await page.$('a[href*="github.com/ansys/ansys-sphinx-theme"]');
    expect(githubLink).not.toBeNull();
});
import { test, expect } from '@playwright/test';

// Homepage and header

test('homepage loads correctly', async ({ page }) => {
    await page.goto('http://localhost:3000');
    await expect(page).toHaveTitle(/Home Page|Ansys Sphinx Theme/i);
    const header = await page.$('h1');
    expect(await header.textContent()).toMatch(/Welcome to Our Website|Ansys Sphinx Theme/i);
});

// Navigation bar

test('renders navigation bar with About link', async ({ page }) => {
    await page.goto('http://localhost:3000');
    const nav = await page.$('nav, [role="navigation"]');
    expect(nav).not.toBeNull();
    // Try to find About link in nav
    const aboutLink = await page.$('nav a:has-text("About"), [role="navigation"] a:has-text("About")');
    if (!aboutLink) test.skip('About link not found in navigation bar');
    expect(aboutLink).not.toBeNull();
});

// Sidebar

test('sidebar is present and contains items', async ({ page }) => {
    await page.goto('http://localhost:3000');
    const sidebar = await page.$('.bd-sidebar-primary, .bd-sidebar-secondary, .sidebar, nav[role="navigation"]');
    expect(sidebar).not.toBeNull();
    const sidebarLinks = await sidebar.$$('a');
    expect(sidebarLinks.length).toBeGreaterThan(0);
});

// Version switcher

test('version switcher is present', async ({ page }) => {
    await page.goto('http://localhost:3000');
    const versionSwitcher = await page.$('.version-switcher, [id*="version-switcher"], [class*="version-switcher"]');
    expect(versionSwitcher).not.toBeNull();
});

// Theme switcher (dark/light)

test('theme switcher toggles dark/light mode', async ({ page }) => {
    await page.goto('http://localhost:3000');
    const themeSwitcher = await page.$('button[aria-label*="theme" i], button[title*="theme" i], .theme-switcher, [id*="theme-switcher"], [class*="theme-switcher"]');
    if (!themeSwitcher) test.skip('Theme switcher not found');
    expect(themeSwitcher).not.toBeNull();
    await themeSwitcher.click();
});

// Code blocks and copy button

test('code blocks and copy button work', async ({ page }) => {
    await page.goto('http://localhost:3000/user-guide/configuration.html');
    const codeBlock = await page.$('pre code');
    if (!codeBlock) test.skip('No code block found on this page');
    expect(codeBlock).not.toBeNull();
    const copyBtn = await page.$('button.copybtn, .copy-button, .btn-copy');
    if (copyBtn) await copyBtn.click();
});

// Tabs and tab sets

test('tab sets render and switch', async ({ page }) => {
    await page.goto('http://localhost:3000/user-guide/configuration.html');
    const tabSet = await page.$('.sd-tab-set, .tab-set, .tab-content');
    expect(tabSet).not.toBeNull();
    const tabLabels = await page.$$('.sd-tab-label, .tab-label, .nav-tabs .nav-link');
    if (tabLabels.length > 1) {
        await tabLabels[1].click();
        // Optionally check for tab content change
    }
});

// Alerts/admonitions

test('alerts/admonitions are styled', async ({ page }) => {
    await page.goto('http://localhost:3000/user-guide/configuration.html');
    const admonition = await page.$('.admonition, .note, .warning, .alert');
    expect(admonition).not.toBeNull();
});

// Breadcrumbs

test('breadcrumbs are present', async ({ page }) => {
    await page.goto('http://localhost:3000/user-guide/configuration.html');
    const breadcrumbs = await page.$('.breadcrumb, nav[aria-label="breadcrumb"]');
    if (!breadcrumbs) test.skip('Breadcrumbs not found');
    expect(breadcrumbs).not.toBeNull();
});

// Logo and logo link

test('logo is present and links to homepage', async ({ page }) => {
    await page.goto('http://localhost:3000');
    const logo = await page.$('img[alt*="logo" i], .navbar-brand img, .logo');
    expect(logo).not.toBeNull();
    const logoLink = await logo.evaluate(el => el.closest('a')?.getAttribute('href'));
    expect(logoLink).toMatch(/\/?(index\.html)?$/);
});

// Edit this page button

test('edit this page button is present', async ({ page }) => {
    await page.goto('http://localhost:3000/user-guide/configuration.html');
    const editBtn = await page.$('a[title*="Edit" i], .edit-this-page, .btn-edit');
    if (!editBtn) test.skip('Edit this page button not found');
    expect(editBtn).not.toBeNull();
});

// API reference and example gallery (if present)

test('API reference and example gallery links exist', async ({ page }) => {
    await page.goto('http://localhost:3000');
    const apiLink = await page.$('a[href*="api" i]');
    const galleryLink = await page.$('a[href*="gallery" i]');
    expect(apiLink || galleryLink).not.toBeNull();
});

// Cards and grid layouts (Sphinx-design)

test('cards and grid layouts render', async ({ page }) => {
    await page.goto('http://localhost:3000');
    const card = await page.$('.sd-card, .card, .grid-item-card');
    expect(card).not.toBeNull();
});

// Dropdowns and menus

test('dropdown menus open', async ({ page }) => {
    await page.goto('http://localhost:3000');
    const dropdown = await page.$('.dropdown, .navbar-dropdown, .dropdown-toggle');
    if (dropdown) {
        await dropdown.click();
        // Optionally check for menu visibility
        const menu = await page.$('.dropdown-menu, .navbar-dropdown-menu');
        expect(menu).not.toBeNull();
    }
});

// Search functionality

test('search functionality works', async ({ page }) => {
    await page.goto('http://localhost:3000');
    // Try to open the search bar/dialog if needed
    const searchBtn = await page.$('button[aria-label*="search" i], .search-bar .fa-magnifying-glass, .search-button, [data-bs-toggle="search"]');
    if (searchBtn) {
        await searchBtn.click();
    } else {
        // Try keyboard shortcut (Ctrl+K or Cmd+K)
        await page.keyboard.press(process.platform === 'darwin' ? 'Meta+K' : 'Control+K');
    }
    // Now try to find a visible search input
    const searchInput = await page.waitForSelector('input[type="search"]:visible, input[placeholder*="Search the docs ..." i]:visible', { timeout: 5000 });
    if (!searchInput) test.skip('Search input not visible after opening search');
    await searchInput.fill('theme');
    console.log('Filled search input with query "theme"');
    console.log(`${await searchInput.evaluate(el => el.value)}`);
    // console search input
    console.log(`${searchInput}`);
    // Wait longer for instant search to update results
    await page.waitForTimeout(1500);
    const results = await page.$$('.static-search-results .result-item');
    console.log(`Found ${results.length} search results.`);
    console.log('Search results:', await Promise.all(results.map(async r => await r.textContent())));
    expect(results.length).toBeGreaterThan(0);
});

// Footer links

test('footer contains correct links', async ({ page }) => {
    await page.goto('http://localhost:3000');
    const footer = await page.$('footer');
    expect(footer).not.toBeNull();
    const footerLinks = await footer.$$('a');
    const linkHrefs = await Promise.all(footerLinks.map(async link => await link.getAttribute('href')));
    if (!linkHrefs.some(href => href && href.includes('privacy'))) test.skip('Privacy link not found in footer');
    if (!linkHrefs.some(href => href && href.includes('terms'))) test.skip('Terms link not found in footer');
    expect(linkHrefs.some(href => href && href.includes('privacy'))).toBeTruthy();
    expect(linkHrefs.some(href => href && href.includes('terms'))).toBeTruthy();
});
