# Copyright (C) 2021 - 2026 ANSYS, Inc. and/or its affiliates.
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

    Parameters
    ----------
    app : Sphinx
        Sphinx application.
    """
    theme_static_options = app.config.html_theme_options.get("static_search", {})
    theme_static_options["keys"] = ["title", "text", "objectID"]
    theme_static_options["threshold"] = theme_static_options.get("threshold", 0.2)
    theme_static_options["limit"] = theme_static_options.get("limit", 10)
    app.config.html_theme_options["static_search"] = theme_static_options


__all__ = [
    "create_search_index",
    "update_search_config",
]
