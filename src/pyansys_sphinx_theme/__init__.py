"""This is the pyansys-sphinx-theme module."""
import os
from pathlib import Path

__version__ = "0.3.1"

# get location of this directory
_this_path = os.path.dirname(os.path.realpath(__file__))

# make logo paths available
pyansys_logo_black = os.path.join(_this_path, "static", "pyansys-logo-black-cropped.png")
pyansys_logo_white = os.path.join(_this_path, "static", "pyansys-logo-white-cropped.png")
ansys_favicon = os.path.join(_this_path, "static", "ansys-favicon.png")
ansys_logo_white = os.path.join(_this_path, "static", "ansys_logo_white.pdf")
ansys_logo_white_cropped = os.path.join(_this_path, "static", "ansys_logo_white_cropped.pdf")
watermark = os.path.join(_this_path, "static", "watermark.pdf")

html_logo = pyansys_logo_black

CSS_FILENAME = "pyansys_sphinx_theme.css"


def get_html_theme_path():
    """Return list of HTML theme paths."""
    return Path(__file__).parents[0].absolute()


def setup(app):
    """Connect to the sphinx theme app."""
    theme_path = get_html_theme_path()
    app.add_html_theme("pyansys_sphinx_theme", theme_path)
    theme_css_path = theme_path / "static" / "css" / CSS_FILENAME
    if not theme_css_path.exists():
        raise FileNotFoundError(f"Unable to locate pyansys-sphinx theme at {theme_css_path}")
    app.add_css_file(str(theme_css_path.relative_to(theme_path / "static")))

    # add templates for autosummary
    path_templates = os.path.join(_this_path, "_templates")
    app.config.templates_path.append(path_templates)

    return {
        "version": __version__,
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }
