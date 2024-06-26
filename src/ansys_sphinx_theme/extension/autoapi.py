"""Module for adding the autoapi extension with the theme."""

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

"""Module containing an extension for creating Sphinx AutoAPI templates for the Ansys Sphinx Theme."""  # noqa: E501

import os
from typing import Any, Dict

from sphinx.application import Sphinx

from ansys_sphinx_theme import __version__, get_autoapi_templates_dir_relative_path


def add_autoapi_theme_option(app: Sphinx) -> None:
    """Add the autoapi template path to the theme options.

    Parameters
    ----------
    app : ~sphinx.application.Sphinx
        Application instance for rendering the documentation.
    """
    autoapi = app.config.html_theme_options.get("ansys_sphinx_theme_autoapi", {})
    if not autoapi:
        return

    # HACK: The ``sphinx_jinja`` and ``sphinx_design`` should be added to the extensions.
    required_extensions = ["sphinx_jinja", "sphinx_design"]

    for extension in required_extensions:
        if extension not in app.config["extensions"]:
            app.config["extensions"].append(extension)
    AUTOAPI_OPTIONS = [
        "members",
        "undoc-members",
        "show-inheritance",
        "show-module-summary",
        "special-members",
    ]
    autoapi_template_dir = autoapi.get("templates", "")
    autoapi_project_name = autoapi.get("project", "")

    if not autoapi_template_dir:
        autoapi_template_dir = get_autoapi_templates_dir_relative_path(app.confdir)

    app.config["autoapi_template_dir"] = autoapi_template_dir

    def prepare_jinja_env(jinja_env) -> None:
        """Prepare the Jinja environment for the theme."""
        jinja_env.globals["project_name"] = autoapi_project_name

    # Set the autoapi options

    app.config["autoapi_prepare_jinja_env"] = prepare_jinja_env
    app.config["autoapi_type"] = autoapi.get("type", "python")
    app.config["autoapi_root"] = autoapi.get("output", "api")
    app.config["autoapi_own_page_level"] = autoapi.get("own_page_level", "class")
    app.config["autoapi_python_use_implicit_namespaces"] = autoapi.get(
        "use_implicit_namespaces", True
    )
    app.config["autoapi_keep_files"] = autoapi.get("keep_files", True)
    app.config["autoapi_python_class_content"] = autoapi.get("class_content", "class")
    app.config["autoapi_options"] = autoapi.get("options", AUTOAPI_OPTIONS)
    app.config["autoapi_ignore"] = autoapi.get("ignore", [])
    app.config["autoapi_add_toctree_entry"] = autoapi.get("add_toctree_entry", False)

    # HACK: The ``autoapi_dirs`` should be given as a relative path to the conf.py.
    relative_autoapi_dir = os.path.relpath(
        autoapi.get("directory", "src/ansys"), start=str(app.confdir / "conf.py")
    )
    app.config["autoapi_dirs"] = [relative_autoapi_dir]


def setup(app: Sphinx) -> Dict[str, Any]:
    """Add the autoapi extension to the Sphinx application.

    Parameters
    ----------
    app : ~sphinx.application.Sphinx
        Application instance for rendering the documentation.

    Returns
    -------
    Dict[str, Any]
        A dictionary containing the version and parallel read/write safety flags.
    """
    # HACK: The ``autoapi.extension`` should add here to initialize the extension.
    app.setup_extension("autoapi.extension")
    app.connect("builder-inited", add_autoapi_theme_option, priority=400)
    return {
        "version": __version__,
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }
