"""This is the pyansys-sphinx-theme module."""
import os

from ._version import __version__

# get location of this directory
_this_path = os.path.dirname(os.path.realpath(__file__))

# make logo paths available
pyansys_logo_black = os.path.join(
    _this_path, "static", "pyansys-logo-black-cropped.png"
)
pyansys_logo_white = os.path.join(
    _this_path, "static", "pyansys-logo-white-cropped.png"
)

html_logo = pyansys_logo_black


def get_html_theme_path():
    """Return list of HTML theme paths."""
    theme_path = os.path.abspath(os.path.dirname(__file__))
    return [theme_path]


def setup(app):
    """Connect to the sphinx theme app."""
    theme_path = get_html_theme_path()[0]
    app.add_html_theme("pyansys_sphinx_theme", theme_path)

    # add templates for autosummary
    path_templates = os.path.join(_this_path, "_templates")
    app.config.templates_path.append(path_templates)

    return {
        "version": __version__,
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }
