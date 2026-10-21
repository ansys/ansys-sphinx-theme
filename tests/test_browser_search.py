"""Playwright coverage for the documentation search interface."""

from playwright.sync_api import Page, expect
from test_common.common import open_page

SEARCH_INPUT = '.search-bar input[type="search"], .search-bar input[placeholder*="Search" i]'
SEARCH_BUTTON = (
    'button[aria-label*="search" i], .search-bar .fa-magnifying-glass, '
    '.search-button, [data-bs-toggle="search"]'
)
QUERY = "install"


def test_search_accepts_query(page: Page) -> None:
    """Open the search dialog and verify it accepts a query.

    Opens the home page, clicks the search button (or uses the Cmd/Ctrl+K shortcut when no
    button exists), then checks the search input becomes visible and keeps the typed text.
    """
    open_page(page)
    search_button = page.locator(SEARCH_BUTTON).first
    if search_button.count():
        search_button.click()
    else:
        is_mac = page.evaluate("navigator.platform.includes('Mac')")
        page.keyboard.press("Meta+K" if is_mac else "Control+K")

    search_input = page.locator(SEARCH_INPUT).first
    expect(search_input).to_be_visible()
    search_input.fill(QUERY)
    expect(search_input).to_have_value(QUERY)


def test_static_search_results_appear(page: Page) -> None:
    """Verify static search results are displayed when a query is entered.

    Opens the home page, enters a search query, and checks that the static search results
    container becomes visible and contains at least one result.
    """
    open_page(page)
    search_input = page.locator(SEARCH_INPUT).first
    search_input.fill(QUERY)
    results = page.locator(".static-search-results").first
    expect(results).to_be_visible()
    result_item = page.locator(".result-item").first
    assert result_item is not None
    result_item = result_item.first
    expect(result_item).to_be_attached()


def test_enter_key_triggers_search(page: Page) -> None:
    """Verify pressing the Enter key takes to search.html.

    Opens the home page, enters a search query, presses Enter and
    check it takes to "search.html" page.
    """
    open_page(page)
    search_input = page.locator(SEARCH_INPUT).first
    search_input.fill(QUERY)
    search_input.press("Enter")
    assert "search.html" in page.url
    assert f"search.html?q={QUERY}" in page.url
    # check result items are visible
    result_item = page.locator(".result-item").first
    assert result_item is not None
    expect(result_item).to_be_attached()
