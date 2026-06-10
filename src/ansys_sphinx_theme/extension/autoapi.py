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

"""Module containing an extension for creating Sphinx AutoAPI templates for the Ansys Sphinx Theme."""  # noqa: E501

import os
from pathlib import Path
from typing import Any, Dict

from sphinx.application import Sphinx

from ansys_sphinx_theme import __version__, get_autoapi_templates_dir_relative_path

AUTOAPI_OPTIONS = [
    "members",
    "undoc-members",
    "show-inheritance",
    "show-module-summary",
    "special-members",
]


def add_autoapi_theme_option(app: Sphinx, config: Dict[str, Any]) -> None:
    """Add the autoapi template path to the theme options.

    Parameters
    ----------
    app : ~sphinx.application.Sphinx
        Application instance for rendering the documentation.
    """
    autoapi = app.config.html_theme_options.get("ansys_sphinx_theme_autoapi", {})
    if not autoapi:
        return
    autoapi_template_dir = autoapi.get("templates", "")
    autoapi_project_name = autoapi.get("project", "")

    if not autoapi_template_dir:
        autoapi_template_dir = get_autoapi_templates_dir_relative_path(app.confdir)

    config["autoapi_template_dir"] = autoapi_template_dir

    def prepare_jinja_env(jinja_env) -> None:
        """Prepare the Jinja environment for the theme."""
        jinja_env.globals["project_name"] = autoapi_project_name
        jinja_env.globals["autoapi_depth"] = autoapi.get("package_depth", 3)

    # Set the autoapi options

    config["autoapi_prepare_jinja_env"] = prepare_jinja_env
    config["autoapi_type"] = autoapi.get("type", "python")
    config["autoapi_root"] = autoapi.get("output", "api")
    config["autoapi_own_page_level"] = autoapi.get("own_page_level", "class")
    config["autoapi_python_use_implicit_namespaces"] = autoapi.get("use_implicit_namespaces", True)
    config["autoapi_keep_files"] = autoapi.get("keep_files", True)
    config["autoapi_python_class_content"] = autoapi.get("class_content", "class")
    config["autoapi_options"] = autoapi.get("options", AUTOAPI_OPTIONS)
    config["autoapi_ignore"] = autoapi.get("ignore", [])
    config["autoapi_add_toctree_entry"] = autoapi.get("add_toctree_entry", True)
    config["autoapi_member_order"] = autoapi.get("member_order", "bysource")

    # HACK: The ``autoapi_dirs`` should be given as a relative path to the conf.py.
    autoapi_dir = autoapi.get("directory", "src/ansys")
    # assume the docs are in doc/source directory
    root_dir = Path(app.srcdir).resolve().parent.parent
    path_to_autoapi_dir = (root_dir / autoapi_dir).resolve()
    if path_to_autoapi_dir.exists():
        relative_autoapi_dir = os.path.relpath(path_to_autoapi_dir, start=app.srcdir)
    else:
        relative_autoapi_dir = autoapi_dir
    config["autoapi_dirs"] = [str(relative_autoapi_dir)]


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
    # HACK: The ``autoapi.extension``,  ``sphinx_design``, and ``sphinx_jinja`` extensions should be
    # added to the Sphinx configuration.
    required_extensions = ["sphinx_design", "sphinx_jinja", "autoapi.extension"]
    for extension in required_extensions:
        if extension not in app.config["extensions"]:
            app.setup_extension(extension)

    app.connect("config-inited", add_autoapi_theme_option)
    return {
        "version": __version__,
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }
