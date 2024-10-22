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

"""Module for the Ansys Sphinx theme."""

import logging
import os
import pathlib
import subprocess
from typing import Any, Dict

from docutils import nodes
from sphinx import addnodes
from sphinx.application import Sphinx

from ansys_sphinx_theme.extension.linkcode import DOMAIN_KEYS, sphinx_linkcode_resolve
from ansys_sphinx_theme.latex import generate_404
from ansys_sphinx_theme.search import (
    ALL_NODES,
    PARAGRAPHS,
    TITLES,
    create_search_index,
    update_search_config,
)

try:
    import importlib.metadata as importlib_metadata
except ModuleNotFoundError:  # pragma: no cover
    import importlib_metadata

__version__ = importlib_metadata.version(__name__.replace(".", "-"))


# Declare the fundamental paths of the theme
THIS_PATH = pathlib.Path(__file__).parent.resolve()
THEME_PATH = THIS_PATH / "theme" / "ansys_sphinx_theme"
STATIC_PATH = THEME_PATH / "static"
STYLE_PATH = STATIC_PATH / "css"
JS_PATH = STATIC_PATH / "js"
CSS_PATH = STYLE_PATH / "ansys_sphinx_theme.css"
TEMPLATES_PATH = THEME_PATH / "_templates"
AUTOAPI_TEMPLATES_PATH = TEMPLATES_PATH / "autoapi"
JS_FILE = JS_PATH / "table.js"
LOGOS_PATH = STATIC_PATH / "logos"

ANSYS_LOGO_LINK = "https://www.ansys.com/"
PYANSYS_LOGO_LINK = "https://docs.pyansys.com/"

# make logo paths available
ansys_favicon = str((LOGOS_PATH / "ansys-favicon.png").absolute())
ansys_logo_black = str((LOGOS_PATH / "ansys_logo_black_cropped.jpg").absolute())
ansys_logo_white = str((LOGOS_PATH / "ansys_logo_white.pdf").absolute())
ansys_logo_white_cropped = str((LOGOS_PATH / "ansys_logo_white_cropped.pdf").absolute())
page_404 = str((STATIC_PATH / "404.rst").absolute())
pyansys_logo_black = str((LOGOS_PATH / "pyansys-logo-black-cropped.png").absolute())
pyansys_logo_white = str((LOGOS_PATH / "pyansys-logo-white-cropped.png").absolute())
watermark = str((LOGOS_PATH / "watermark.pdf").absolute())
pyansys_logo_dark_mode = str((LOGOS_PATH / "pyansys_logo_transparent_white.png").absolute())
pyansys_logo_light_mode = str((LOGOS_PATH / "pyansys_logo_transparent_black.png").absolute())
ansys_logo_light_mode = str((LOGOS_PATH / "ansys_logo_transparent_black.png").absolute())
ansys_logo_dark_mode = str((LOGOS_PATH / "ansys_logo_transparent_white.png").absolute())

# Cheat sheet extension version
CHEAT_SHEET_QUARTO_EXTENTION_VERSION = "v1"


def get_html_theme_path() -> pathlib.Path:
    """Return list of HTML theme paths.

    Returns
    -------
    pathlib.Path
        Path pointing to the installation directory of the theme.

    """
    return THEME_PATH.resolve()


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
    return os.path.relpath(str(AUTOAPI_TEMPLATES_PATH.absolute()), start=str(path.absolute()))


def get_version_match(semver: str) -> str:
    """Evaluate the version match for the multi-documentation.

    Parameters
    ----------
    semver : str
        Semantic version number in the form of a string.

    Returns
    -------
    str
        Matching version number in the form of a string.

    """
    if "dev" in semver:
        return "dev"
    major, minor, *_ = semver.split(".")
    return ".".join([major, minor])


def setup_default_html_theme_options(app):
    """Set up the default configuration for the HTML options.

    Parameters
    ----------
    app : ~sphinx.application.Sphinx
        Application instance for rendering the documentation.

    Notes
    -----
    This function is the only way to overwrite ``pydata-sphinx-theme``
    configuration. Variables declared in the ``theme.conf`` do not include
    inherited ones.

    """
    # Place all switchers and icons at the end of the navigation bar
    theme_options = app.config.html_theme_options
    # Place all switchers and icons at the end of the navigation bar
    if theme_options.get("switcher"):
        theme_options.setdefault(
            "navbar_end", ["version-switcher", "theme-switcher", "navbar-icon-links"]
        )
    theme_options.setdefault("collapse_navigation", True)
    theme_options.setdefault("navigation_with_keys", True)

    # Update the icon links. If not given, add a default GitHub icon.
    if not theme_options.get("icon_links") and theme_options.get("github_url"):
        theme_options["icon_links"] = [
            {
                "name": "GitHub",
                "url": theme_options["github_url"],
                "icon": "fa-brands fa-github",
            }
        ]
        theme_options["github_url"] = None

    # Add default pygments style options
    if not theme_options.get("pygments_light_style"):
        theme_options["pygments_light_style"] = "friendly"
    if not theme_options.get("pygments_dark_style"):
        theme_options["pygments_dark_style"] = "monokai"


def fix_edit_html_page_context(
    app: Sphinx, pagename: str, templatename: str, context: dict, doctree: nodes.document
) -> None:
    """Add a function that Jinja can access for returning an "edit this page" link .

    This function creates an "edit this page" link for any library.
    The link points to the corresponding file on the main branch.

    Parameters
    ----------
    app : Sphinx
        Sphinx application instance for rendering the documentation.
    pagename : str
        Name of the current page.
    templatename : str
        Name of the template being used.
    context : dict
        Context dictionary for the page.
    doctree : document
        Document tree for the page.

    Notes
    -----
    [1] Originally implemented by `Alex Kaszynski <https://github.com/akaszynski>`_ in
    `PyVista <https://github.com/pyvista/pyvista>`_ ,
    see https://github.com/pyvista/pyvista/pull/4113
    """

    def fix_edit_link_page(link: str) -> str:
        """Transform "edit on GitHub" links to the correct URL.

        This function fixes the URL for the "edit this page" link.

        Parameters
        ----------
        link : str
            Link to the GitHub edit interface.

        Returns
        -------
        str
            Link to the corresponding file on the main branch.
        """
        github_user = context.get("github_user", "")
        github_repo = context.get("github_repo", "")
        github_source = context.get("source_path", "")
        kind = context.get("github_version", "")

        if "_autosummary" in pagename:
            for obj_node in list(doctree.findall(addnodes.desc)):
                try:
                    domain = obj_node.get("domain")
                    for signode in obj_node:
                        if not isinstance(signode, addnodes.desc_signature):
                            continue
                        # Convert signode to a specified format
                        info = {}
                        for key in DOMAIN_KEYS.get(domain, []):
                            value = signode.get(key)
                            if not value:
                                value = ""
                            info[key] = value
                        if not info:
                            continue
                        # This is an API example
                        return sphinx_linkcode_resolve(
                            domain=domain,
                            info=info,
                            library=f"{github_user}/{github_repo}",
                            source_path=github_source,
                            github_version=kind,
                            edit=True,
                        )
                except ValueError as e:
                    logging.debug(f"An error occurred: {e}")  # Log the exception as debug info
                    return link

        elif "api" in pagename:
            for obj_node in list(doctree.findall(addnodes.desc)):
                domain = obj_node.get("domain")
                if domain != "py":
                    return link

                for signode in obj_node:
                    if not isinstance(signode, addnodes.desc_signature):
                        continue

                    fullname = signode["fullname"]
                    modname = fullname.replace(".", "/")

                    if github_source:
                        return f"http://github.com/{github_user}/{github_repo}/edit/{kind}/{github_source}/{modname}.{domain}"  # noqa: E501
                    else:
                        return f"http://github.com/{github_user}/{github_repo}/edit/{kind}/{modname}.{domain}"  # noqa: E501

        else:
            return link

    context["fix_edit_link_page"] = fix_edit_link_page


def update_footer_theme(
    app: Sphinx, pagename: str, templatename: str, context: Dict[str, Any], doctree: nodes.document
) -> None:
    """Update the version number of the Ansys Sphinx theme in the footer.

    Connect to the Sphinx application instance for rendering the documentation,
    and add the current version number of the Ansys Sphinx theme to the page context.
    This allows the theme to update the footer with the current version number.

    Parameters
    ----------
    app : ~sphinx.application.Sphinx
        Application instance for rendering the documentation.
    pagename : str
        The name of the current page.
    templatename : str
        The name of the template being used.
    context : dict
        The context dictionary for the page.
    doctree : ~docutils.nodes.document
        The document tree for the page.
    """
    context["ansys_sphinx_theme_version"] = __version__


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
    defined_extensions = app.config["extensions"]
    if not any(
        extension in defined_extensions
        for extension in ["autoapi.extension", "ansys_sphinx_theme.extension.autoapi"]
    ):
        return
    api_dir = app.config["autoapi_root"]
    api_path = build_dir / api_dir
    if not api_path.exists():
        return

    file_names = list(api_path.rglob("*.html"))
    for file_name in file_names:
        with pathlib.Path.open(api_dir / file_name, "r", encoding="utf-8") as file:
            content = file.read()
        with pathlib.Path.open(api_dir / file_name, "w", encoding="utf-8") as file:
            modified_content = content.replace("&lt;", "<").replace("&gt;", ">")
            file.write(modified_content)


def configure_theme_logo(app: Sphinx):
    """
    Configure the theme logo based on the theme options.

    Parameters
    ----------
    app : sphinx.application.Sphinx
        Application instance for rendering the documentation.
    """
    # Define logo configurations
    pyansys_logo = {
        "image_dark": pyansys_logo_dark_mode,
        "image_light": pyansys_logo_light_mode,
    }

    ansys_logo = {
        "image_dark": ansys_logo_dark_mode,
        "image_light": ansys_logo_light_mode,
    }
    theme_options = app.config.html_theme_options
    logo_option = theme_options.get("logo")

    if not logo_option:
        theme_options["logo"] = pyansys_logo

    if isinstance(logo_option, str) and logo_option not in {"ansys", "pyansys", "no_logo"}:
        raise ValueError(
            f"Invalid logo option: '{logo_option}'. The logo option must be either 'ansys', 'pyansys', or 'no_logo'"  # noqa: E501
        )

    if logo_option == "ansys":
        theme_options["logo"] = ansys_logo
        theme_options["logo_link"] = theme_options.get("logo_link", ANSYS_LOGO_LINK)
    elif logo_option == "pyansys":
        theme_options["logo"] = pyansys_logo
        theme_options["logo_link"] = theme_options.get("logo_link", PYANSYS_LOGO_LINK)
    elif logo_option == "no_logo":
        theme_options["logo"] = None

    elif isinstance(logo_option, dict):
        theme_options["logo"] = logo_option


def convert_pdf_to_png(pdf_path: pathlib.Path, output_dir: pathlib.Path, output_png: str):
    """
    Convert PDF to PNG images.

    Parameters
    ----------
    pdf_path : pathlib.Path
        Path to the PDF file.
    output_dir : pathlib.Path
        Path to the output directory.
    output_png : str
        Name of the output PNG file.
    """
    try:
        from pdf2image import convert_from_path
    except ImportError as e:
        raise ImportError(
            f"Failed to import `pdf2image`: {e}. Install the package using `pip install pdf2image`"  # noqa: E501
        )
    try:
        images = convert_from_path(pdf_path, 500)
        images[0].save(output_dir / output_png, "PNG")
    except Exception as e:
        raise RuntimeError(
            f"Failed to convert PDF to PNG: {e}, ensure `poppler` is installed. See https://pypi.org/project/pdf2image/"  # noqa: E501
        )


def add_cheat_sheet(
    app: Sphinx, pagename: str, templatename: str, context: Dict[str, Any], doctree: nodes.document
) -> None:
    """Add a cheat sheet to the left navigation sidebar.

    Parameters
    ----------
    app : ~sphinx.application.Sphinx
        Application instance for rendering the documentation.
    pagename : str
        Name of the current page.
    templatename : str
        Name of the template being used.
    context : dict
        Context dictionary for the page.
    doctree : ~docutils.nodes.document
        The doctree.
    """
    cheatsheet_options = app.config.html_theme_options.get("cheatsheet", {})
    pages = cheatsheet_options.get("pages", ["index"])
    pages = [pages] if isinstance(pages, str) else pages
    if cheatsheet_options and any(pagename == page for page in pages):
        sidebar = context.get("sidebars", [])
        sidebar.append("cheatsheet_sidebar.html")
        context["sidebars"] = sidebar


def build_quarto_cheatsheet(app: Sphinx):
    """
    Build the Quarto cheatsheet.

    Parameters
    ----------
    app : sphinx.application.Sphinx
        Application instance for rendering the documentation.
    """
    cheatsheet_options = app.config.html_theme_options.get("cheatsheet", {})

    if not cheatsheet_options:
        return

    cheatsheet_file = cheatsheet_options.get("file", "")
    output_dir = "_static"
    version = cheatsheet_options.get("version", "main")

    if not cheatsheet_file:
        return

    cheatsheet_file = pathlib.Path(app.srcdir) / cheatsheet_file
    file_name = str(cheatsheet_file.name)
    file_path = cheatsheet_file.parent
    output_dir_path = pathlib.Path(app.outdir) / output_dir
    try:
        # Add the cheatsheet to the Quarto project
        subprocess.run(
            [
                "quarto",
                "add",
                f"ansys/pyansys-quarto-cheatsheet@{CHEAT_SHEET_QUARTO_EXTENTION_VERSION}",
                "--no-prompt",
            ],
            cwd=file_path,
            capture_output=True,
            text=True,
        )

        # Render the cheatsheet
        subprocess.run(
            [
                "quarto",
                "render",
                file_name,
                "--to",
                "cheat_sheet-pdf",
                "--output-dir",
                output_dir_path,
                "-V",
                f"version={version}",
            ],
            cwd=file_path,
            capture_output=True,
            text=True,
        )

        # Remove the cheatsheet from the Quarto project
        subprocess.run(
            ["quarto", "remove", "ansys/cheat_sheet", "--no-prompt"],
            cwd=file_path,
            capture_output=True,
            text=True,
        )

        # Remove all supplementary files
        supplementary_files = [
            "_static/slash.png",
            "_static/bground.png",
            "_static/ansys.png",
        ]
        for file in supplementary_files:
            file_path = cheatsheet_file.parent / file
            if file_path.exists():
                file_path.unlink()

        # If static folder is clean, delete it
        if not list(cheatsheet_file.parent.glob("_static/*")):
            cheatsheet_file.parent.joinpath("_static").rmdir()

    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Failed to build Quarto cheatsheet: {e}. Ensure Quarto is installed.")

    output_file = output_dir_path / file_name.replace(".qmd", ".pdf")
    app.config.html_theme_options["cheatsheet"]["output_dir"] = f"{output_dir}/{output_file.name}"
    output_png = file_name.replace(".qmd", ".png")
    convert_pdf_to_png(output_file, output_dir_path, output_png)
    app.config.html_theme_options["cheatsheet"]["thumbnail"] = f"{output_dir}/{output_png}"


def check_for_depreciated_theme_options(app: Sphinx):
    """Check for depreciated theme options.

    Parameters
    ----------
    app : sphinx.application.Sphinx
        Application instance for rendering the documentation.
    """
    theme_options = app.config.html_theme_options
    if "use_meilisearch" in theme_options:
        raise DeprecationWarning(
            "The 'use_meilisearch' option is deprecated. Remove the option from your configuration file."  # noqa: E501
        )


def setup(app: Sphinx) -> Dict:
    """Connect to the Sphinx theme app.

    Parameters
    ----------
    app : ~sphinx.application.Sphinx
        Application instance for rendering the documentation.

    Returns
    -------
    Dict
        Dictionary containing application status.

    """
    # Add the theme configuration
    theme_path = get_html_theme_path()
    app.add_html_theme("ansys_sphinx_theme", theme_path)
    app.config.templates_path.append(str(THEME_PATH / "components"))

    # Add default HTML configuration
    setup_default_html_theme_options(app)

    update_search_config(app)

    # Verify that the main CSS file exists
    if not CSS_PATH.exists():
        raise FileNotFoundError(f"Unable to locate ansys-sphinx theme at {CSS_PATH.absolute()}")
    app.add_css_file(str(CSS_PATH.relative_to(STATIC_PATH)))
    app.add_js_file(str(JS_FILE.relative_to(STATIC_PATH)))
    app.config.templates_path.append(str(TEMPLATES_PATH))
    app.add_js_file("https://cdn.datatables.net/1.10.23/js/jquery.dataTables.min.js")
    app.add_css_file("https://cdn.datatables.net/1.10.23/css/jquery.dataTables.min.css")
    app.add_css_file("https://www.nerdfonts.com/assets/css/webfont.css")
    app.connect("builder-inited", configure_theme_logo)
    app.connect("builder-inited", build_quarto_cheatsheet)
    app.connect("builder-inited", check_for_depreciated_theme_options)
    app.connect("html-page-context", update_footer_theme)
    app.connect("html-page-context", fix_edit_html_page_context)
    app.connect("html-page-context", add_cheat_sheet)
    app.connect("build-finished", replace_html_tag)
    app.connect("build-finished", create_search_index)
    return {
        "version": __version__,
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }


__all__ = ["__version__", "generate_404", "get_version_match", "TITLEs", "PARAGRAPHS", "ALL_NODES"]
