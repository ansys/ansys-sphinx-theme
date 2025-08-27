# Copyright (C) 2021 - 2025 ANSYS, Inc. and/or its affiliates.
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

import os
import pathlib
import re
from typing import Any

from docutils import nodes
from pydata_sphinx_theme.toctree import traverse_or_findall
from sphinx import addnodes
from sphinx.addnodes import toctree
from sphinx.application import Sphinx
from sphinx.util import logging

from ansys_sphinx_theme.cheatsheet import build_quarto_cheatsheet, cheatsheet_sidebar_pages
from ansys_sphinx_theme.extension.linkcode import DOMAIN_KEYS, sphinx_linkcode_resolve
from ansys_sphinx_theme.latex import generate_404
from ansys_sphinx_theme.navbar_dropdown import load_navbar_configuration, update_template_context
from ansys_sphinx_theme.search import (
    create_search_index,
    update_search_config,
)
from ansys_sphinx_theme.whatsnew import (
    add_whatsnew_changelog,
    extract_whatsnew,
    get_whatsnew_options,
    whatsnew_sidebar_pages,
)

try:
    import importlib.metadata as importlib_metadata
except ModuleNotFoundError:  # pragma: no cover
    import importlib_metadata

__version__ = importlib_metadata.version(__name__.replace(".", "-"))
logger = logging.getLogger(__name__)


# Declare the fundamental paths of the theme
THIS_PATH = pathlib.Path(__file__).parent.resolve()
THEME_PATH = THIS_PATH / "theme" / "ansys_sphinx_theme"
STATIC_PATH = THEME_PATH / "static"
STYLE_PATH = STATIC_PATH / "styles"
JS_PATH = STATIC_PATH / "js"
CSS_PATH = STYLE_PATH / "ansys-sphinx-theme.css"
TEMPLATES_PATH = THEME_PATH / "_templates"
AUTOAPI_TEMPLATES_PATH = TEMPLATES_PATH / "autoapi"
LOGOS_PATH = STATIC_PATH / "logos"

ANSYS_LOGO_LINK = "https://www.ansys.com/"
PYANSYS_LOGO_LINK = "https://docs.pyansys.com/"

PACKAGE_HOME_HTML_PATTERN = re.compile(r'<a([^>]*?)href="[^"]*index\.html"([^>]*?)>\s*Home\s*</a>')


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
            "navbar_end",
            ["search-button-field", "version-switcher", "theme-switcher", "navbar-icon-links"],
        )

    # HACK: Add the search button field to the navbar_end and insert it at the beginning of
    # the list. This is a workaround to ensure the search button field is always present
    if "navbar_end" in theme_options:
        if "search-button-field" not in theme_options["navbar_end"]:
            theme_options["navbar_end"].insert(0, "search-button-field")
        logging.getLogger(__name__).info(
            "The 'search-button-field' has been added to the 'navbar_end' in the theme options."
        )
    theme_options.setdefault("navbar_persistent", [])
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
                    logger.error(f"An error occurred: {e}")  # Log the exception as debug info
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
    app: Sphinx, pagename: str, templatename: str, context: dict[str, Any], doctree: nodes.document
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
        # Ansys logo should link to the ANSYS homepage
        theme_options["logo_link"] = ANSYS_LOGO_LINK
    elif logo_option == "pyansys":
        theme_options["logo"] = pyansys_logo
        # PyAnsys logo should link to the PyAnsys Meta documentation
        theme_options["logo_link"] = PYANSYS_LOGO_LINK
    elif logo_option == "no_logo":
        theme_options["logo"] = None

    elif isinstance(logo_option, dict):
        theme_options["logo"] = logo_option


def add_sidebar_context(
    app: Sphinx, pagename: str, templatename: str, context: dict, doctree: nodes.document
) -> None:
    """Add the sidebar context to the page.

    This function adds the sidebar context to the page. The sidebar context
    includes the sidebar pages for the cheatsheet and what's new sections.
    `whatsnew_sidebar_pages` and `cheatsheet_sidebar_pages` are used to determine
    the pages to display the sidebar.

    Parameters
    ----------
    app : sphinx.application.Sphinx
        Application instance for rendering the documentation.
    pagename : str
        Name of the current page.
    templatename : str
        Name of the template being used.
    context : dict
        Context dictionary for the page.
    doctree : docutils.nodes.document
        Document tree for the page.
    """
    whatsnew_pages = whatsnew_sidebar_pages(app)
    cheatsheet_pages = cheatsheet_sidebar_pages(app)

    if not whatsnew_pages and not cheatsheet_pages:
        return

    sidebar = context.get("sidebars", [])

    sidebar_mapping = {"cheatsheet": "cheatsheet_sidebar.html", "whatsnew": "whatsnew_sidebar.html"}

    sidebars_to_add = []

    if cheatsheet_pages and pagename in cheatsheet_pages:
        sidebars_to_add.append("cheatsheet")

    if whatsnew_pages and pagename in whatsnew_pages:
        whatsnew = context.get("whatsnew", [])
        whatsnew.extend(app.env.whatsnew)
        context["whatsnew"] = whatsnew
        sidebars_to_add.append("whatsnew")

    # Append sidebars

    for item in sidebars_to_add:
        if sidebar_mapping[item] not in sidebar:
            sidebar.append(sidebar_mapping[item])

    # Update the sidebar context
    context["sidebars"] = sidebar


def update_search_sidebar_context(
    app: Sphinx, pagename: str, templatename: str, context: dict, doctree: nodes.document
) -> None:
    """Update the search sidebar context.

    This function updates the search sidebar context with the search index
    and the search options.

    Parameters
    ----------
    app : sphinx.application.Sphinx
        Application instance for rendering the documentation.
    pagename : str
        Name of the current page.
    templatename : str
        Name of the template being used.
    context : dict
        Context dictionary for the page.
    doctree : docutils.nodes.document
        Document tree for the page.
    """
    sidebar = context.get("sidebars", [])
    if pagename == "search" and "search_sidebar.html" not in sidebar:
        sidebar.append("search_sidebar.html")

    # Update the sidebar context
    context["sidebars"] = sidebar


def on_doctree_resolved(app: Sphinx, doctree: nodes.document, docname: str) -> None:
    """Add a 'Home' entry to the root TOC.

    Parameters
    ----------
    app : Sphinx
        Sphinx application instance for rendering the documentation.
    doctree : nodes.document
        Document tree for the page.
    docname : str
        Name of the current document.

    Notes
    -----
    This function checks if the 'Home' entry already exists in the root TOC.
    If it does not exist, it adds the 'Home' entry at the beginning of the TOC.
    The 'Home' entry links to the index page of the documentation.
    """
    index_page = app.config.root_doc or app.config.master_doc or "index"
    root_toc = app.env.tocs[app.config.root_doc]
    for toc in traverse_or_findall(root_toc, toctree):
        if not toc.attributes.get("entries"):
            return

        for title, page in toc.attributes["entries"]:
            if title == "Home":
                return

        home_entry = (
            nodes.Text("Home"),
            index_page if index_page != docname else None,
        )
        # Insert 'Home' entry at the beginning of the TOC
        toc.attributes["entries"].insert(0, home_entry)


def add_tooltip_after_build(app: Sphinx, exception):
    """Add tooltips to 'Home' links after the build process.

    Parameters
    ----------
    app : Sphinx
        Sphinx application instance for rendering the documentation.
    exception : Exception
        Exception raised during the build process.

    Returns
    -------
    None
    """
    if exception:
        return

    outdir = pathlib.Path(app.outdir)

    project_name = "Package Home"

    if app.config.html_short_title:
        project_name = f"{app.config.html_short_title} home"
    elif app.config.project:
        project_name = f"{app.config.project} home"

    for html_file in outdir.rglob("*.html"):
        text = html_file.read_text(encoding="utf-8")

        def replacer(match):
            attrs_before, attrs_after = match.groups()
            full_attrs = f"{attrs_before}{attrs_after}"
            if "title=" in full_attrs:
                return match.group(0)  # don't duplicate title
            return f'<a{attrs_before}href="index.html"{attrs_after} title="{project_name}">\n    Home\n</a>'  # noqa: E501

        new_text = PACKAGE_HOME_HTML_PATTERN.sub(replacer, text)

        if new_text != text:
            html_file.write_text(new_text, encoding="utf-8")


def setup(app: Sphinx) -> dict:
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
    load_navbar_configuration(app)

    # Check for what's new options in the theme configuration
    whatsnew_file, changelog_file = get_whatsnew_options(app)

    use_ansys_search = app.config.html_theme_options.get("use_ansys_search", True)
    if use_ansys_search:
        update_search_config(app)
    if not CSS_PATH.exists():
        raise FileNotFoundError(f"Unable to locate ansys-sphinx theme at {CSS_PATH.absolute()}")
    app.add_css_file(str(CSS_PATH.relative_to(STATIC_PATH)))
    app.config.templates_path.append(str(TEMPLATES_PATH))
    app.add_js_file("https://cdn.datatables.net/1.10.23/js/jquery.dataTables.min.js")
    app.add_css_file("https://cdn.datatables.net/1.10.23/css/jquery.dataTables.min.css")
    app.add_css_file("https://www.nerdfonts.com/assets/css/webfont.css")
    app.connect("builder-inited", configure_theme_logo)
    app.connect("builder-inited", build_quarto_cheatsheet)

    if whatsnew_file and changelog_file:
        app.connect("doctree-read", add_whatsnew_changelog)
        app.connect("doctree-resolved", extract_whatsnew)
    app.connect("html-page-context", add_sidebar_context)
    app.connect("html-page-context", update_footer_theme)
    app.connect("html-page-context", fix_edit_html_page_context)
    app.connect("html-page-context", update_search_sidebar_context)
    app.connect("html-page-context", update_template_context)
    app.connect("doctree-resolved", on_doctree_resolved)

    app.connect("build-finished", replace_html_tag)
    app.connect("build-finished", add_tooltip_after_build)
    if use_ansys_search:
        app.connect("build-finished", create_search_index)

    return {
        "version": __version__,
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }


__all__ = [
    "__version__",
    "generate_404",
    "get_version_match",
]
