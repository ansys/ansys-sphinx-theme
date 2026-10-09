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

"""Content resolver Sphinx extension entry point."""

from sphinx.application import Sphinx

from ansys_sphinx_theme.extension.resolver import __version__, setup_content_resolver

__all__ = ["__version__", "setup"]


def setup(app: Sphinx) -> dict:
    """Set up the Content Resolver Sphinx Extension.

    Parameters
    ----------
    app : Sphinx
        The Sphinx application instance.

    Returns
    -------
    dict
        Configuration information for the extension.
    """
    setup_content_resolver(app)
    return {
        "version": __version__,
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }
