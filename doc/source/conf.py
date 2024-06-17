"""Sphinx documentation configuration file."""

from datetime import datetime
import os

from github import Github
from sphinx.builders.latex import LaTeXBuilder

LaTeXBuilder.supported_image_types = ["image/png", "image/pdf", "image/svg+xml"]

from ansys_sphinx_theme import (
    __version__,
    ansys_favicon,
    ansys_logo_black,
    ansys_logo_white,
    ansys_logo_white_cropped,
    convert_version_to_pymeilisearch,
    generate_404,
    get_version_match,
    latex,
    watermark,
)

# Project information
project = "ansys_sphinx_theme"
copyright = f"(c) {datetime.now().year} ANSYS, Inc. All rights reserved"
author = "ANSYS, Inc."
release = version = __version__
cname = os.getenv("DOCUMENTATION_CNAME", "sphinxdocs.ansys.com")
switcher_version = get_version_match(__version__)

# use the default ansys logo
html_logo = ansys_logo_black
html_theme = "ansys_sphinx_theme"


# In the html_context dictionary in conf.py
html_context = {
    "github_user": "ansys",
    "github_repo": "ansys-sphinx-theme",
    "github_version": "main",
    "doc_path": "doc/source",
}


# specify the location of your github repo
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
    "sphinx_design",
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

# ONLY FOR ANSYS-SPHINX-THEME
exclude_patterns = ["links.rst"]
rst_epilog = ""
with open("links.rst") as f:
    rst_epilog += f.read()

from pathlib import Path
from typing import List

import requests

THIS_PATH = Path(__file__).parent.resolve()

EXAMPLE_PATH = (THIS_PATH / "examples" / "sphinx_examples").resolve()

linkcheck_ignore = []
if switcher_version != "dev":
    linkcheck_ignore.append(
        f"https://github.com/ansys/ansys-sphinx-theme/releases/tag/v{__version__}"
    )


def extract_example_links(
    repo_fullname: str, path_relative_to_root: str, exclude_files: List[str]
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

jinja_contexts = {
    "examples": {"inputs_examples": file_names},
    "install_guide": {
        "version": f"v{version}" if not version.endswith("dev0") else "main",
    },
}
