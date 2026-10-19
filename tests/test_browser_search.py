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
    """Open the search dialog and verify it accepts a query."""
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
