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
from typing import Dict, List, Union

import bs4
from docutils import nodes
from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import PythonLexer
import sphinx
from sphinx.util.nodes import make_refnode
import yaml


def load_navbar_config(app: sphinx.application.Sphinx) -> None:
    """Load the navbar configuration from a YAML file.

    This function is called when the Sphinx application is initialized to load
    the navbar configuration from a specified YAML file.

    Parameters
    ----------
    app : sphinx.application.Sphinx
        Application instance passed when the `config-inited` event is emitted
    """
    config_options = app.config.html_theme_options.get("use_navigation_dropdown", {})
    if not config_options:
        return
    navigation_yaml_file = config_options.get("navigation_yaml_file", None)
    if navigation_yaml_file:
        try:
            with pathlib.Path.open(app.srcdir / navigation_yaml_file, encoding="utf-8") as f:
                app.config.navbar_contents = yaml.safe_load(f)
        except FileNotFoundError:
            raise FileNotFoundError(
                f"Navbar configuration file '{navigation_yaml_file}' not found in source directory."
            )
        except yaml.YAMLError as exc:
            raise ValueError(f"Error parsing YAML file '{navigation_yaml_file}': {exc}")


NavEntry = Dict[str, Union[str, List["NavEntry"]]]


def setup_context(app, pagename, templatename, context, doctree):
    """Add custom variables to the context for use in templates."""

    @lru_cache(maxsize=None)
    def render_header_nav_links() -> bs4.BeautifulSoup:
        """Render external header links into the top nav bar.

        The structure rendered here is defined in an external yaml file.

        Returns
        -------
        str
            Raw HTML to be rendered in the top nav bar
        """
        if not hasattr(app.config, "navbar_content"):
            raise ValueError(
                "A template is attempting to call render_header_nav_links(); a "
                "navbar configuration must be specified."
            )

        node = nodes.container(classes=["navbar-content"])
        node.append(render_header_nodes(app.config.navbar_content))
        header_soup = bs4.BeautifulSoup(app.builder.render_partial(node)["fragment"], "html.parser")
        return add_nav_chevrons(header_soup)

    def render_header_nodes(obj: List[NavEntry], is_top_level: bool = True) -> nodes.Node:
        """Generate a set of header nav links with docutils nodes.

        Parameters
        ----------
        is_top_level : bool
            True if the call to this function is rendering the top level nodes,
            False otherwise (non-top level nodes are displayed as submenus of the top
            level nodes)
        obj : List[NavEntry]
            List of yaml config entries to render as docutils nodes

        Returns
        -------
        nodes.Node
            Bullet list which will be turned into header nav HTML by the sphinx builder
        """
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
                wrapper.append(render_header_nodes(item["sections"], is_top_level=False))
                list_item.append(wrapper)

            bullet_list.append(list_item)

        return bullet_list

    context["render_header_nav_links"] = render_header_nav_links
    # context["render_library_examples"] = render_library_examples

    # Update the HTML page context with a few extra utilities.
    context["pygments_highlight_python"] = lambda code: highlight(
        code, PythonLexer(), HtmlFormatter()
    )


def add_nav_chevrons(input_soup: bs4.BeautifulSoup) -> bs4.BeautifulSoup:
    """Add dropdown chevron icons to the header nav bar.

    Parameters
    ----------
    input_soup : bs4.BeautifulSoup
        Soup containing rendered HTML which will be inserted into the header nav bar

    Returns
    -------
    bs4.BeautifulSoup
        A new BeautifulSoup instance containing chevrons on the list items that
        are meant to be dropdowns.
    """
    soup = copy.copy(input_soup)

    for li in soup.find_all("li", recursive=True):
        divs = li.find_all("div", {"class": "navbar-dropdown"}, recursive=False)
        if divs:
            ref = li.find("div", {"class": "ref-container"})
            ref.append(soup.new_tag("i", attrs={"class": "fa-solid fa-chevron-down"}))

    return soup


def render_example_gallery_dropdown(cls: type) -> bs4.BeautifulSoup:
    """Render a dropdown menu selector for the example gallery.

    Parameters
    ----------
    cls : type
        ExampleEnum class type to use to populate the dropdown

    Returns
    -------
    bs4.BeautifulSoup
        Soup containing the dropdown element
    """
    soup = bs4.BeautifulSoup()

    dropdown_name = cls.formatted_name().lower().replace(" ", "-")
    dropdown_container = soup.new_tag(
        "div", attrs={"class": "filter-dropdown", "id": f"{dropdown_name}-dropdown"}
    )

    dropdown_show_checkbox = soup.new_tag(
        "input",
        attrs={
            "class": "dropdown-checkbox",
            "id": f"{dropdown_name}-checkbox",
            "type": "checkbox",
        },
    )
    dropdown_container.append(dropdown_show_checkbox)

    dropdown_label = soup.new_tag(
        "label", attrs={"class": "dropdown-label", "for": f"{dropdown_name}-checkbox"}
    )
    dropdown_label.append(cls.formatted_name())
    chevron = soup.new_tag("i", attrs={"class": "fa-solid fa-chevron-down"})
    dropdown_label.append(chevron)
    dropdown_container.append(dropdown_label)

    if cls.values():
        dropdown_options = soup.new_tag("div", attrs={"class": "dropdown-content"})

        for member in list(cls):
            label = soup.new_tag("label", attrs={"class": "checkbox-container"})
            label.append(member.value)

            tag = getattr(member, "tag", member.value)
            checkbox = soup.new_tag(
                "input",
                attrs={
                    "id": f"{tag}-checkbox",
                    "class": "filter-checkbox",
                    "type": "checkbox",
                },
            )
            label.append(checkbox)

            checkmark = soup.new_tag("span", attrs={"class": "checkmark"})
            label.append(checkmark)

            dropdown_options.append(label)

        dropdown_container.append(dropdown_options)

    soup.append(dropdown_container)
    return soup
