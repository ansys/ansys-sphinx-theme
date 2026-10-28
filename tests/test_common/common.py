"""Shared helpers for the Playwright browser tests."""

from playwright.sync_api import Page


def open_page(page: Page, path: str = "") -> None:
    """Navigate to a generated documentation page, relative to the served documentation."""
    page.goto(f"/{path.lstrip('/')}")
