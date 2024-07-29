"""Sphinx documentation configuration file."""

from datetime import datetime
import os
from pathlib import Path
from typing import List

from github import Github
import pyvista
import requests
from sphinx.builders.latex import LaTeXBuilder

from ansys_sphinx_theme import (
    __version__,
    ansys_favicon,
    ansys_logo_white,
    ansys_logo_white_cropped,
    convert_version_to_pymeilisearch,
    generate_404,
    get_version_match,
    latex,
    watermark,
)

THIS_PATH = Path(__file__).parent.resolve()
EXAMPLE_PATH = (THIS_PATH / "examples" / "sphinx_examples").resolve()
API_TEMPLATES = (THIS_PATH / "examples" / "autoapi").resolve()

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
# static path
html_static_path = ["_static"]
# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

html_context = {
    "github_user": "ansys",
    "github_repo": "ansys-sphinx-theme",
    "github_version": "main",
    "doc_path": "doc/source",
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
    "use_meilisearch": {
        "api_key": os.getenv("MEILISEARCH_PUBLIC_API_KEY", ""),
        "index_uids": {
            f"ansys-sphinx-theme-v{convert_version_to_pymeilisearch(__version__)}": "ansys-sphinx-theme",  # noqa: E501
        },
    },
    "ansys_sphinx_theme_autoapi": {
        "project": project,
        "directory": "src/ansys_sphinx_theme/examples",
        "output": "examples/",
        "own_page_level": "function",
    },
    "logo": "ansys",
}

# Sphinx extensions
extensions = [
    "ansys_sphinx_theme.extension.autoapi",
    "nbsphinx",
    "numpydoc",
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.intersphinx",
    "sphinx.ext.todo",
    "sphinx_copybutton",
    "sphinx_design",
    "sphinx.ext.intersphinx",
    "sphinx.ext.todo",
    "sphinx_gallery.gen_gallery",
    "sphinx_jinja",
    "notfound.extension",
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
    "examples/gallery-examples/*.ipynb",
]
rst_epilog = ""
with open("links.rst") as f:
    rst_epilog += f.read()

sphinx_gallery_conf = {
    # path to your examples scripts
    "examples_dirs": ["examples/sphinx-gallery"],
    # path where to save gallery generated examples
    "gallery_dirs": ["examples/gallery-examples"],
    # Pattern to search for example files
    "filename_pattern": r"sphinx_gallery\.py",
    # Remove the "Download all examples" button from the top level gallery
    "download_all_examples": False,
    # Modules for which function level galleries are created.  In
    "image_scrapers": ("pyvista", "matplotlib"),
    "default_thumb_file": "source/_static/pyansys_light_square.png",
}
nbsphinx_execute = "always"
nbsphinx_thumbnails = {
    "examples/nbsphinx/jupyter-notebook": "_static/pyansys_light_square.png",
}

# Ensure that offscreen rendering is used for docs generation
# Preferred plotting style for documentation
pyvista.BUILDING_GALLERY = True

linkcheck_ignore = ["https://sphinxdocs.ansys.com/version/dev/*"]
if switcher_version != "dev":
    linkcheck_ignore.append(
        f"https://github.com/ansys/ansys-sphinx-theme/releases/tag/v{__version__}"
    )


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
    token = os.environ.get("GITHUB_TOKEN")
    g = Github(token)
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
        with open(file_path, "wb") as f:
            response = requests.get(link)
            content = response.content.decode()
            lines = content.splitlines()
            # Replace the "target" string with the file name in the example files
            f.write("\n".join([line.replace("target", file_name) for line in lines]).encode())
        file_names.append(file_name)

    return file_names


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

jinja_contexts = {
    "examples": {"inputs_examples": file_names},
    "admonitions": {"inputs_admonitions": admonitions_links},
    "install_guide": {
        "version": f"v{version}" if not version.endswith("dev0") else "main",
    },
    "pdf_guide": {"version": get_version_match(__version__)},  # noqa: E501
}
