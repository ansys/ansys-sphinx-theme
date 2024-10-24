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
"""Initiate the search."""

from sphinx.application import Sphinx

from ansys_sphinx_theme.search.fuse_search import (
    ALL_NODES,
    LITERAL,
    PARAGRAPHS,
    TITLES,
    create_search_index,
)


def update_search_config(app: Sphinx) -> None:
    """Update the search configuration.

    Parameters
    ----------
    app : Sphinx
        Sphinx application.
    """
    theme_static_options = app.config.html_theme_options.get("static_search", {})
    theme_static_options["keys"] = ["title", "text"]
    theme_static_options["threshold"] = theme_static_options.get("threshold", 0.2)
    theme_static_options["limit"] = theme_static_options.get("limit", 10)
    app.add_config_value("index_patterns", {}, "html")
    app.config.html_theme_options["static_search"] = theme_static_options


__all__ = [
    "create_search_index",
    "update_search_config",
    "LITERAL",
    "PARAGRAPHS",
    "TITLES",
    "ALL_NODES",
]
