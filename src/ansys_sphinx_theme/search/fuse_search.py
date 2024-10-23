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


class SearchIndex:
    """Generate a search index for a Sphinx document."""

    def __init__(self, doc_name, app):
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
        self.doc_title = self.env.titles[self.doc_name].astext()
        self.doc_tree = self.env.get_doctree(self.doc_name)
        self.sections = []

    def build_sections(self):
        """Build sections from the document tree."""
        for node in self.doc_tree.traverse(nodes.section):
            section_title = node[0].astext()
            section_text = "\n".join(
                n.astext()
                for node_type in [nodes.paragraph, nodes.literal_block]
                for n in node.traverse(node_type)
            )
            section_anchor_id = _title_to_anchor(section_title)
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


def _title_to_anchor(title: str) -> str:
    """Convert a title to a URL-friendly anchor identifier."""
    return re.sub(r"[^\w\s-]", "", title.lower().strip().replace(" ", "-"))


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

    for document in app.env.found_docs:
        search_index = SearchIndex(document, app)
        search_index.build_sections()
        search_index_list.extend(search_index.indices)

    search_index_path = Path(app.builder.outdir) / "_static" / "search.json"
    with search_index_path.open("w", encoding="utf-8") as index_file:
        json.dump(search_index_list, index_file, ensure_ascii=False, indent=4)
