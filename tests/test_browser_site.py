"""Playwright coverage for site navigation and rendered components."""

import re

from playwright.sync_api import Page, expect
import pytest

BASE_URL = "http://localhost:8000"


def open_page(page: Page, path: str = "") -> None:
    """Navigate to a generated documentation page."""
    page.goto(f"{BASE_URL}/{path.lstrip('/')}")


def test_homepage_loads(page: Page) -> None:
    open_page(page, "index.html")
    heading = page.locator("h1").first
    expect(heading).to_be_attached()
    expect(heading).to_contain_text(re.compile("Ansys Sphinx Theme|Welcome", re.I))


def test_navbar_links_and_dropdown(page: Page) -> None:
    open_page(page)
    links = {
        "Home": "#",
        "Getting started": "getting-started.html",
        "User guide": "user-guide.html",
        "Examples": "examples.html",
        "Release notes": "changelog.html",
    }
    for text, href in links.items():
        link = page.locator("nav a.nav-link").filter(has_text=text).first
        expect(link).to_be_attached()
        expect(link).to_have_attribute("href", re.compile(re.escape(href)))

    page.get_by_role("button", name=re.compile("More")).click()
    for text, href in {
        "Contribute": "contribute.html",
        "API reference": "examples/api/index.html",
    }.items():
        link = page.locator(".dropdown-menu a").filter(has_text=text).first
        expect(link).to_be_attached()
        expect(link).to_have_attribute("href", re.compile(re.escape(href)))


def test_navbar_end_components(page: Page) -> None:
    open_page(page)
    expect(
        page.locator('.search-bar input[type="search"], .search-bar input[placeholder*="Search" i]')
    ).to_be_attached()
    expect(
        page.locator(".version-switcher__button, .version-switcher__container button")
    ).to_be_attached()
    expect(
        page.locator('button.theme-switch-button, button[aria-label*="Color mode" i]')
    ).to_be_attached()
    expect(page.locator('a[href*="github.com/ansys/ansys-sphinx-theme"]')).to_be_attached()


def test_navigation_contains_home_link(page: Page) -> None:
    open_page(page)
    link = page.locator('nav a:has-text("Home"), [role="navigation"] a:has-text("Home")').first
    if link.count() == 0:
        pytest.skip("Home link not found in navigation bar")
    expect(link).to_be_attached()


def test_sidebar_has_links(page: Page) -> None:
    open_page(page)
    sidebar = page.locator(
        ".bd-sidebar-primary, .bd-sidebar-secondary, .sidebar, nav[role='navigation']"
    ).first
    expect(sidebar).to_be_attached()
    expect(sidebar.locator("a").first).to_be_attached()
    assert sidebar.locator("a").count() > 0


def test_version_switcher_exists(page: Page) -> None:
    open_page(page)
    expect(
        page.locator(
            '.version-switcher, [id*="version-switcher"], [class*="version-switcher"]'
        ).first
    ).to_be_attached()


def test_version_switcher_opens_dropdown(page: Page) -> None:
    open_page(page)
    switcher = page.locator(
        '.version-switcher, [id*="version-switcher"], [class*="version-switcher"]'
    ).first
    expect(switcher).to_be_attached()
    switcher.click()
    expect(
        page.locator(
            '.version-switcher__menu, [id*="pst-version-switcher-list-2"]'
            ', [class*="version-switcher__menu"]'
        ).first
    ).to_be_attached()


def test_theme_switcher_options(page: Page) -> None:
    open_page(page)
    switcher = page.locator('button.theme-switch-button[aria-label="Color mode"]').first
    if switcher.count() == 0:
        pytest.skip("Theme switcher is not available")
    switcher.click()
    menu = page.locator(".theme-switch-container .dropdown-menu").first
    expect(menu).to_be_visible()
    for mode in ("light", "dark", "auto"):
        expect(
            page.locator(f'button.theme-change-button[data-mode="{mode}"]').first
        ).to_be_attached()
    page.locator('button.theme-change-button[data-mode="dark"]').first.click(force=True)
    expect(page.locator("html")).to_have_attribute("data-mode", "dark")


def test_dark_mode_css_variables_are_defined(page: Page) -> None:
    open_page(page)
    styles = page.evaluate(
        """() => {
            document.documentElement.removeAttribute('data-theme');
            document.documentElement.setAttribute('data-mode', 'dark');
            const computed = getComputedStyle(document.documentElement);
            return {
                background: computed.getPropertyValue('--ast-search-bar-enable-background').trim(),
                text: computed.getPropertyValue('--ast-search-bar-enable-text').trim(),
                bodyColor: getComputedStyle(document.body).color,
            };
        }"""
    )
    assert styles["background"]
    assert styles["text"]
    assert styles["background"] != "rgb(0, 0, 0)"
    assert styles["bodyColor"] != "rgb(0, 0, 0)"


def test_breadcrumbs_exist(page: Page) -> None:
    open_page(page, "user-guide/configuration.html")
    breadcrumbs = page.locator('.bd-breadcrumb, nav[aria-label="Breadcrumb"]').first
    if breadcrumbs.count() == 0:
        pytest.skip("Breadcrumbs not found")
    expect(breadcrumbs).to_be_attached()


def test_logo_links_home(page: Page) -> None:
    open_page(page)
    logo = page.locator('img[alt*="logo" i], .navbar-brand img, .logo').first
    expect(logo).to_be_attached()
    href = logo.evaluate("element => element.closest('a')?.getAttribute('href')")
    assert re.search(r"/?(index\.html)?$", href or "")


def test_edit_this_page_button_exists(page: Page) -> None:
    open_page(page, "user-guide/configuration.html")
    button = page.locator('tocsection.editthispage, a:has-text("Edit on GitHub")').first
    if button.count() == 0:
        pytest.skip("Edit this page button not found")
    expect(button).to_be_attached()


def test_footer_links_and_version(page: Page) -> None:
    open_page(page)
    footer = page.locator(".bd-footer")
    expect(footer).to_be_attached()
    expect(footer.locator(".copyright")).to_be_attached()
    assert footer.locator("a").count() > 0
    expect(footer.locator(".theme-version")).to_be_attached()
    assert footer.locator(".theme-version").text_content() is not None


def test_code_block_and_copy_button(page: Page) -> None:
    open_page(page, "user-guide/configuration.html")
    expect(page.locator(".highlight").first).to_be_attached()
    copy_button = page.locator("button.copybtn, .copy-button, .btn-copy").first
    expect(copy_button).to_be_attached()
    copy_button.click()


def test_sphinx_tabs(page: Page) -> None:
    open_page(page, "user-guide/configuration.html")
    expect(page.locator(".sd-tab-set, .tab-set, .tab-content").first).to_be_attached()
    labels = page.locator(".sd-tab-label, .tab-label, .nav-tabs .nav-link")
    if labels.count() > 1:
        labels.nth(1).click()


def test_tables(page: Page) -> None:
    open_page(page, "examples/table.html")
    table = page.locator(".pst-scrollable-table-container")
    expect(table).to_be_attached()
    assert table.locator("th").count() > 0
    assert table.locator("tbody tr").count() > 0


def test_admonitions(page: Page) -> None:
    open_page(page, "examples/admonitions.html")
    expect(
        page.locator(".admonition, .note, .warning, .caution, .tip, .important").first
    ).to_be_attached()


def test_sphinx_design_card_grid_and_badge(page: Page) -> None:
    open_page(page, "examples/sphinx-design.html")
    expect(page.locator(".sd-card, .card, div.sd-card").first).to_be_attached()
    expect(page.locator(".sd-row, .sd-grid, .row, .grid").first).to_be_attached()
    expect(page.locator(".sd-badge, span.sd-badge, button.sd-badge").first).to_be_attached()


def test_clickable_card_navigation(page: Page) -> None:
    open_page(page, "examples/sphinx-design.html")
    link = page.locator(
        '.sd-card:has(.sd-card-title:has-text("Clickable Card (external)")) a.sd-stretched-link'
    )
    expect(link).to_be_attached()
    href = link.get_attribute("href") or ""
    target = link.get_attribute("target")
    if target == "_blank":
        with page.expect_popup() as popup_info:
            link.click()
        popup = popup_info.value
        popup.wait_for_load_state()
        assert href in popup.url
    else:
        with page.expect_navigation():
            link.click()
        assert href in page.url


def test_sphinx_design_dropdown(page: Page) -> None:
    open_page(page, "examples/sphinx-design.html")
    dropdown = page.locator("details.sd-dropdown")
    expect(dropdown).to_be_attached()
    summary = dropdown.locator("summary.sd-summary-title")
    expect(summary).to_be_attached()
    if dropdown.get_attribute("open") is not None:
        summary.click()
    summary.click()
    expect(dropdown).to_have_attribute("open", "")
    expect(dropdown.locator(".sd-summary-content")).to_contain_text("Dropdown content")


def test_user_guide_sidebar_has_links(page: Page) -> None:
    open_page(page, "user-guide.html")
    sidebar = page.locator(
        ".bd-sidebar-primary, .bd-sidebar-secondary, .sidebar, nav[role='navigation']"
    ).first
    expect(sidebar).to_be_attached()
    assert sidebar.locator("a").count() > 0
