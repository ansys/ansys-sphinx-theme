"""Sphinx documentation configuration file."""

import copy
from datetime import datetime
from functools import lru_cache
import os
import pathlib
from pathlib import Path
import subprocess
from typing import Dict, List, Union

import bs4
from docutils import nodes
from github import Github
import plotly.io as pio
from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import PythonLexer
import pyvista
import requests
import sphinx
from sphinx.application import Sphinx
from sphinx.builders.latex import LaTeXBuilder
import sphinx.config
from sphinx.util.nodes import make_refnode
import yaml

from ansys_sphinx_theme import (
    ALL_NODES,
    PARAGRAPHS,
    TITLES,
    __version__,
    ansys_favicon,
    ansys_logo_white,
    ansys_logo_white_cropped,
    generate_404,
    get_version_match,
    latex,
    watermark,
)

pio.renderers.default = "sphinx_gallery"
THIS_PATH = Path(__file__).parent.resolve()
PYANSYS_LIGHT_SQUARE = (THIS_PATH / "_static" / "pyansys_light_square.png").resolve()
EXAMPLE_PATH = (THIS_PATH / "examples" / "sphinx_examples").resolve()

# Project information
project = "ansys_sphinx_theme"
copyright = f"(c) {datetime.now().year} ANSYS, Inc. All rights reserved"
author = "ANSYS, Inc."
release = version = __version__
cname = os.getenv("DOCUMENTATION_CNAME", "sphinxdocs.ansys.com")
switcher_version = get_version_match(__version__)

# HTML configuration
html_favicon = ansys_favicon
html_theme = "ansys_sphinx_theme"
html_short_title = html_title = "Ansys Sphinx Theme"
html_static_path = ["_static"]
templates_path = ["_templates"]

html_context = {
    "github_user": "ansys",
    "github_repo": "ansys-sphinx-theme",
    "github_version": "main",
    "doc_path": "doc/source",
    "page_assets": {
        "examples/table": {
            "needs_datatables": True,
        },
    },
}

html_theme_options = {
    "github_url": "https://github.com/ansys/ansys-sphinx-theme",
    "contact_mail": "pyansys.support@ansys.com",
    "use_edit_page_button": True,
    "additional_breadcrumbs": [
        ("PyAnsys", "https://docs.pyansys.com/"),
    ],
    "switcher": {
        "json_url": f"https://{cname}/versions.json",
        "version_match": get_version_match(__version__),
    },
    "logo": "ansys",
    "static_search": {
        "threshold": 0.2,
        "limit": 7,
        "minMatchCharLength": 3,
    },
    "navbar_center": ["navbar-links"],
}

html_js_files = ["https://cdn.plot.ly/plotly-3.0.1.min.js"]


index_patterns = {
    "examples/api/": ALL_NODES,
    "examples/sphinx_examples/": TITLES + PARAGRAPHS,
}


# Sphinx extensions
extensions = [
    "numpydoc",
    "sphinx_design",
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.intersphinx",
    "sphinx.ext.todo",
    "sphinx_copybutton",
    "sphinx.ext.intersphinx",
    "sphinx.ext.todo",
    "notfound.extension",
    "sphinx_jinja",
]

# Intersphinx mapping
intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    "sphinx": ("https://www.sphinx-doc.org/en/master", None),
}

# numpydoc configuration
numpydoc_show_class_members = False
numpydoc_xref_param_type = True
numpydoc_validate = True
numpydoc_validation_checks = {
    "GL06",  # Found unknown section
    "GL07",  # Sections are in the wrong order.
    "GL09",  # Deprecation warning should precede extended summary
    "GL10",  # reST directives {directives} must be followed by two colons
    "SS01",  # No summary found
    "SS02",  # Summary does not start with a capital letter
    "SS04",  # Summary contains heading whitespaces
    "RT02",  # The first line of the Returns section should contain only the type
}

suppress_warnings = ["config.cache"]

# The suffix(es) of source filenames.
source_suffix = ".rst"

# The master toctree document.
master_doc = "index"

# additional logos for the latex coverpage
LaTeXBuilder.supported_image_types = ["image/png", "image/pdf", "image/svg+xml"]
latex_additional_files = [watermark, ansys_logo_white, ansys_logo_white_cropped]
latex_elements = {"preamble": latex.generate_preamble(html_title)}

# Not found page
notfound_context = {
    "body": generate_404(),
}
notfound_no_urls_prefix = True

# ONLY FOR ANSYS-SPHINX-THEME
exclude_patterns = [
    "links.rst",
    "examples/sphinx-gallery/README.rst",
    "sg_execution_times.rst",
    "examples/gallery-examples/*.ipynb",
]
rst_epilog = ""
with Path.open(THIS_PATH / "links.rst", "r") as f:
    rst_epilog += f.read()


linkcheck_ignore = [
    r"https://sphinxdocs.ansys.com/version/*",
]
if switcher_version != "dev":
    linkcheck_ignore.append(
        f"https://github.com/ansys/ansys-sphinx-theme/releases/tag/v{__version__}"
    )


# Configure the Jinja contexts

jinja_contexts = {
    "install_guide": {
        "version": f"v{version}" if not version.endswith("dev0") else "main",
    },
    "pdf_guide": {"version": get_version_match(__version__)},  # noqa: E501
    "toxenvs": {
        "envs": subprocess.run(
            ["tox", "list", "-d", "-q"], capture_output=True, text=True
        ).stdout.splitlines()[1:],
    },
}


def extract_example_links(
    repo_fullname: str, path_relative_to_root: str, exclude_files: List[str] = []
) -> List[str]:
    """
    Extract example links from a specific GitHub repository.

    Parameters
    ----------
    repo_fullname : str
        Fullname of the repository to extract example links from.
    path_relative_to_root : str
        Path relative to the root of the repository to extract example links from.
    exclude_files : list of str
        A list of files to exclude from the returned example links.

    Returns
    -------
    list
        List of example links.
    """
    g = Github()
    repo = g.get_repo(repo_fullname)
    contents = repo.get_contents(path_relative_to_root)
    if not isinstance(contents, list):
        contents = [contents]
    example_links = []
    for content in contents:
        if content.type == "dir":
            example_links.extend(extract_example_links(repo_fullname, content.path, exclude_files))
        elif content.type == "file":
            if content.name not in exclude_files:
                example_links.append(content.download_url)

    return example_links


def download_and_process_files(example_links: List[str]) -> List[str]:
    """Download and process a series of example files.

    This function downloads a series of example files using a
    list of links and processes each file.

    Parameters
    ----------
    example_links : List[str]
        List of links to the example files to be downloaded.

    Returns
    -------
    list
        List of the names of the processed files.
    """
    file_names = []
    for link in example_links:
        file_name = link.split("/")[-1]
        file_path = str((EXAMPLE_PATH / file_name).absolute())
        with open(file_path, "wb") as f:  # noqa: PTH123
            response = requests.get(link)
            content = response.content.decode()
            lines = content.splitlines()
            # Replace the "target" string with the file name in the example files
            f.write("\n".join([line.replace("target", file_name) for line in lines]).encode())
        file_names.append(file_name)

    return file_names


# Skip building examples if desired
BUILD_EXAMPLES = True if os.environ.get("BUILD_EXAMPLES", "true") == "true" else False
jinja_contexts["main_toctree"] = {"build_examples": BUILD_EXAMPLES}

if not BUILD_EXAMPLES:
    exclude_patterns.extend(["examples.rst", "examples/**", "examples/api/**"])
else:
    # Autoapi examples
    extensions.append("ansys_sphinx_theme.extension.autoapi")
    html_theme_options["ansys_sphinx_theme_autoapi"] = {
        "project": project,
        "directory": "src/ansys_sphinx_theme/examples",
        "output": "examples/api",
        "own_page_level": "function",
        "package_depth": 1,
    }

    # Gallery of examples
    extensions.extend(["nbsphinx", "sphinx_gallery.gen_gallery"])
    sphinx_gallery_conf = {
        # path to your examples scripts
        "examples_dirs": ["examples/sphinx-gallery/"],
        # path where to save gallery generated examples
        "gallery_dirs": ["examples/gallery-examples/"],
        # Pattern to search for example files
        "filename_pattern": r"\.py",
        # Remove the "Download all examples" button from the top level gallery
        "download_all_examples": False,
        # Modules for which function level galleries are created.  In
        "image_scrapers": ("pyvista", "matplotlib", "plotly.io._sg_scraper.plotly_sg_scraper"),
        "default_thumb_file": str(PYANSYS_LIGHT_SQUARE),
    }
    pyvista.BUILDING_GALLERY = True
    pyvista.OFF_SCREEN = True

    nbsphinx_prolog = """
Download this example as a :download:`Jupyter notebook </{{ env.docname }}.ipynb>`.

----
"""
    nbsphinx_thumbnails = {
        "examples/nbsphinx/jupyter-notebook": "_static/pyansys_light_square.png",
    }

    # Third party examples
    example_links = extract_example_links(
        "executablebooks/sphinx-design",
        "docs/snippets/rst",
        exclude_files=["article-info.txt"],
    )
    file_names = download_and_process_files(example_links)

    admonitions_links = extract_example_links(
        "pydata/pydata-sphinx-theme",
        "docs/examples/kitchen-sink/admonitions.rst",
    )

    admonitions_links = download_and_process_files(admonitions_links)
    todo_include_todos = True  # admonition todo needs this to be True

    jinja_contexts["examples"] = {"inputs_examples": file_names}
    jinja_contexts["admonitions"] = {"inputs_admonitions": admonitions_links}


jinja_globals = {
    "ANSYS_SPHINX_THEME_VERSION": version,
}


def revert_exclude_patterns(app, env):
    """Revert the exclude patterns.

    Parameters
    ----------
    app : Sphinx
        Sphinx application instance.
    env : BuildEnvironment
        The build environment.

    Notes
    -----
    Remove the examples/gallery-examples/*.ipynb pattern from the exclude patterns.
    When the nbsphinx extension is enabled, the exclude patterns are modified
    to exclude the examples/gallery-examples/*.ipynb pattern. This function reverts
    the exclude patterns to their original state.
    """
    excluded_pattern = env.config.exclude_patterns
    excluded_pattern.remove("examples/gallery-examples/*.ipynb")
    env.config.exclude_patterns = excluded_pattern


def parse_navbar_config(app: sphinx.application.Sphinx, config: sphinx.config.Config):
    """Parse the navbar config file into a set of links to show in the navbar.

    Parameters
    ----------
    app : sphinx.application.Sphinx
        Application instance passed when the `config-inited` event is emitted
    config : sphinx.config.Config
        Initialized configuration to be modified
    """
    if "navbar_content_path" in config:
        filename = app.config["navbar_content_path"]
    else:
        filename = ""

    if filename:
        # with open(pathlib.Path(__file__).parent / filename, "r") as f:
        with pathlib.Path.open(THIS_PATH / filename, "r") as f:
            config.navbar_content = yaml.safe_load(f)
    else:
        config.navbar_content = None


NavEntry = Dict[str, Union[str, List["NavEntry"]]]


def setup_context(app, pagename, templatename, context, doctree):
    """Add custom variables to the context for use in templates.

    Parameters
    ----------
    app : Sphinx
        Sphinx application instance.
    pagename : str
        Name of the page being built.
    templatename : str
        Name of the template being used.
    context : dict
        Context dictionary for the template.
    doctree : docutils.nodes.document
        Document tree for the page being built.
    """

    @lru_cache(maxsize=None)
    def render_header_nav_links() -> bs4.BeautifulSoup:
        """Render external header links into the top nav bar.

        The structure rendered here is defined in an external yaml file.

        Returns
        -------
        str
            Raw HTML to be rendered in the top nav bar
        """
        if not hasattr(app.config, "navbar_content"):
            raise ValueError(
                "A template is attempting to call render_header_nav_links(); a "
                "navbar configuration must be specified."
            )

        node = nodes.container(classes=["navbar-content"])
        node.append(render_header_nodes(app.config.navbar_content))
        header_soup = bs4.BeautifulSoup(app.builder.render_partial(node)["fragment"], "html.parser")
        return add_nav_chevrons(header_soup)

    def render_header_nodes(obj: List[NavEntry], is_top_level: bool = True) -> nodes.Node:
        """Generate a set of header nav links with docutils nodes.

        Parameters
        ----------
        is_top_level : bool
            True if the call to this function is rendering the top level nodes,
            False otherwise (non-top level nodes are displayed as submenus of the top
            level nodes)
        obj : List[NavEntry]
            List of yaml config entries to render as docutils nodes

        Returns
        -------
        nodes.Node
            Bullet list which will be turned into header nav HTML by the sphinx builder
        """
        bullet_list = nodes.bullet_list(
            bullet="-",
            classes=["navbar-toplevel" if is_top_level else "navbar-sublevel"],
        )

        for item in obj:
            if "file" in item:
                ref_node = make_refnode(
                    app.builder,
                    context["current_page_name"],
                    item["file"],
                    None,
                    nodes.inline(classes=["navbar-link-title"], text=item.get("title")),
                    item.get("title"),
                )
            elif "link" in item:
                ref_node = nodes.reference("", "", internal=False)
                ref_node["refuri"] = item.get("link")
                ref_node["reftitle"] = item.get("title")
                ref_node.append(nodes.inline(classes=["navbar-link-title"], text=item.get("title")))

            if "caption" in item:
                caption = nodes.Text(item.get("caption"))
                ref_node.append(caption)

            paragraph = nodes.paragraph()
            paragraph.append(ref_node)

            container = nodes.container(classes=["ref-container"])
            container.append(paragraph)

            list_item = nodes.list_item(
                classes=["active-link"] if item.get("file") == pagename else []
            )
            list_item.append(container)

            if "sections" in item:
                wrapper = nodes.container(classes=["navbar-dropdown"])
                wrapper.append(render_header_nodes(item["sections"], is_top_level=False))
                list_item.append(wrapper)

            bullet_list.append(list_item)

        return bullet_list

    context["render_header_nav_links"] = render_header_nav_links
    # context["render_library_examples"] = render_library_examples

    # Update the HTML page context with a few extra utilities.
    context["pygments_highlight_python"] = lambda code: highlight(
        code, PythonLexer(), HtmlFormatter()
    )


def add_nav_chevrons(input_soup: bs4.BeautifulSoup) -> bs4.BeautifulSoup:
    """Add dropdown chevron icons to the header nav bar.

    Parameters
    ----------
    input_soup : bs4.BeautifulSoup
        Soup containing rendered HTML which will be inserted into the header nav bar

    Returns
    -------
    bs4.BeautifulSoup
        A new BeautifulSoup instance containing chevrons on the list items that
        are meant to be dropdowns.
    """
    soup = copy.copy(input_soup)

    for li in soup.find_all("li", recursive=True):
        divs = li.find_all("div", {"class": "navbar-dropdown"}, recursive=False)
        if divs:
            ref = li.find("div", {"class": "ref-container"})
            ref.append(soup.new_tag("i", attrs={"class": "fa-solid fa-chevron-down"}))

    return soup


def setup(app: Sphinx) -> Dict:
    """Sphinx hooks to add to the setup."""
    app.connect("env-updated", revert_exclude_patterns)
    app.add_config_value("navbar_content_path", "navbar.yml", "env")
    app.connect("config-inited", parse_navbar_config)
    app.connect("html-page-context", setup_context)
    app.add_css_file("custom.css", priority=800)
