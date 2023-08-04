"""This is the ansys-sphinx-theme module."""
import pathlib
from typing import Any, Dict

from docutils.nodes import document
from sphinx.application import Sphinx

from ansys_sphinx_theme.latex import generate_404  # noqa: F401
from ansys_sphinx_theme.sphinx_link_code_extension import link_code_extension

__version__ = "0.11.dev0"


# Declare the fundamental paths of the theme
THIS_PATH = pathlib.Path(__file__).parent.resolve()
THEME_PATH = THIS_PATH / "theme" / "ansys_sphinx_theme"
STATIC_PATH = THEME_PATH / "static"
STYLE_PATH = STATIC_PATH / "css"
JS_PATH = STATIC_PATH / "js"
CSS_PATH = STYLE_PATH / "ansys_sphinx_theme.css"
TEMPLATES_PATH = THEME_PATH / "_templates"
JS_FILE = JS_PATH / "table.js"

# make logo paths available
ansys_favicon = str((STATIC_PATH / "ansys-favicon.png").absolute())
ansys_logo_black = str((STATIC_PATH / "ansys_logo_black_cropped.jpg").absolute())
ansys_logo_white = str((STATIC_PATH / "ansys_logo_white.pdf").absolute())
ansys_logo_white_cropped = str((STATIC_PATH / "ansys_logo_white_cropped.pdf").absolute())
page_404 = str((STATIC_PATH / "404.rst").absolute())
pyansys_logo_black = str((STATIC_PATH / "pyansys-logo-black-cropped.png").absolute())
pyansys_logo_white = str((STATIC_PATH / "pyansys-logo-white-cropped.png").absolute())
watermark = str((STATIC_PATH / "watermark.pdf").absolute())


def get_html_theme_path() -> pathlib.Path:
    """Return list of HTML theme paths.

    Returns
    -------
    pathlib.Path
        Path pointing to the installation directory of the theme.

    """
    return THEME_PATH.resolve()


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


def convert_version_to_pymeilisearch(semver: str) -> str:
    """Convert a semantic version number to pymeilisearch-compatible format.

    This function evaluates the given semantic version number and returns a
    version number that is compatible with `pymeilisearch`, where dots are
    replaced with hyphens.

    Parameters
    ----------
    semver : str
        Semantic version number in the form of a string.

    Returns
    -------
    str
        pymeilisearch-compatible version number.
    """
    version = get_version_match(semver).replace(".", "-")
    return version


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
    if app.config.html_theme_options.get("switcher"):
        app.config.html_theme_options.setdefault(
            "navbar_end", ["version-switcher", "theme-switcher", "navbar-icon-links"]
        )
    app.config.html_theme_options.setdefault("collapse_navigation", True)


def pv_html_page_context(app, pagename: str, templatename: str, context, doctree) -> None:
    """Add a function that Jinja can access for returning an "edit this page" link .

    This function will create an "edit this page" link for any library.
    The link will point to the corresponding file on the main branch.

    Parameters
    ----------
    app : Sphinx
        The Sphinx application instance for rendering the documentation.

    pagename : str
        The name of the current page.

    templatename : str
        The name of the template being used.

    context : dict
        The context dictionary for the page.

    doctree : document
        The document tree for the page.
    """

    def fix_edit_link_button(link: str) -> str:
        """Transform "edit on GitHub" links to the correct URL.

        This function will create the correct URL for the "edit this page" link.

        Parameters
        ----------
        link : str
            The link to the GitHub edit interface.

        Returns
        -------
        str
            The link to the corresponding file on the main branch.
        """
        github_user = context.get("github_user", "")
        github_repo = context.get("github_repo", "")
        if pagename.startswith("examples") and "index" not in pagename:
            return f"http://github.com/{github_user}/{github_repo}/edit/main/{pagename}.py"
        elif "_autosummary" in pagename:
            # This is an API example
            fullname = pagename.split("_autosummary")[1][1:]
            return link_code_extension.linkcode_resolve(
                "py", {"module": f"{github_repo}", "fullname": fullname}, edit=True
            )
        else:
            return link

    context["fix_edit_link_button"] = fix_edit_link_button


def update_footer_theme(
    app: Sphinx, pagename: str, templatename: str, context: Dict[str, Any], doctree: document
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


def setup(app: Sphinx) -> Dict:
    """Connect to the sphinx theme app.

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

    # Verify that the main CSS file exists
    if not CSS_PATH.exists():
        raise FileNotFoundError(f"Unable to locate ansys-sphinx theme at {CSS_PATH.absolute()}")
    app.add_css_file(str(CSS_PATH.relative_to(STATIC_PATH)))
    app.add_js_file(str(JS_FILE.relative_to(STATIC_PATH)))
    app.add_js_file("https://cdn.datatables.net/1.10.23/js/jquery.dataTables.min.js")
    app.add_css_file("https://cdn.datatables.net/1.10.23/css/jquery.dataTables.min.css")
    app.connect("html-page-context", update_footer_theme)
    # Add templates for autosummary
    app.config.templates_path.append(str(TEMPLATES_PATH))

    return {
        "version": __version__,
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }
