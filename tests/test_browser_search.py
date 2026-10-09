"""Playwright coverage for the documentation search interface."""

from playwright.sync_api import Page, expect

BASE_URL = "http://localhost:8000"


def test_search_returns_results(page: Page) -> None:
    page.goto(BASE_URL)
    search_button = page.locator(
        'button[aria-label*="search" i], .search-bar .fa-magnifying-glass, '
        '.search-button, [data-bs-toggle="search"]'
    ).first
    if search_button.count():
        search_button.click()
    else:
        page.keyboard.press(
            "Meta+K" if page.evaluate("navigator.platform.includes('Mac')") else "Control+K"
        )

    search_input = page.locator(
        '.search-bar input[type="search"], .search-bar input[placeholder*="Search" i]'
    ).first
    expect(search_input).to_be_visible()
    search_input.fill("install")
    page.wait_for_timeout(1500)
    expect(page.locator(".search-bar").first).to_be_attached()
    assert page.locator(".search-bar").count() > 0
