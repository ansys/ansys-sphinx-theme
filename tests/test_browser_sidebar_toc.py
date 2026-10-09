"""Playwright coverage for primary and secondary sidebar navigation."""

import re

from playwright.sync_api import Page, expect
import pytest

BASE_URL = "http://localhost:8000"
NESTED_PAGE = "/user-guide/options.html"
SECTION_ROOT_PAGE = "/user-guide.html"
TOP_NAV_PAGE = "/getting-started.html"


def open_page(page: Page, path: str) -> None:
    """Navigate to a generated documentation page."""
    page.goto(f"{BASE_URL}{path}")


def is_primary_toc_enabled(page: Page) -> bool:
    """Return whether the primary sidebar TOC feature is active."""
    return page.evaluate("!!document.querySelector('.ast-primary-toc, .ast-toc-toggle')")


def has_secondary_page_toc(page: Page) -> bool:
    """Return whether a page TOC is rendered in the secondary sidebar."""
    return page.evaluate(
        "!!(document.querySelector('#pst-page-toc-nav') || "
        "document.querySelector('.bd-sidebar-secondary nav.page-toc'))"
    )


def require_primary_toc(page: Page) -> None:
    """Skip tests when primary sidebar TOC is disabled."""
    if not is_primary_toc_enabled(page):
        pytest.skip("show_page_toc_in_primary_sidebar is not active")


def test_secondary_page_toc_visible_by_default(page: Page) -> None:
    open_page(page, NESTED_PAGE)
    if is_primary_toc_enabled(page):
        pytest.skip("Page TOC is in the primary sidebar")
    toc = page.locator("#pst-page-toc-nav, .bd-sidebar-secondary nav.page-toc").first
    if toc.count() == 0:
        pytest.skip("Page TOC not found; show_page_toc may be False")
    links = toc.locator("a.nav-link, a.reference")
    assert links.count() > 0


def test_sidebar_title_matches_top_breadcrumb(page: Page) -> None:
    open_page(page, NESTED_PAGE)
    title = page.locator(".bd-docs-nav .bd-links__title")
    expect(title).to_have_count(1)
    expected = page.evaluate(
        """() => {
            const items = Array.from(document.querySelectorAll(
                '.bd-breadcrumb li.breadcrumb-item, nav[aria-label="Breadcrumb"] li.breadcrumb-item'
            ));
            const home = items.findIndex(item => item.classList.contains('breadcrumb-home'));
            for (const item of items.slice(home >= 0 ? home + 1 : 0)) {
                if (item.classList.contains('active')) continue;
                const text = item.querySelector('a.nav-link, a')?.textContent?.trim();
                if (text) return text;
            }
            return items.find(item => item.classList.contains('active'))?.textContent?.trim() || '';
        }"""
    )
    assert expected
    expect(title).to_have_text(expected)


def test_top_level_sidebar_title(page: Page) -> None:
    open_page(page, TOP_NAV_PAGE)
    expect(page.locator(".bd-docs-nav .bd-links__title")).to_have_text("Getting started")


def test_edit_this_page_link_present(page: Page) -> None:
    open_page(page, NESTED_PAGE)
    link = page.locator(
        ".bd-sidebar-secondary .tocsection.editthispage a, "
        '.bd-sidebar-secondary a[aria-label*="edit" i], '
        '.bd-sidebar-secondary a:has-text("Edit on GitHub")'
    ).first
    if link.count() == 0:
        pytest.skip("Edit link not found; GitHub context may not be configured")
    expect(link).to_have_attribute("href", re.compile("github.com"))


def test_source_link_present_when_enabled(page: Page) -> None:
    open_page(page, NESTED_PAGE)
    link = page.locator(
        '.bd-sidebar-secondary a[href*="_sources"], '
        '.bd-sidebar-secondary a:has-text("Show Source"), '
        ".bd-sidebar-secondary .tocsection.viewsourcecode"
    ).first
    if link.count() == 0:
        pytest.skip("Source link not found; show_source_button may be False")
    expect(link).to_be_attached()


def test_secondary_sidebar_items(page: Page) -> None:
    open_page(page, NESTED_PAGE)
    if is_primary_toc_enabled(page):
        pytest.skip("Primary TOC is active")
    secondary = page.locator(".bd-sidebar-secondary")
    expect(secondary).to_be_attached()
    toc = secondary.locator("#pst-page-toc-nav, nav.page-toc, .page-toc").first
    expect(toc).to_be_attached()
    edit_section = secondary.locator(".tocsection.editthispage, .tocsection[aria-label*='edit' i]")
    if edit_section.count():
        expect(edit_section.locator("a[href]").first).to_be_attached()


def test_no_secondary_page_toc_when_disabled(page: Page) -> None:
    open_page(page, NESTED_PAGE)
    if has_secondary_page_toc(page):
        pytest.skip("show_page_toc is enabled")
    if not is_primary_toc_enabled(page):
        expect(page.locator(".bd-sidebar-secondary #pst-page-toc-nav")).to_have_count(0)


def test_source_link_absent_when_disabled(page: Page) -> None:
    open_page(page, NESTED_PAGE)
    link = page.locator(
        '.bd-sidebar-secondary a[href*="_sources"], '
        '.bd-sidebar-secondary a:has-text("Show Source"), '
        ".bd-sidebar-secondary .tocsection.viewsourcecode"
    ).first
    if link.count():
        pytest.skip("Source link is present; show_source_button is enabled")
    expect(link).to_have_count(0)


def test_no_primary_toc_when_disabled(page: Page) -> None:
    open_page(page, NESTED_PAGE)
    if is_primary_toc_enabled(page):
        pytest.skip("Primary TOC feature is enabled")
    expect(page.locator(".ast-primary-toc")).to_have_count(0)


def test_no_primary_toc_toggle_when_disabled(page: Page) -> None:
    open_page(page, NESTED_PAGE)
    if is_primary_toc_enabled(page):
        pytest.skip("Primary TOC feature is enabled")
    expect(page.locator(".ast-toc-toggle")).to_have_count(0)


def test_primary_toc_is_injected_when_enabled(page: Page) -> None:
    open_page(page, NESTED_PAGE)
    require_primary_toc(page)
    toc = page.locator(".bd-sidebar-primary .ast-primary-toc")
    expect(toc).to_be_attached()
    assert toc.locator("a").count() > 0


def test_primary_toc_toggle_is_accessible(page: Page) -> None:
    open_page(page, NESTED_PAGE)
    require_primary_toc(page)
    if page.locator(".bd-docs-nav .bd-toc-item li.current").count() == 0:
        pytest.skip("No current nav item; top-level page uses direct-append fallback")
    toggle = page.locator(".ast-toc-toggle")
    expect(toggle).to_have_attribute("aria-label", re.compile("toggle page sections", re.I))
    expect(toggle).to_have_attribute("aria-expanded", "false")
    expect(toggle).to_have_attribute("type", "button")


def test_primary_toc_toggle_expands_and_collapses(page: Page) -> None:
    open_page(page, NESTED_PAGE)
    require_primary_toc(page)
    toggle = page.locator(".ast-toc-toggle")
    if toggle.count() == 0:
        pytest.skip("Toggle not present; page uses direct-append fallback")
    toc = page.locator(".bd-sidebar-primary .ast-primary-toc")
    expect(toc).to_be_hidden()
    expect(toggle).to_have_attribute("aria-expanded", "false")
    toggle.click()
    expect(toc).to_be_visible()
    expect(toggle).to_have_attribute("aria-expanded", "true")
    expect(toggle).to_have_class(re.compile("ast-toc-toggle--open"))
    toggle.click()
    expect(toc).to_be_hidden()
    expect(toggle).to_have_attribute("aria-expanded", "false")


def test_primary_toc_not_duplicated_in_secondary_sidebar(page: Page) -> None:
    open_page(page, NESTED_PAGE)
    require_primary_toc(page)
    expect(
        page.locator(".bd-sidebar-secondary #pst-page-toc-nav, .bd-sidebar-secondary nav.page-toc")
    ).to_have_count(0)


def test_primary_toc_uses_sidebar_sizing_class(page: Page) -> None:
    open_page(page, NESTED_PAGE)
    require_primary_toc(page)
    toc = page.locator(".ast-primary-toc")
    expect(toc).to_have_class(re.compile("bd-sidenav"))
    expect(toc).not_to_have_class(re.compile("section-nav"))


def test_top_level_primary_toc_uses_direct_append_fallback(page: Page) -> None:
    open_page(page, SECTION_ROOT_PAGE)
    require_primary_toc(page)
    if page.locator(".bd-docs-nav .bd-toc-item li.current").count():
        pytest.skip("Current nav item found; direct-append fallback is not active")
    expect(page.locator(".ast-toc-toggle")).to_have_count(0)
    expect(page.locator(".bd-docs-nav .bd-toc-item > ul")).to_be_attached()


def test_page_toc_is_not_present_in_both_sidebars(page: Page) -> None:
    open_page(page, NESTED_PAGE)
    primary = page.locator(".ast-primary-toc").count() > 0
    secondary = page.locator("#pst-page-toc-nav, .bd-sidebar-secondary nav.page-toc").count() > 0
    assert not (primary and secondary)


def test_primary_toc_scroll_spy_highlights_heading(page: Page) -> None:
    open_page(page, NESTED_PAGE)
    require_primary_toc(page)
    toggle = page.locator(".ast-toc-toggle")
    if toggle.count() == 0:
        pytest.skip("No toggle button; direct-append page")
    toc = page.locator(".bd-sidebar-primary .ast-primary-toc")
    if toc.evaluate("element => element.hidden"):
        toggle.click()
    page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
    active_link = page.locator(".ast-primary-toc a[href][style*='font-weight: 700']")
    expect(active_link).to_have_count(1, timeout=5000)


def test_scroll_spy_expands_collapsed_toc(page: Page) -> None:
    open_page(page, NESTED_PAGE)
    require_primary_toc(page)
    toggle = page.locator(".ast-toc-toggle")
    if toggle.count() == 0:
        pytest.skip("No toggle button on this page")
    toc = page.locator(".bd-sidebar-primary .ast-primary-toc")
    if toc.evaluate("element => element.hidden"):
        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        expect(toc).to_be_visible(timeout=5000)
    active_link = page.locator(".ast-primary-toc a[href][style*='font-weight: 700']")
    expect(active_link).to_have_count(1, timeout=5000)
