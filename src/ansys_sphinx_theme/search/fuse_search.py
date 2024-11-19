# Copyright (C) 2021 - 2024 ANSYS, Inc. and/or its affiliates.
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

"""Module for generating search indices."""

import json
from pathlib import Path
import re

from docutils import nodes
from docutils.nodes import Element

PARAGRAPHS = [nodes.paragraph]
TITLES = [nodes.title]
LITERAL = [nodes.literal]
ALL_NODES = [nodes.Text]
DEFAULT_PATTERN = PARAGRAPHS + TITLES + LITERAL


class SearchIndex:
    """Generate a search index for a Sphinx document."""

    def __init__(self, doc_name, app, pattern=None):
        """
        Initialize the search index object.

        Parameters
        ----------
        doc_name : str
            Name of the document.
        app : Sphinx
            Sphinx application instance.
        """
        self.doc_name = doc_name
        self.doc_path = f"{self.doc_name}.html"
        self.env = app.env
        self.theme_options = app.config.html_theme_options.get("static_search", {})
        self.doc_title = self.env.titles[self.doc_name].astext()
        self.doc_tree = self.env.get_doctree(self.doc_name)
        self.sections = []
        self.pattern = pattern

    def build_sections(self):
        """Build sections from the document tree, handling subsections and descriptions."""
        for node in self.doc_tree.traverse(nodes.section):
            subsections = list(node.traverse(nodes.section))

            if len(subsections) > 1:
                # get only the first section
                main_section = subsections[0]
                # remove subsections from the main section
                for subsection in main_section.traverse(nodes.section):
                    subsection.parent.remove(subsection)
                node = main_section

            section_title = node[0].astext()

            section_text = "\n".join(
                n.astext() for node_type in self.pattern for n in node.traverse(node_type)
            )

            section_anchor_id = _title_to_anchor(section_title)
            self.sections.append(
                {
                    "title": section_title,
                    "text": section_text,
                    "anchor_id": section_anchor_id,
                }
            )

            self._process_desc_element(node, section_title)

    def _process_desc_element(self, node, title):
        """Process `desc` element within a section."""
        for element in node.traverse(Element):
            if element.tagname != "desc":
                continue

            # id is the id tag of the desc element
            section_anchor_id = element.attributes["ids"]
            if element.children:
                for element_child in element.children:
                    if element_child.tagname != "desc_signature":
                        continue
                    if element_child.attributes.get("ids"):
                        section_anchor_id = element_child.attributes["ids"][0]
            section_text = element.astext()
            if isinstance(section_anchor_id, list) and len(section_anchor_id) > 0:
                section_anchor_id = section_anchor_id[0]
            if section_anchor_id:
                section_title = _desc_anchor_to_title(title, section_anchor_id)
            else:
                section_title = title
            self.sections.append(
                {
                    "title": section_title,
                    "text": section_text,
                    "anchor_id": section_anchor_id,
                }
            )

    def generate_breadcrumbs(self, section_title: str) -> str:
        """
        Generate title breadcrumbs from the document structure.

        Parameters
        ----------
        section_title : str
            The section title to generate breadcrumbs for.

        Returns
        -------
        str
            Breadcrumb string.

        Notes
        -----
        The last part of `doc_name` is ignored because it represents the file name,
        which is not needed for the breadcrumb trail. The breadcrumb trail is generated
        by iterating over the parts of `doc_name` and fetching the title from the environment.
        """
        docs_parts = self.doc_name.split("/")[:-1]

        breadcrumb_parts = [
            self.env.titles[part].astext() for part in docs_parts if part in self.env.titles
        ]

        # Create breadcrumb hierarchy
        breadcrumbs = " > ".join(breadcrumb_parts)
        ignore_doc_title = section_title == self.doc_title

        # Construct final breadcrumb path
        if ignore_doc_title:
            return f"{breadcrumbs} > {section_title}" if breadcrumbs else section_title

        return (
            f"{breadcrumbs} > {self.doc_title} > {section_title}"
            if breadcrumbs
            else f"{self.doc_title} > {section_title}"
        )

    @property
    def indices(self):
        """Generate indices for each section."""
        for section in self.sections:
            breadcrumbs = self.generate_breadcrumbs(section["title"])
            yield {
                "objectID": self.doc_name,
                "href": f"{self.doc_path}#{section['anchor_id']}",
                "title": breadcrumbs,
                "section": section["title"],
                "text": section["text"],
            }


def _desc_anchor_to_title(title, anchor):
    """Convert a desc anchor to a title."""
    anchor_title = anchor.split(".")[-1]
    return f"{title} > {anchor_title}"


def _title_to_anchor(title: str) -> str:
    """Convert a title to a URL-friendly anchor identifier."""
    return re.sub(r"[^\w\s-]", "", title.lower().strip().replace(" ", "-"))


def get_pattern_for_each_page(app, doc_name):
    """Get the pattern for each page in the search index."""
    patterns = app.env.config.index_patterns or {}

    for filename, pattern in patterns.items():
        if doc_name.startswith(filename):
            return pattern

    return DEFAULT_PATTERN


def create_search_index(app, exception):
    """
    Generate search index at the end of the Sphinx build process.

    Parameters
    ----------
    app : Sphinx
        Sphinx application instance.
    exception : Exception
        Exception raised during the build process, if any.
    """
    if exception:
        return

    search_index_list = []

    static_search_options = app.config.html_theme_options.get("static_search", {})
    excluded_docs = static_search_options.get("files_to_exclude", [])
    included_docs = app.env.found_docs

    for exclude_doc in excluded_docs:
        exclude_doc = Path(exclude_doc).resolve()

        # Exclude documents based on whether exclude_doc is a folder or a file:
        # - For folders, exclude all documents within the folder.
        # - For files, exclude only the exact file match.
        included_docs = [
            doc for doc in included_docs if not Path(doc).resolve().is_relative_to(exclude_doc)
        ]

    for document in included_docs:
        pattern = get_pattern_for_each_page(app, document)
        search_index = SearchIndex(document, app, pattern)
        search_index.build_sections()
        search_index_list.extend(search_index.indices)

    search_index_path = Path(app.builder.outdir) / "_static" / "search.json"
    with search_index_path.open("w", encoding="utf-8") as index_file:
        json.dump(search_index_list, index_file, ensure_ascii=False, indent=4)
