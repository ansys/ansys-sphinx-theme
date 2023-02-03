"""This is the ansys-sphinx-theme module."""
import pathlib
from typing import Dict

import sphinx

from ansys_sphinx_theme.latex import generate_404  # noqa: F401

__version__ = "0.9.dev0"


# Declare the fundamental paths of the theme
THIS_PATH = pathlib.Path(__file__).parent.resolve()
THEME_PATH = THIS_PATH / "theme" / "ansys_sphinx_theme"
STATIC_PATH = THEME_PATH / "static"
STYLE_PATH = STATIC_PATH / "css"
CSS_PATH = STYLE_PATH / "ansys_sphinx_theme.css"
TEMPLATES_PATH = THEME_PATH / "_templates"

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
    if semver.endswith("dev0"):
        return "dev"
    major, minor, _ = semver.split(".")
    return ".".join([major, minor])


def setup_default_html_theme_options(app):
    """Set up the default configuration for the HTML options.

    Parameters
    ----------
    app : sphinx.application.Sphinx
        Application instance for rendering the documentation.

    Notes
    -----
    This function is the only way to overwrite ``pydata-sphinx-theme``
    configuration. Variables declared in the ``theme.conf`` do not include
    inherited ones.

    """
    # Place all switchers and icons at the end of the navigation bar
    app.config.html_theme_options.setdefault(
        "navbar_end", ["version-switcher", "theme-switcher", "navbar-icon-links"]
    )


def setup(app: sphinx.application.Sphinx) -> Dict:
    """Connect to the sphinx theme app.

    Parameters
    ----------
    app : sphinx.application.Sphinx
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

    # Add templates for autosummary
    app.config.templates_path.append(str(TEMPLATES_PATH))

    return {
        "version": __version__,
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }
