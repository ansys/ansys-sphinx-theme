"""Shared helpers for the Playwright browser tests."""

import os

from playwright.sync_api import Page

BASE_URL = os.environ.get("ANSYS_THEME_BASE_URL", "http://localhost:8000").rstrip("/")


def open_page(page: Page, path: str = "") -> None:
    """Navigate to a generated documentation page."""
    page.goto(f"{BASE_URL}/{path.lstrip('/')}")
