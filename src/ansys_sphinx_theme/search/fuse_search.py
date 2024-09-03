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

"""Module to fuse search."""

import json
from typing import Any, Dict

from docutils import nodes
from sphinx.application import Sphinx


def create_search_index(app, exception):
    """Create a search index from the rst files."""
    # Get the current document's path
    all_docs = app.env.found_docs
    search_index_list = []
    for doc in all_docs:
        doc_name = doc
        doc_path = doc + ".html"
        doc_title = app.env.titles[doc].astext()
        doc_source = app.env.get_doctree(doc).traverse(nodes.paragraph)
        doc_text = "\n".join([node.astext() for node in doc_source]).strip()
        search_index = {
            "objectID": doc_name,  # Unique ID (document name)
            "href": doc_path,  # Relative file path
            "title": doc_title,  # Title of the document
            "section": "",  # Empty for now
            "text": doc_text,  # Body text of the document
        }
        search_index_list.append(search_index)

    # create search.json in outdir
    outdir = app.builder.outdir
    with open(outdir / "search.json", "w", encoding="utf-8") as f:  # noqa: PTH123
        json.dump(search_index_list, f, ensure_ascii=False, indent=4)


def setup(app: Sphinx) -> Dict[str, Any]:
    """Set up the Sphinx extension."""
    app.connect("build-finished", create_search_index)
