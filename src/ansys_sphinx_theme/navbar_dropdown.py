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
from typing import TypedDict

import bs4
from docutils import nodes
import sphinx
from sphinx.util import logging
from sphinx.util.nodes import make_refnode
import yaml

logger = logging.getLogger(__name__)


class NavEntry(TypedDict, total=False):
    """Represents an entry in the navbar configuration."""

    title: str
    caption: str
    file: str
    link: str
    sections: list["NavEntry"]


def load_navbar_configuration(app: sphinx.application.Sphinx) -> None:
    """Load the navbar configuration from a YAML file for the Sphinx app."""
    navigation_theme_options = app.config.html_theme_options.get("navigation_dropdown", {})
    if not navigation_theme_options or "layout_file" not in navigation_theme_options:
        return

    layout_file = navigation_theme_options["layout_file"]

    yaml_path = pathlib.Path(app.srcdir) / layout_file

    try:
        yaml_content = yaml_path.read_text(encoding="utf-8")
        app.config.navbar_contents = yaml.safe_load(yaml_content)

    except FileNotFoundError:
        raise FileNotFoundError(
            f"Navbar layout file '{layout_file}' not found in: {yaml_path.parent.resolve()}"
        )

    except yaml.YAMLError as exc:
        raise ValueError(f"Failed to parse YAML in '{yaml_path.name}': {exc}")


def update_template_context(
    app: sphinx, pagename: str, templatename: str, context: dict, doctree: nodes.document | None
) -> None:
    """Inject navbar rendering logic into the Sphinx HTML template context."""

    @lru_cache(maxsize=None)
    def render_navbar_links_html() -> bs4.BeautifulSoup:
        """Render the navbar content as HTML using the navbar configuration."""
        if not hasattr(app.config, "navbar_contents"):
            raise ValueError("Navbar configuration not found. Please define a layout YAML file.")

        nav_root = nodes.container(classes=["navbar-content"])
        nav_root.append(build_navbar_nodes(app.config.navbar_contents))
        rendered = app.builder.render_partial(nav_root)["fragment"]
        return add_navbar_chevrons(bs4.BeautifulSoup(rendered, "html.parser"))

    def build_navbar_nodes(entries: list[NavEntry], is_top_level: bool = True) -> nodes.bullet_list:
        """Recursively construct docutils nodes for the navbar structure."""
        classes = ["navbar-toplevel"] if is_top_level else ["navbar-sublevel"]
        nav_list = nodes.bullet_list(bullet="-", classes=classes)

        for entry in entries:
            title = entry.get("title", "")
            file = entry.get("file")
            link = entry.get("link")

            if file:
                ref_node = make_refnode(
                    app.builder,
                    context["current_page_name"],
                    file,
                    None,
                    nodes.inline(classes=["navbar-link-title"], text=title),
                    title,
                )
            elif link:
                ref_node = nodes.reference("", "", internal=False)
                ref_node["refuri"] = link
                ref_node["reftitle"] = title
                ref_node.append(nodes.inline(classes=["navbar-link-title"], text=title))
            else:
                logger.warning(
                    f"Invalid navbar entry: {entry}. Expected 'file' or 'link'. Skipping."
                )
                continue

            if "caption" in entry:
                ref_node.append(nodes.Text(entry["caption"]))

            paragraph = nodes.paragraph()
            paragraph.append(ref_node)

            container = nodes.container(classes=["ref-container"])
            container.append(paragraph)

            list_item_classes = ["active-link"] if file == pagename else []
            list_item = nodes.list_item(classes=list_item_classes)
            list_item.append(container)

            if "sections" in entry:
                dropdown = nodes.container(classes=["navbar-dropdown"])
                dropdown.append(build_navbar_nodes(entry["sections"], is_top_level=False))
                list_item.append(dropdown)

            nav_list.append(list_item)

        return nav_list

    context["render_navbar_links_html"] = render_navbar_links_html


def add_navbar_chevrons(soup: bs4.BeautifulSoup) -> bs4.BeautifulSoup:
    """Add chevron icons to navbar items that have dropdown menus."""
    soup_copy = copy.copy(soup)

    for li in soup_copy.find_all("li", recursive=True):
        if li.find("div", class_="navbar-dropdown", recursive=False):
            ref_container = li.find("div", class_="ref-container")
            if ref_container:
                chevron = soup_copy.new_tag("i", attrs={"class": "fa-solid fa-chevron-down"})
                ref_container.append(chevron)

    return soup_copy
