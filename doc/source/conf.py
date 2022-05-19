"""Sphinx documentation configuration file."""
from datetime import datetime

from sphinx.builders.latex import LaTeXBuilder

LaTeXBuilder.supported_image_types = ["image/png", "image/pdf", "image/svg+xml"]

from pyansys_sphinx_theme import __version__, ansys_favicon, pyansys_logo_black

# Project information
project = "pyansys_sphinx_theme"
copyright = f"(c) {datetime.now().year} ANSYS, Inc. All rights reserved"
author = "Ansys Inc."
release = version = __version__

# use the default pyansys logo
html_logo = pyansys_logo_black
html_theme = "pyansys_sphinx_theme"

# specify the location of your github repo
html_theme_options = {
    "github_url": "https://github.com/pyansys/pyansys-sphinx-theme",
    "additional_breadcrumbs": [
        ("PyAnsys", "https://docs.pyansys.com/"),
    ],
}

html_short_title = html_title = "PyAnsys Sphinx Theme"

# Sphinx extensions
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "numpydoc",
    "sphinx.ext.intersphinx",
    "sphinx_copybutton",
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

# change the preamble of latex with customized title page
latex_elements = {
    "sphinxsetup": "",
    "passoptionstopackages": r"""
    \PassOptionsToPackage{table}{xcolor}""",
    "preamble": r"""\renewcommand{\sphinxmaketitle}{%
    \newsavebox\imagebox
    \newsavebox\myTitle
    % native LaTeX command. Specifies a page with no formatting.
    % Page number restarts after this page
    \begin{titlepage}
    % san serif
    \sffamily
    %
    % set to 0 so that we don't have any blank space at the top of the page
    \topskip0pt
    %
    % removes all margins
    \advance\voffset -1in %
    \advance\hoffset -1in %
    \advance\vsize 2in %
    \advance\hsize 2in %
    %
    % load the graphics into a LaTeX (not TeX) "savebox". We use this load
    % to obtain the height later, and to insert it into the doc later
    \sbox{\imagebox}{\includegraphics{../../drawing.pdf}}%
    %
    % put the picture in a zero sized box to get a "background effect"
    % everything else will draw over it
    \hbox to 0in {\vbox to 0in {\usebox{\imagebox}}}
    %
    % how it worked before savebox method
    %\hbox to 0in {\vbox to 0in {\includegraphics{../../drawing.pdf}}} %
    % Where the right boundary of the title block goes
    %
    % Define "ansysBlockWidth" <-- exactly what its name implies
    \newdimen\ansysBlockWidth\ansysBlockWidth = 3in %
    % Define "ansysBlockDistanceFromRightEdge" <-- exactly what its name implies
    \newdimen\ansysBlockDistanceFromRightEdge \ansysBlockDistanceFromRightEdge = 0.5in %
    % Define "distanceToBottomOfAnsysBox" <-- length from top of page to bottom of title box
    \newdimen\distanceToBottomOfAnsysBox %
    \distanceToBottomOfAnsysBox=\ht\imagebox %
    \advance\distanceToBottomOfAnsysBox -\lineskip %
    \advance\distanceToBottomOfAnsysBox -0.125in %
    % Define "myHBoxWidth" <-- distance from left edge of page to right edge Ansys box
    \newdimen\myHBoxWidth \myHBoxWidth=\hsize \advance\myHBoxWidth-\ansysBlockDistanceFromRightEdge
    % implement the Ansys block
    \hbox to \myHBoxWidth {\vbox to \distanceToBottomOfAnsysBox {}  %
        \hfil
        %
        % draw the box
        \parbox[b]{\ansysBlockWidth}{\raggedleft {
            \includegraphics{../../logo-1.pdf}} \\
            \footnotesize
            \textcolor{lightgray}
            \hrule
            \vskip 6pt
            \textcopyright{} 2022 ANSYS, Inc. or affiliated companies\\
            Unauthorized use, distribution, or duplication prohibited.}
    } %
    %we use a save box method so that we can get draw the bottom material with respect
    %to the bottom of the page
    \sbox{\myTitle}{\vbox{
    %vskip skips down a specified distance from the previous Ansys block and picture
    \vskip 1in
    %title
    \centerline{\huge \bfseries PyAnsys Developer's Guide}
    \vskip 6pt
    %line under title
    \centerline{\vrule height 0.0625in  width 6.5in}
    }
    }
    \usebox{\myTitle} \\%
    \newdimen\toBottom%
    %trying to calculate distance from the bottom of the line under the title
    %to the bottom of the page, used to construct a strut (0 width vbox)
    \toBottom=\vsize%
    \advance\toBottom -\ht\myTitle %
    \advance\toBottom -\distanceToBottomOfAnsysBox%
    \advance\toBottom -\baselineskip%
    \advance\toBottom -\lineskip%
    \advance\toBottom -0.5in
    \hbox to \hsize{%
        %0 width vbox (empty vbox)
        \vbox to \toBottom {}%
        %distance from the left side
        \hskip 1in%
        %left block
        \parbox[b]{2in}{
            {\includegraphics{../../logo-2.pdf}} \\
            ANSYS, Inc.\\
            Southpointe\\
            2600 Ansys Drive\\
            Canonsburg, PA 15317\\
            \href{mailto:ansysinfo@ansys.com}{ansysinfo@ansys.com}\\
            \url{http://www.ansys.com}\\
            (T) 724-746-3304\\
            (F) 724-514-9494
        }%
        \hfil%
        %hfil pushes the right box to the right
        %we needed the vbox since we are stacking two objects on the right side
        \vbox{\hbox {December 2021} \vskip 0.5\baselineskip%\footnotesize
        %fbox is a horizontal box, so we need to put a vbox in it to get multiple lines.
        %the fbox is wrapped in an hbox so we can control where it goes.
        %we stack the hboxes in the vbox. We need the hboxes because otherwise the fbox had
        %a huge width
            \hbox{\fbox{\vbox{\hbox{ANSYS, Inc. and}\hbox{ANSYS Europe,}
            \hbox{Ltd. are UL}\hbox{registered ISO}\hbox{9001:2015}\hbox{companies.}}}}%
        }
        %1in of space between the right box and the right edge of the page
        \hskip 1in%
    }
    \end{titlepage}
}}""",
}
