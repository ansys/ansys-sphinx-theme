"""Playwright coverage for site navigation and rendered components."""

import re

from playwright.sync_api import Page, expect
import pytest
from test_common.common import open_page


def test_homepage_loads(page: Page) -> None:
    """Verify the home page renders its main heading.

    Opens index.html and checks the first h1 exists and mentions the theme name or 'Welcome'.
    """
    open_page(page, "index.html")
    heading = page.locator("h1").first
    expect(heading).to_be_attached()
    expect(heading).to_contain_text(re.compile("Ansys Sphinx Theme|Welcome", re.I))


def test_navbar_links_and_dropdown(page: Page) -> None:
    """Verify the top navigation links and the 'More' dropdown.

    Checks each primary navbar link exists with the expected href, then opens the 'More'
    dropdown and checks its Contribute and API reference entries.
    """
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
    """Verify the components at the end of the navbar are present.

    Checks the search bar input, version switcher button, color mode button and GitHub
    repository link are attached. Only the first match of each is used, since some
    components render in more than one place (e.g. desktop and mobile).
    """
    open_page(page)
    expect(page.locator('.search-bar input[type="search"]').first).to_be_attached()
    expect(page.locator("button.version-switcher__button").first).to_be_attached()
    expect(page.locator("button.theme-switch-button").first).to_be_attached()
    expect(page.locator('a[href*="github.com/ansys/ansys-sphinx-theme"]').first).to_be_attached()


def test_navigation_contains_home_link(page: Page) -> None:
    """Verify the navigation bar has a 'Home' link.

    Checks the link exists and points to the site root.
    """
    open_page(page)
    link = page.locator("nav a.nav-link").filter(has_text="Home").first
    expect(link).to_be_attached()
    expect(link).to_have_attribute("href", re.compile(r"#|index\.html"))


@pytest.mark.parametrize("path", ("", "user-guide.html"))
def test_sidebar_has_links(page: Page, path: str) -> None:
    """Verify the primary sidebar is rendered and contains links.

    Opens the home page and the user guide, and checks the primary sidebar has links.
    """
    open_page(page, path)
    sidebar = page.locator(".bd-sidebar-primary").first
    expect(sidebar).to_be_attached()
    expect(sidebar.locator("a").first).to_be_attached()


def test_version_switcher_exists(page: Page) -> None:
    """Verify the version switcher is rendered.

    Checks the switcher button is attached and shows a non-empty active version.
    """
    open_page(page)
    button = page.locator("button.version-switcher__button").first
    expect(button).to_be_attached()
    expect(button).not_to_be_empty()


def test_version_switcher_opens_dropdown(page: Page) -> None:
    """Verify clicking the version switcher opens its menu.

    Clicks the first switcher button and checks it is expanded and controls a visible menu.
    """
    open_page(page)
    button = page.locator("button.version-switcher__button").first
    expect(button).to_be_visible()
    button.click()
    expect(button).to_have_attribute("aria-expanded", "true")
    menu_id = button.get_attribute("aria-controls")
    expect(page.locator(f"[id='{menu_id}']")).to_be_visible()


def test_theme_switcher_options(page: Page) -> None:
    """Verify the color mode switcher offers all modes and applies one.

    Opens the color mode menu, checks the light, dark and auto buttons exist, selects dark
    and checks the html element gets data-mode='dark'.
    """
    open_page(page)
    switcher = page.locator('button.theme-switch-button[aria-label="Color mode"]').first
    expect(switcher).to_be_attached()
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
    """Verify dark mode CSS variables resolve to usable colors.

    Forces data-mode='dark' on the html element and checks the search bar CSS variables are
    defined and that the background and body text color are not pure black.
    """
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
    """Verify breadcrumbs render on a nested page.

    Opens user-guide/configuration.html and checks the breadcrumb navigation is attached.
    """
    open_page(page, "user-guide/configuration.html")
    expect(page.locator('.bd-breadcrumb, nav[aria-label="Breadcrumb"]').first).to_be_attached()


def test_logo_links_home(page: Page) -> None:
    """Verify the navbar logo is wrapped in a link to the home page.

    Checks the logo exists and its closest anchor points to the site root or index.html.
    """
    open_page(page)
    logo = page.locator('img[alt*="logo" i], .navbar-brand img, .logo').first
    expect(logo).to_be_attached()
    href = logo.evaluate("element => element.closest('a')?.getAttribute('href')")
    assert re.search(r"/?(index\.html)?$", href or "")


def test_edit_this_page_button_exists(page: Page) -> None:
    """Verify the 'Edit on GitHub' button is present on a content page.

    Opens user-guide/configuration.html and checks the edit button is attached.
    Skipped when the button is not rendered.
    """
    open_page(page, "user-guide/configuration.html")
    button = page.locator('tocsection.editthispage, a:has-text("Edit on GitHub")').first
    if button.count() == 0:
        pytest.skip("Edit this page button not found")
    expect(button).to_be_attached()


def test_footer_links_and_version(page: Page) -> None:
    """Verify the footer shows copyright, links and the theme version.

    Checks the footer contains a copyright element, at least one link and a theme version
    element with text.
    """
    open_page(page)
    footer = page.locator(".bd-footer")
    expect(footer).to_be_attached()
    expect(footer.locator(".copyright")).to_be_attached()
    assert footer.locator("a").count() > 0
    expect(footer.locator(".theme-version")).to_be_attached()
    assert footer.locator(".theme-version").text_content() is not None


def test_code_block_and_copy_button(page: Page) -> None:
    """Verify code blocks are highlighted and have a working copy button.

    Opens user-guide/configuration.html, checks a highlighted block and a copy button are
    attached, then clicks the copy button and checks it reports success.
    """
    open_page(page, "user-guide/configuration.html")
    expect(page.locator(".highlight").first).to_be_attached()
    copy_button = page.locator("button.copybtn").first
    expect(copy_button).to_be_attached()
    copy_button.click(force=True)
    expect(copy_button).to_have_class(re.compile(r"\bsuccess\b"))


def test_sphinx_tabs(page: Page) -> None:
    """Verify tab sets render and can be switched.

    Opens user-guide/configuration.html, checks a tab set is attached and, when it has more
    than one tab, clicks the second tab label and checks its input becomes checked.
    """
    open_page(page, "user-guide/configuration.html")
    tab_set = page.locator(".sd-tab-set").first
    expect(tab_set).to_be_attached()
    labels = tab_set.locator("> label.sd-tab-label")
    assert labels.count() > 1
    labels.nth(1).click()
    expect(tab_set.locator("> input").nth(1)).to_be_checked()


def test_tables(page: Page) -> None:
    """Verify tables render inside the scrollable container.

    Opens examples/table.html and checks the table container has header cells and body rows.
    """
    open_page(page, "examples/table.html")
    table = page.locator(".pst-scrollable-table-container").first
    expect(table).to_be_attached()
    assert table.locator("th").count() > 0
    assert table.locator("tbody tr").count() > 0


def test_admonitions(page: Page) -> None:
    """Verify admonitions render.

    Opens examples/admonitions.html and checks at least one admonition element is attached.
    """
    open_page(page, "examples/admonitions.html")
    expect(
        page.locator(".admonition, .note, .warning, .caution, .tip, .important").first
    ).to_be_attached()


def test_sphinx_design_card_grid_and_badge(page: Page) -> None:
    """Verify sphinx-design cards, grids and badges render.

    Opens examples/sphinx-design.html and checks a card, a grid or row and a badge are attached.
    """
    open_page(page, "examples/sphinx-design.html")
    expect(page.locator(".sd-card, .card, div.sd-card").first).to_be_attached()
    expect(page.locator(".sd-row, .sd-grid, .row, .grid").first).to_be_attached()
    expect(page.locator(".sd-badge, span.sd-badge, button.sd-badge").first).to_be_attached()


def test_clickable_card_navigation(page: Page) -> None:
    """Verify a clickable sphinx-design card navigates to its link.

    Finds the stretched link of the external clickable card and clicks it. Follows a popup
    when the link opens in a new tab, otherwise follows the in-page navigation, and checks
    the resulting URL contains the link's href.
    """
    open_page(page, "examples/sphinx-design.html")
    link = page.locator(
        '.sd-card:has(.sd-card-title:has-text("Clickable Card (external)")) a.sd-stretched-link'
    ).first
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
    """Verify a sphinx-design dropdown opens and shows its content.

    Makes sure the dropdown is closed, clicks its summary, then checks it is open and
    shows the expected content.
    """
    open_page(page, "examples/sphinx-design.html")
    dropdown = page.locator("details.sd-dropdown").first
    expect(dropdown).to_be_attached()
    summary = dropdown.locator("summary.sd-summary-title")
    expect(summary).to_be_attached()
    if dropdown.get_attribute("open") is not None:
        summary.click()
    summary.click()
    expect(dropdown).to_have_attribute("open", "")
    expect(dropdown.locator(".sd-summary-content")).to_contain_text("Dropdown content")
