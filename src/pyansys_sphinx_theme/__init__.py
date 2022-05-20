"""This is the pyansys-sphinx-theme module."""
import os

__version__ = "0.2.dev0"

# get location of this directory
_this_path = os.path.dirname(os.path.realpath(__file__))

# make logo paths available
pyansys_logo_black = os.path.join(_this_path, "static", "pyansys-logo-black-cropped.png")
pyansys_logo_white = os.path.join(_this_path, "static", "pyansys-logo-white-cropped.png")
ansys_favicon = os.path.join(_this_path, "static", "ansys-favicon.png")
ansys_logo_1 = os.path.join(_this_path, "static", "ansys_logo_1.pdf")
ansys_logo_2 = os.path.join(_this_path, "static", "ansys_logo_2.pdf")
drawing = os.path.join(_this_path, "static", "drawing.pdf")

html_logo = pyansys_logo_black


def get_html_theme_path():
    """Return list of HTML theme paths."""
    theme_path = os.path.abspath(os.path.dirname(__file__))
    return [theme_path]


def setup(app):
    """Connect to the sphinx theme app."""
    theme_path = get_html_theme_path()[0]
    app.add_html_theme("pyansys_sphinx_theme", theme_path)
    theme_css_path = os.path.join(theme_path, "static", "css", "pyansys_sphinx_theme.css")
    if not os.path.isfile(theme_css_path):
        raise FileNotFoundError(f"Unable to locate pyansys-sphinx theme at {theme_css_path}")
    app.add_css_file(theme_css_path)

    # add templates for autosummary
    path_templates = os.path.join(_this_path, "_templates")
    app.config.templates_path.append(path_templates)

    return {
        "version": __version__,
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }


latex_elements = {
    "preamble": r"""
\makeatletter
    \renewcommand{\sphinxmaketitle}{%
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
        \sbox{\imagebox}{\includegraphics{drawing}}%
        %
        % put the picture in a zero sized box to get a "background effect"
        % everything else will draw over it
        \hbox to 0in {\vbox to 0in {\usebox{\imagebox}}}
        %
        % how it worked before savebox method
        %\hbox to 0in {\vbox to 0in {\includegraphics{drawing}}} %
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
        \newdimen\myHBoxWidth
        \myHBoxWidth=\hsize \advance\myHBoxWidth-\ansysBlockDistanceFromRightEdge
        % implement the Ansys block
        \hbox to \myHBoxWidth {\vbox to \distanceToBottomOfAnsysBox {}  %
            \hfil
            %
            % draw the box
            \parbox[b]{\ansysBlockWidth}{\raggedleft {
                \includegraphics{ansys_logo_1}} \\
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
        \centerline{\huge \bfseries \@title}
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
                {\includegraphics{ansys_logo_2}} \\
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
}}
\makeatother
""",
}
