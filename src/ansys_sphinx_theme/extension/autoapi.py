"""AutoAPI extension for the ANSYS Sphinx theme."""

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

import os
import pathlib
from typing import Any, Dict

from sphinx.application import Sphinx

from ansys_sphinx_theme import __version__

THIS_PARENT_PATH = pathlib.Path(__file__).parent.absolute()


AUTOAPI_TEMPLATES_PATH = (
    THIS_PARENT_PATH.parent.resolve() / "theme" / "ansys_sphinx_theme" / "_templates" / "autoapi"
)


def get_autoapi_templates_dir_relative_path(path: pathlib.Path) -> str:
    """Return a string representing the relative path for autoapi templates.

    Parameters
    ----------
    path : pathlib.Path
        Path to the desired file.

    Returns
    -------
    str
        A string rerpesenting the relative path to the autoapi templates.

    """
    print(AUTOAPI_TEMPLATES_PATH.absolute())
    return os.path.relpath(str(AUTOAPI_TEMPLATES_PATH.absolute()), start=str(path.absolute()))


def replace_html_tag(app, exception):
    """Replace HTML tags in the generated HTML files.

    Parameters
    ----------
    app : ~sphinx.application.Sphinx
        Application instance for rendering the documentation.
    exception : Exception
        Exception that occurred during the build process.
    """
    if exception is not None:
        return

    build_dir = pathlib.Path(app.builder.outdir).resolve()
    if app.config["extensions"] and "autoapi.extension" not in app.config["extensions"]:
        return
    api_dir = app.config["autoapi_root"]
    api_path = build_dir / api_dir
    if not api_path.exists():
        return
    file_names = list(api_path.rglob("*.html"))
    for file_name in file_names:
        with open(api_dir / file_name, "r", encoding="utf-8") as file:
            content = file.read()
        with open(api_dir / file_name, "w", encoding="utf-8") as file:
            modified_content = content.replace("&lt;", "<").replace("&gt;", ">")
            file.write(modified_content)


def add_autoapi_theme_option(app: Sphinx) -> None:
    """Add the autoapi template path to the theme options.

    Parameters
    ----------
    app : ~sphinx.application.Sphinx
        Application instance for rendering the documentation.
    """
    autoapi = app.config.html_theme_options.get("autoapi", {})
    if not autoapi:
        return
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
    app.add_css_file("https://www.nerdfonts.com/assets/css/webfont.css")
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
    relative_autoapi_dir = os.path.relpath(
        autoapi.get("directory", ""), start=str(app.confdir / "conf.py")
    )
    app.config["autoapi_dirs"] = [relative_autoapi_dir]


def setup(app: Sphinx) -> Dict[str, Any]:
    """Add the autoapi extension to the Sphinx application."""
    app.setup_extension("autoapi.extension")
    app.connect("builder-inited", add_autoapi_theme_option, priority=400)
    app.connect("build-finished", replace_html_tag)
    return {
        "version": __version__,
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }
