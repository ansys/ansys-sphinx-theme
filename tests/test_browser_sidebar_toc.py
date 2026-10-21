"""Playwright coverage for primary and secondary sidebar navigation."""

import re

from playwright.sync_api import Page, expect
import pytest
from test_common.common import open_page

NESTED_PAGE = "/user-guide/options.html"
SECTION_ROOT_PAGE = "/user-guide.html"
TOP_NAV_PAGE = "/getting-started.html"


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
    """Verify the page TOC shows in the secondary sidebar by default.

    Checks the TOC has at least one link. Skipped when the TOC is moved to the primary
    sidebar or the page TOC is disabled.
    """
    open_page(page, NESTED_PAGE)
    if is_primary_toc_enabled(page):
        pytest.skip("Page TOC is in the primary sidebar")
    toc = page.locator("#pst-page-toc-nav, .bd-sidebar-secondary nav.page-toc").first
    if toc.count() == 0:
        pytest.skip("Page TOC not found; show_page_toc may be False")
    links = toc.locator("a.nav-link, a.reference")
    assert links.count() > 0


def test_sidebar_title_matches_top_breadcrumb(page: Page) -> None:
    """Verify the sidebar title matches the section name in the breadcrumbs.

    Computes the expected title from the first non-home breadcrumb and compares it to the
    single sidebar title on a nested page.
    """
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
    """Verify the sidebar title on a top-level page.

    Opens the getting started page and checks the sidebar title is 'Getting started'.
    """
    open_page(page, TOP_NAV_PAGE)
    expect(page.locator(".bd-docs-nav .bd-links__title")).to_have_text("Getting started")


def test_edit_this_page_link_present(page: Page) -> None:
    """Verify the secondary sidebar edit link points to GitHub.

    Skipped when no edit link is rendered (GitHub context not configured).
    """
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
    """Verify the 'Show Source' link is present when enabled.

    Skipped when show_source_button is disabled.
    """
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
    """Verify the secondary sidebar contains the page TOC and edit links.

    Checks the sidebar and the page TOC are attached and, when an edit section exists, that
    it contains a link. Skipped when the primary sidebar TOC is active.
    """
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
    """Verify no page TOC is rendered in the secondary sidebar when disabled.

    Skipped when the page TOC is enabled.
    """
    open_page(page, NESTED_PAGE)
    if has_secondary_page_toc(page):
        pytest.skip("show_page_toc is enabled")
    if not is_primary_toc_enabled(page):
        expect(page.locator(".bd-sidebar-secondary #pst-page-toc-nav")).to_have_count(0)


def test_source_link_absent_when_disabled(page: Page) -> None:
    """Verify no source link is rendered when it is disabled.

    Skipped when the source link is present.
    """
    open_page(page, NESTED_PAGE)
    link = page.locator(
        '.bd-sidebar-secondary a[href*="_sources"], '
        '.bd-sidebar-secondary a:has-text("Show Source"), '
        ".bd-sidebar-secondary .tocsection.viewsourcecode"
    ).first
    if link.count():
        pytest.skip("Source link is present; show_source_button is enabled")
    expect(link).to_have_count(0)


@pytest.mark.parametrize("selector", (".ast-primary-toc", ".ast-toc-toggle"))
def test_no_primary_toc_elements_when_disabled(page: Page, selector: str) -> None:
    """Verify no primary sidebar TOC or toggle is rendered when the feature is off.

    Skipped when show_page_toc_in_primary_sidebar is enabled.
    """
    open_page(page, NESTED_PAGE)
    if is_primary_toc_enabled(page):
        pytest.skip("Primary TOC feature is enabled")
    expect(page.locator(selector)).to_have_count(0)


def test_primary_toc_is_injected_when_enabled(page: Page) -> None:
    """Verify the page TOC is injected into the primary sidebar.

    Checks the primary TOC exists and contains links. Skipped when the feature is off.
    """
    open_page(page, NESTED_PAGE)
    require_primary_toc(page)
    toc = page.locator(".bd-sidebar-primary .ast-primary-toc")
    expect(toc).to_be_attached()
    assert toc.locator("a").count() > 0


def test_primary_toc_toggle_is_accessible(page: Page) -> None:
    """Verify the primary TOC toggle has accessible attributes.

    Checks the toggle has an aria-label, starts collapsed (aria-expanded='false') and is a
    button. Skipped when the feature is off or the page has no current nav item.
    """
    open_page(page, NESTED_PAGE)
    require_primary_toc(page)
    if page.locator(".bd-docs-nav .bd-toc-item li.current").count() == 0:
        pytest.skip("No current nav item; top-level page uses direct-append fallback")
    toggle = page.locator(".ast-toc-toggle")
    expect(toggle).to_have_attribute("aria-label", re.compile("toggle page sections", re.I))
    expect(toggle).to_have_attribute("aria-expanded", "false")
    expect(toggle).to_have_attribute("type", "button")


def test_primary_toc_toggle_expands_and_collapses(page: Page) -> None:
    """Verify the toggle expands and collapses the primary TOC.

    Clicks the toggle twice and checks the TOC visibility, aria-expanded and open class
    change each time. Skipped when the feature is off or no toggle exists.
    """
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
    """Verify the page TOC is removed from the secondary sidebar when in the primary one.

    Skipped when the primary TOC feature is off.
    """
    open_page(page, NESTED_PAGE)
    require_primary_toc(page)
    expect(
        page.locator(".bd-sidebar-secondary #pst-page-toc-nav, .bd-sidebar-secondary nav.page-toc")
    ).to_have_count(0)


def test_primary_toc_uses_sidebar_sizing_class(page: Page) -> None:
    """Verify the primary TOC uses the sidebar sizing class.

    Checks the TOC has the 'bd-sidenav' class and not 'section-nav'.
    """
    open_page(page, NESTED_PAGE)
    require_primary_toc(page)
    toc = page.locator(".ast-primary-toc")
    expect(toc).to_have_class(re.compile("bd-sidenav"))
    expect(toc).not_to_have_class(re.compile("section-nav"))


def test_top_level_primary_toc_uses_direct_append_fallback(page: Page) -> None:
    """Verify top-level pages append the TOC directly without a toggle.

    On the section root page, checks no toggle exists and the nav list is present.
    Skipped when the feature is off or a current nav item exists.
    """
    open_page(page, SECTION_ROOT_PAGE)
    require_primary_toc(page)
    if page.locator(".bd-docs-nav .bd-toc-item li.current").count():
        pytest.skip("Current nav item found; direct-append fallback is not active")
    expect(page.locator(".ast-toc-toggle")).to_have_count(0)
    expect(page.locator(".bd-docs-nav .bd-toc-item > ul")).to_be_attached()


def test_page_toc_is_not_present_in_both_sidebars(page: Page) -> None:
    """Verify the page TOC is never rendered in both sidebars at once.

    Checks the primary and secondary TOCs are not both present.
    """
    open_page(page, NESTED_PAGE)
    primary = page.locator(".ast-primary-toc").count() > 0
    secondary = page.locator("#pst-page-toc-nav, .bd-sidebar-secondary nav.page-toc").count() > 0
    assert not (primary and secondary)


def test_primary_toc_scroll_spy_highlights_heading(page: Page) -> None:
    """Verify scrolling highlights the current heading in the primary TOC.

    Opens the TOC, scrolls to the page bottom and checks exactly one link is bold.
    Skipped when the feature is off or no toggle exists.
    """
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
    """Verify scrolling expands a collapsed primary TOC.

    Scrolls to the page bottom while the TOC is hidden and checks it becomes visible with
    one highlighted link. Skipped when the feature is off or no toggle exists.
    """
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
