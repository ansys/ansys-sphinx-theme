"""PyData-based Sphinx theme from the PyAnsys community."""
import os
from pathlib import Path

__version__ = "0.3.dev0"

# get location of this directory
_here = Path(__file__).parent.resolve()

# make logo paths available
_static_path = _here / 'theme' / 'pyansys_sphinx_theme' / 'static'
pyansys_logo_black = str(_static_path / 'pyansys-logo-black-cropped.png')
pyansys_logo_white = str(_static_path / 'pyansys-logo-white-cropped.png')
html_logo = pyansys_logo_black


def get_html_theme_path():
    """Return list of HTML theme paths."""
    theme_path = os.path.abspath(os.path.dirname(__file__))
    return [theme_path]


def setup(app):
    theme_path = _here / "theme" / "pyansys_sphinx_theme"
    app.add_html_theme("pyansys_sphinx_theme", str(theme_path))

    # add templates for autosummary
    app.config.templates_path.append(str(theme_path / "_templates"))

    return {
        'version': __version__,
        'parallel_read_safe': True,
        'parallel_write_safe': True,
    }
