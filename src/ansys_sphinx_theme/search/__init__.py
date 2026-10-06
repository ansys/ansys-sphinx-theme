# Copyright (C) 2021 - 2026 Synopsys, Inc. and ANSYS, Inc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Initiate the search."""

from sphinx.application import Sphinx

from ansys_sphinx_theme.search.fuse_search import (
    create_search_index,
)


def update_search_config(app: Sphinx) -> None:
    """Update the search configuration.

    The ``static_search`` theme option accepts the following keys (all optional):

    - **keys** (*list*) – Fuse.js field descriptors with ``name`` and ``weight``.
      Default weights: ``section`` = 3, ``title`` = 3, ``text`` = 1,
      ``objectID`` = 0.5.
    - **threshold** (*float*) – Fuse.js match threshold (0 = exact, 1 = any).
      Defaults to ``0.2``.
    - **limit** (*int*) – Maximum number of results returned. Defaults to ``10``.
    - **includeScore** (*bool*) – Include Fuse.js score in results. Defaults to
      ``True``.
    - **includeMatches** (*bool*) – Include matched indices in results. Defaults
      to ``True``.

    Parameters
    ----------
    app : Sphinx
        Sphinx application.
    """
    theme_static_options = app.config.html_theme_options.get("static_search", {})
    theme_static_options.setdefault(
        "keys",
        [
            {"name": "section", "weight": 3},
            {"name": "title", "weight": 3},
            {"name": "text", "weight": 1},
            {"name": "objectID", "weight": 0.5},
        ],
    )
    theme_static_options.setdefault("threshold", 0.2)
    theme_static_options.setdefault("limit", 10)
    theme_static_options.setdefault("includeScore", True)
    theme_static_options.setdefault("includeMatches", True)
    app.config.html_theme_options["static_search"] = theme_static_options


__all__ = [
    "create_search_index",
    "update_search_config",
]
