"""Shared helpers for the Playwright browser tests."""

import os

from playwright.sync_api import Page

PORT = os.environ.get("ANSYS_THEME_TEST_PORT", "8000")
BASE_URL = f"http://localhost:{PORT}"


def open_page(page: Page, path: str = "") -> None:
    """Navigate to a generated documentation page."""
    page.goto(f"{BASE_URL}/{path.lstrip('/')}")
