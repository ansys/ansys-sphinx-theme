from pyansys_sphinx_theme import __version__

# Project information
project = 'pyansys_sphinx_theme'
copyright = '2021, ANSYS'
author = 'PyAnsys Open Source Developers'
release = version = __version__

# optionally the default pyansys logo
html_logo = 'https://docs.pyansys.com/_static/pyansys-logo-black-cropped.png'

# Sphinx extensions
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
    'sphinx.ext.autosummary',
]

# The suffix(es) of source filenames.
source_suffix = '.rst'

# The master toctree document.
master_doc = 'index'

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = 'pyansys_sphinx_theme'
