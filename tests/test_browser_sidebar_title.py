"""Playwright coverage for sidebar section titles."""

from playwright.sync_api import Page, expect
import pytest

BASE_URL = "http://localhost:8000"
API_PAGES = (
    "/examples/api/examples/sample_func/index.html",
    "/examples/api/examples/samples/ExamplePydanticClass.html",
)


@pytest.mark.parametrize("path", API_PAGES)
def test_sidebar_section_title_is_plain_text(page: Page, path: str) -> None:
    """API sidebar titles should be text, not injected HTML."""
    page.goto(f"{BASE_URL}{path}")
    title = page.locator(".bd-docs-nav .bd-links__title")
    expect(title).to_have_count(1)

    state = title.evaluate(
        """element => ({
            text: (element.textContent || '').trim(),
            html: element.innerHTML,
            ariaLabel: element.closest('.bd-docs-nav')?.getAttribute('aria-label')?.trim() || '',
            hasChildElements: element.children.length > 0,
            hasCodeTag: !!element.querySelector('code'),
        })"""
    )

    assert state["text"]
    assert state["ariaLabel"] == state["text"]
    assert state["hasChildElements"] is False
    assert state["hasCodeTag"] is False
    assert "<code" not in state["html"]
    if "<" in state["text"]:
        assert "&lt;" in state["html"]
    if ">" in state["text"]:
        assert "&gt;" in state["html"]


@pytest.mark.parametrize("path", ("/user-guide/options.html", "/getting-started.html"))
def test_sidebar_section_title_is_non_empty(page: Page, path: str) -> None:
    """Sidebar titles and their accessible labels should be non-empty and match."""
    page.goto(f"{BASE_URL}{path}")
    title = page.locator(".bd-docs-nav .bd-links__title")
    nav = page.locator(".bd-docs-nav")
    expect(title).to_have_count(1)
    title_text = (title.text_content() or "").strip()
    assert title_text
    expect(nav).to_have_attribute("aria-label", title_text)
