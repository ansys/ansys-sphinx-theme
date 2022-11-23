"""Sphinx documentation configuration file."""
from datetime import datetime

from sphinx.builders.latex import LaTeXBuilder

LaTeXBuilder.supported_image_types = ["image/png", "image/pdf", "image/svg+xml"]

from ansys_sphinx_theme import (
    __version__,
    ansys_favicon,
    ansys_logo_black,
    ansys_logo_white,
    ansys_logo_white_cropped,
    generate_404,
    latex,
    watermark,
)

# Project information
project = "ansys_sphinx_theme"
copyright = f"(c) {datetime.now().year} ANSYS, Inc. All rights reserved"
author = "Ansys Inc."
release = version = __version__


def get_version_match(semver):
    """Evaluate the version match for the multi-documentation."""
    if semver.endswith("dev0"):
        return "dev"
    major, minor, _ = semver.split(".")
    return ".".join([major, minor])


# use the default ansys logo
html_logo = ansys_logo_black
html_theme = "ansys_sphinx_theme"

html_context = {
    "github_user": "ansys",
    "github_repo": "ansys-sphinx-theme",
    "github_version": "main",
    "doc_path": "doc/source",
}

# specify the location of your github repo
html_theme_options = {
    "github_url": "https://github.com/ansys/ansys-sphinx-theme",
    "use_edit_page_button": True,
    "contact_mail": "pyansys.support@ansys.com",
    "switcher": {
        "json_url": "https://raw.githubusercontent.com/ansys/ansys-templates/gh-pages/release/versions.json",  # noqa: E501
        "version_match": get_version_match(__version__),
    },
    "additional_breadcrumbs": [
        ("Ansys Internal Developer Portal", "https://dev.docs.ansys.com"),
    ],
    "external_links": [
        {
            "url": "https://github.com/ansys/ansys-sphinx-theme/releases",
            "name": "Changelog",
        },
    ],
}

html_short_title = html_title = "Ansys Sphinx Theme"

# Sphinx extensions
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "numpydoc",
    "sphinx.ext.intersphinx",
    "notfound.extension",
    "sphinx_copybutton",
    "ansys_sphinx_theme",
]

# Intersphinx mapping
intersphinx_mapping = {
    "python": ("https://docs.python.org/dev", None),
    # kept here as an example
    # "scipy": ("https://docs.scipy.org/doc/scipy/reference", None),
    # "numpy": ("https://numpy.org/devdocs", None),
    # "matplotlib": ("https://matplotlib.org/stable", None),
    # "pandas": ("https://pandas.pydata.org/pandas-docs/stable", None),
    # "pyvista": ("https://docs.pyvista.org/", None),
}

# numpydoc configuration
numpydoc_show_class_members = False
numpydoc_xref_param_type = True

# Consider enabling numpydoc validation. See:
# https://numpydoc.readthedocs.io/en/latest/validation.html#
numpydoc_validate = True
numpydoc_validation_checks = {
    "GL06",  # Found unknown section
    "GL07",  # Sections are in the wrong order.
    "GL08",  # The object does not have a docstring
    "GL09",  # Deprecation warning should precede extended summary
    "GL10",  # reST directives {directives} must be followed by two colons
    "SS01",  # No summary found
    "SS02",  # Summary does not start with a capital letter
    # "SS03", # Summary does not end with a period
    "SS04",  # Summary contains heading whitespaces
    # "SS05", # Summary must start with infinitive verb, not third person
    "RT02",  # The first line of the Returns section should contain only the
    # type, unless multiple values are being returned"
}

# Favicon
html_favicon = ansys_favicon

# static path
html_static_path = ["_static"]

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# The suffix(es) of source filenames.
source_suffix = ".rst"

# The master toctree document.
master_doc = "index"

# additional logos for the latex coverpage
latex_additional_files = [watermark, ansys_logo_white, ansys_logo_white_cropped]

# change the preamble of latex with customized title page
# variables are the title of pdf, watermark
latex_elements = {"preamble": latex.generate_preamble(html_title)}

# Not found page
notfound_context = {
    "body": generate_404(),
}
notfound_no_urls_prefix = True
