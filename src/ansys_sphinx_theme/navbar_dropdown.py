# Copyright (C) 2021 - 2025 ANSYS, Inc. and/or its affiliates.
# SPDX-License-Identifier: MIT
#
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""Navigation Dropdown for navigation bar."""

import copy
from functools import lru_cache
import pathlib

import bs4
from docutils import nodes
import sphinx
from sphinx.util import logging
from sphinx.util.nodes import make_refnode
import yaml

logger = logging.getLogger(__name__)


def load_navbar_configuration(app: sphinx.application.Sphinx) -> None:
    """Load the navbar configuration from a YAML file for the Sphinx app."""
    navigation_theme_options = app.config.html_theme_options.get("navigation_dropdown", {})
    if not navigation_theme_options or "layout_file" not in navigation_theme_options:
        return
    layout_file = navigation_theme_options["layout_file"]
    try:
        with pathlib.Path.open(app.srcdir / layout_file, encoding="utf-8") as config_file:
            app.config.navbar_contents = yaml.safe_load(config_file)
    except FileNotFoundError:
        raise FileNotFoundError(f"Could not find {layout_file}.")
    except yaml.YAMLError as exc:
        raise ValueError(f"Error parsing '{layout_file}': {exc}")


NavEntry = dict[str, str | list["NavEntry"]]
"""Type alias for a navigation entry in the navbar configuration.

Each entry can have a 'file' or 'link' key, and optionally 'title',
'caption', and 'sections' keys. The 'sections' key contains a list of
sub-entries, allowing for nested navigation structures.
"""


def update_template_context(app, pagename, templatename, context, doctree):
    """Inject custom variables and utilities into the Sphinx template context."""

    @lru_cache(maxsize=None)
    def render_navbar_links_html() -> bs4.BeautifulSoup:
        """Render external header links as HTML for the navbar."""
        if not hasattr(app.config, "navbar_contents"):
            raise ValueError("Navbar configuration is missing. Please specify a navbar YAML file.")
        node = nodes.container(classes=["navbar-content"])
        node.append(build_navbar_nodes(app.config.navbar_contents))
        header_soup = bs4.BeautifulSoup(app.builder.render_partial(node)["fragment"], "html.parser")
        return add_navbar_chevrons(header_soup)

    def build_navbar_nodes(obj: list[NavEntry], is_top_level: bool = True) -> nodes.Node:
        """Recursively build navbar nodes from configuration entries."""
        bullet_list = nodes.bullet_list(
            bullet="-",
            classes=["navbar-toplevel" if is_top_level else "navbar-sublevel"],
        )
        for item in obj:
            if "file" in item:
                ref_node = make_refnode(
                    app.builder,
                    context["current_page_name"],
                    item["file"],
                    None,
                    nodes.inline(classes=["navbar-link-title"], text=item.get("title")),
                    item.get("title"),
                )
            elif "link" in item:
                ref_node = nodes.reference("", "", internal=False)
                ref_node["refuri"] = item.get("link")
                ref_node["reftitle"] = item.get("title")
                ref_node.append(nodes.inline(classes=["navbar-link-title"], text=item.get("title")))
            else:
                logger.warning(
                    f"Navbar entry '{item}' is missing 'file' or 'link' key. Skipping this entry."
                )
                continue
            if "caption" in item:
                caption = nodes.Text(item.get("caption"))
                ref_node.append(caption)
            paragraph = nodes.paragraph()
            paragraph.append(ref_node)
            container = nodes.container(classes=["ref-container"])
            container.append(paragraph)
            list_item = nodes.list_item(
                classes=["active-link"] if item.get("file") == pagename else []
            )
            list_item.append(container)
            if "sections" in item:
                wrapper = nodes.container(classes=["navbar-dropdown"])
                wrapper.append(build_navbar_nodes(item["sections"], is_top_level=False))
                list_item.append(wrapper)
            bullet_list.append(list_item)
        return bullet_list

    context["render_navbar_links_html"] = render_navbar_links_html


def add_navbar_chevrons(input_soup: bs4.BeautifulSoup) -> bs4.BeautifulSoup:
    """Add dropdown chevron icons to navbar items with submenus."""
    soup = copy.copy(input_soup)
    for li in soup.find_all("li", recursive=True):
        divs = li.find_all("div", {"class": "navbar-dropdown"}, recursive=False)
        if divs:
            ref = li.find("div", {"class": "ref-container"})
            ref.append(soup.new_tag("i", attrs={"class": "fa-solid fa-chevron-down"}))
    return soup
