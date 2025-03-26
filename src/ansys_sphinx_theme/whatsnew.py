# Copyright (C) 2021 - 2025 ANSYS, Inc. and/or its affiliates.
# SPDX-License-Identifier: MIT
#
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""Module to configure whatsnew options and layer the what's new content on the documentation.

This module provides functions to configure whatsnew options, extract the what's new content
from the changelog document, and layer the what's new content on the documentation.
"""

import pathlib
import re
from typing import Iterable

from docutils import nodes
from sphinx.application import Sphinx

"""Semantic version regex as found on semver.org:
https://semver.org/#is-there-a-suggested-regular-expression-regex-to-check-a-semver-string"""
SEMVER_REGEX = (
    r"(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)"
    r"(?:-((?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*)"
    r"(?:\.(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*))*))?"
    r"(?:\+(>[0-9a-zA-Z-]+(?:\.[0-9a-zA-Z-]+)*))?"
)


def get_whatsnew_options(app: Sphinx) -> tuple:
    """Get the whatsnew options from the configuration file.

    Parameters
    ----------
    app : sphinx.application.Sphinx
        Application instance for rendering the documentation.

    Returns
    -------
    tuple
        Tuple containing the paths to the whatsnew file, changelog file, and the sidebar pages.
        If the whatsnew options are not found, return None for each of those fields.
    """
    # Get the html_theme_options from conf.py
    config_options = app.config.html_theme_options

    # Get the whatsnew key from the html_theme_options
    whatsnew_options = config_options.get("whatsnew")

    if not whatsnew_options:
        return None, None

    # Get the names of the whatsnew.yml and changelog.rst files
    whatsnew_file = whatsnew_options.get("whatsnew_file_name")
    changelog_file = whatsnew_options.get("changelog_file_name")

    # The source directory of the documentation: {repository_root}/doc/source
    doc_src_dir = app.env.srcdir

    if whatsnew_file is not None:
        whatsnew_file = pathlib.Path(doc_src_dir) / whatsnew_file
    if changelog_file is not None:
        changelog_file = pathlib.Path(doc_src_dir) / changelog_file

    return whatsnew_file, changelog_file


def add_whatsnew_changelog(app: Sphinx, doctree: nodes.document) -> None:
    """Add the what's new section to each minor version if applicable.

    Parameters
    ----------
    app : sphinx.application.Sphinx
        Application instance for rendering the documentation.
    doctree : docutils.nodes.document
        Document tree for the page.
    """
    # Get the html_theme_options from conf.py
    config_options = app.config.html_theme_options

    # Get the whatsnew key from the html_theme_options
    whatsnew_options = config_options.get("whatsnew")

    # The source directory of the documentation: {repository_root}/doc/source
    doc_src_dir = pathlib.Path(app.env.srcdir)

    # Full paths to the whatsnew.yml and changelog.rst files from the doc/source directory
    whatsnew_file = doc_src_dir / whatsnew_options.get("whatsnew_file_name")
    changelog_file = doc_src_dir / whatsnew_options.get("changelog_file_name")

    # Read the file and get the sections from the file as a list. For example,
    # sections = [<document: <target...><section "getting started; ref-getting-starte ...>]
    sections = doctree.traverse(nodes.document)
    if not sections:
        return

    # Get the file name of the section using section.get("source") and return the section
    # if section.get("source") is equal to the changelog_file
    changelog_doctree_sections = [
        section for section in sections if section.get("source") == str(changelog_file)
    ]

    # Return if the changelog file sections are not found
    if not changelog_doctree_sections:
        return

    # Get the what's new data from the whatsnew.yml file
    whatsnew_data = get_whatsnew_data(whatsnew_file)

    existing_minor_versions = []
    docs_content = doctree.traverse(nodes.section)

    # Get each section that contains a semantic version number
    version_sections = [node for node in docs_content if re.search(SEMVER_REGEX, node[0].astext())]

    for node in version_sections:
        # Get the semantic version number from the section title link
        next_node = node.next_node(nodes.reference)
        # Get the name of the section title link
        version = next_node.get("name")

        if version:
            # Create the minor version from the patch version
            minor_version = ".".join(version.split(".")[:-1])

            if minor_version not in existing_minor_versions:
                # Add minor version to list of existing minor versions
                existing_minor_versions.append(minor_version)

                # Create a section for the minor version
                minor_version_section = nodes.section(
                    ids=[f"version-{minor_version}"], names=[f"Version {minor_version}"]
                )
                # Add the title to the section for the minor version
                minor_version_section += nodes.title("", f"Version {minor_version}")

                # Add "What's New" section under the minor version if the minor version is in
                # the what's new data
                if whatsnew_file.exists() and (minor_version in list(whatsnew_data.keys())):
                    minor_version_whatsnew = add_whatsnew_section(minor_version, whatsnew_data)
                    minor_version_section.append(minor_version_whatsnew)

                # Add the title at the beginning of a section with a patch version
                node.insert(0, minor_version_section)


def get_whatsnew_data(whatsnew_file: pathlib.Path) -> dict:
    """Get the what's new data from the whatsnew.yml file.

    Parameters
    ----------
    whatsnew_file : pathlib.Path
        Path to the whatsnew.yml file.

    Returns
    -------
    dict
        Dictionary containing the what's new data from the whatsnew.yml file.
    """
    if whatsnew_file.exists():
        # Open and read the whatsnew.yml file

        try:
            import yaml
        except ImportError as e:
            raise ImportError(
                f"Failed to import `pyyaml`: {e}. Install the package using `pip install ansys-sphinx-theme[changelog]`"  # noqa: E501
            )

        with pathlib.Path.open(whatsnew_file, "r", encoding="utf-8") as file:
            whatsnew_data = yaml.safe_load(file)

        # Create a dictionary containing the what's new data for each minor version
        # For example: { minor_version: [fragment1_dict, fragment2_dict, ...] }
        minor_version_whatsnew_data = {}
        for fragment in whatsnew_data["fragments"]:
            # Get the minor version from the fragment version
            whatsnew_minor_version = ".".join(fragment["version"].split(".")[:2])

            # Create an empty list for the minor version if it does not exist
            if whatsnew_minor_version not in minor_version_whatsnew_data:
                minor_version_whatsnew_data[whatsnew_minor_version] = []
            # Append the fragment to the minor version in the whatsnew_data
            minor_version_whatsnew_data[whatsnew_minor_version].append(fragment)

        return minor_version_whatsnew_data


def add_whatsnew_section(minor_version: str, whatsnew_data: dict) -> nodes.section:
    """Add the what's new section and dropdowns for each fragment in the whatsnew.yml file.

    Parameters
    ----------
    minor_version : str
        Minor version number.
    whatsnew_data : dict
        Dictionary containing the what's new data from the whatsnew.yml file.

    Returns
    -------
    nodes.section
        Section containing the what's new title and dropdowns for each fragment in the
        whatsnew.yml file.
    """
    # Add the what's new section and title
    minor_version_whatsnew = nodes.section(ids=[f"version-{minor_version}-whatsnew"])
    minor_version_whatsnew += nodes.title("", "What's New")

    # Add a dropdown under the "What's New" section for each fragment in the whatsnew.yml file
    for fragment in whatsnew_data[minor_version]:
        # Create a dropdown for the fragment
        whatsnew_dropdown = nodes.container(
            body_classes=[""],
            chevron=True,
            container_classes=["sd-mb-3 sd-fade-in-slide-down"],
            design_component="dropdown",
            has_title=True,
            icon="",
            is_div=True,
            opened=False,
            title_classes=[""],
            type="dropdown",
        )

        # Set the title_id for the dropdown
        title_id = fragment["title"].replace(" ", "-").lower()

        # Add the title of the fragment to the dropdown
        whatsnew_dropdown += nodes.rubric(ids=[title_id], text=fragment["title"])

        # Add a line specifying which version the fragment is available in
        version_paragraph = nodes.paragraph("sd-card-text")
        version_paragraph.append(
            nodes.emphasis("", f"Available in v{fragment['version']} and later")
        )
        whatsnew_dropdown += version_paragraph

        # Split content from YAML file into list
        content_lines = fragment["content"].split("\n")

        # Create iterator for the content_lines
        content_iterator = iter(content_lines)

        # Navigate to first line in the iterator
        line = next(content_iterator, None)

        while line is not None:
            if ".. code" in line or ".. sourcecode" in line:
                # Get language after "code::"
                language = line.split("::")[1].strip()
                # Create the code block container node with the language if it exists
                code_block = (
                    nodes.container(classes=[f"highlight-{language} notranslate"])
                    if language
                    else nodes.container()
                )

                # Fill the code block with the following lines until it reaches the end or an
                # unindented line
                code_block, line = fill_code_block(content_iterator, code_block)
                whatsnew_dropdown += code_block
            else:
                # Create the paragraph node
                paragraph = nodes.paragraph("sd-card-text")

                # Fill the paragraph node with the following lines until it reaches
                # the end or a code block
                paragraph, line = fill_paragraph(content_iterator, paragraph, line)
                whatsnew_dropdown += paragraph

        # Append the fragment dropdown to the minor_version_whatsnew section
        minor_version_whatsnew.append(whatsnew_dropdown)

    return minor_version_whatsnew


def fill_code_block(content_iterator: Iterable, code_block: nodes.container) -> nodes.container:
    """Fill the code block.

    Parameters
    ----------
    content_iterator : Iterable
        Iterator for the content lines from the fragments in the whatsnew.yml file.
    code_block : nodes.container
        Container node for the code block.

    Returns
    -------
    nodes.container, str
        Container node for the code block and the next line in the content iterator.
    """
    # classes=["highlight"] is required for the copy button to show up in the literal_block
    highlight_container = nodes.container(classes=["highlight"])

    # Create literal block with copy button
    literal_block = nodes.literal_block(
        classes=["sd-button sd-button--icon sd-button--icon-only sd-button--icon-small"],
        icon="copy",
        label="Copy",
        title="Copy",
    )

    # Move to the first line in the code block (the line after ".. code::")
    next_line = next(content_iterator, None)

    # Boolean to check if the line in code block is within a dictionary
    in_dictionary = False

    # While the next_line is indented or blank, add it to the code block
    while next_line is not None and (next_line.startswith(" ") or (next_line == "")):
        if in_dictionary:
            if next_line.lstrip().startswith("}"):
                in_dictionary = False
                formatted_line = next_line.lstrip() + "\n"
            else:
                formatted_line = next_line + "\n"
        else:
            if next_line.lstrip().startswith("{"):
                in_dictionary = True
            formatted_line = next_line.lstrip() + "\n"

        # Add the formatted line to the literal block
        literal_block += nodes.inline(text=formatted_line)

        # Break the loop if the end of the content is reached
        if next_line is not None:
            # Move to the next line in the content
            next_line = next(content_iterator, None)
        else:
            break

    # Add the literal block to the highlight container
    highlight_container += literal_block

    # Add the highlight container to the code block
    code_block += highlight_container

    return code_block, next_line


def fill_paragraph(
    content_iterator: Iterable, paragraph: nodes.paragraph, next_line: str
) -> nodes.paragraph:
    """Fill the paragraph node.

    Parameters
    ----------
    content_iterator : Iterable
        Iterator for the content lines from the fragments in the whatsnew.yml file.
    paragraph : nodes.paragraph
        Paragraph node.
    next_line : str
        Next line in the content iterator.

    Returns
    -------
    nodes.paragraph, str
        Paragraph node and the next line in the content iterator.
    """
    # While the next_line is not None and is not a code block, add it to the paragraph
    while next_line is not None and not next_line.startswith(".. "):
        # Regular expressions to find rst links, and single & double backticks/asterisks
        rst_link_regex = r"(`[^<`]+? <[^>`]+?>`_)"
        single_backtick_regex = r"(`[^`]+?`)"
        double_backtick_regex = r"(``.*?``)"
        bold_text_regex = r"(\*\*.*?\*\*)"
        italic_text_regex = r"(\*[^\*]+?\*)"

        # Check if there are rst links, single & double backticks/asterisks in the line
        link_backtick_regex = (
            rf"{rst_link_regex}|"
            rf"{single_backtick_regex}|{double_backtick_regex}|"
            rf"{bold_text_regex}|{italic_text_regex}"
        )

        # Get all matches for rst links, single & double backticks/asterisks in the line
        # Sample: next_line = "The files are **deleted** when the ``GUI`` is closed. For more info"
        # For example, matches = [('', '', '', '**deleted**', ''), ('', '', '``GUI``', '', '')]
        matches = re.findall(link_backtick_regex, next_line)

        if matches:
            # Get all of the matches from the matches list
            # For example, regex_matches = ['**deleted**', '``GUI``']
            regex_matches = [
                element for match in matches for i, element in enumerate(match) if element
            ]

            # Create a regular expression pattern that matches any URL
            # For example, pattern = r"\*\*deleted\*\*|``GUI``"
            pattern = "|".join(map(re.escape, regex_matches))

            # Split the line using the pattern
            # For example, split_lines = ['The files are ', '**deleted**', ' when the ', '``GUI``',
            # ' is closed. For more info']
            split_lines = re.split(f"({pattern})", next_line)

            for line in split_lines:
                if line in regex_matches:
                    # If it matches RST link regex, append a reference node
                    if re.search(rst_link_regex, line):
                        text, url = re.findall(r"`([^<`]+?) <([^>`]+?)>`_", line)[0]
                        if url.startswith("http") or url.startswith("www"):
                            ref_type = "external"
                        else:
                            ref_type = "internal"
                        paragraph.append(
                            nodes.reference(
                                classes=[f"reference-{ref_type}"],
                                refuri=url,
                                href=url,
                                text=text,
                            )
                        )
                    # If it matches single or double backticks, append a literal node
                    elif re.search(single_backtick_regex, line):
                        text = re.findall(r"`([^`]+?)`", line)[0]
                        paragraph.append(nodes.literal(text=text))
                    elif re.search(double_backtick_regex, line):
                        text = re.findall(r"``(.*?)``", line)[0]
                        paragraph.append(nodes.literal(text=text))
                    # If it matches bold text, append a strong node
                    elif re.search(bold_text_regex, line):
                        text = re.findall(r"\*\*(.*?)\*\*", line)[0]
                        paragraph.append(nodes.strong(text=text))
                    # If it matches italic text, append an emphasis node
                    elif re.search(italic_text_regex, line):
                        text = re.findall(r"\*([^\*]+?)\*", line)[0]
                        paragraph.append(nodes.emphasis(text=text))
                else:
                    paragraph.append(nodes.inline(text=line))
        else:
            # Append the next_line as an inline element, unless it is an empty string. If it's an
            # empty string, append a line break
            paragraph.append(nodes.inline(text=next_line)) if next_line != "" else paragraph.append(
                nodes.line(text="\n")
            )

        # Add a space at the end of each line
        paragraph.append(nodes.inline(text=" "))

        # Break the loop if the end of the content is reached
        if next_line is not None:
            # Move to the next line in the content
            next_line = next(content_iterator, None)
        else:
            break

    return paragraph, next_line


def extract_whatsnew(app: Sphinx, doctree: nodes.document, docname: str) -> None:
    """Extract the what's new content from the changelog document.

    Parameters
    ----------
    app : sphinx.application.Sphinx
        Application instance for rendering the documentation.
    doctree : docutils.nodes.document
        Document tree for the page.
    docname : str
        Name of the document being processed.
    """
    # Get the html_theme_options from conf.py
    config_options = app.config.html_theme_options

    # Get the whatsnew key from the html_theme_options
    whatsnew_options = config_options.get("whatsnew")

    # The source directory of the documentation: {repository_root}/doc/source
    doc_src_dir = pathlib.Path(app.env.srcdir)

    # Full path to the changelog.rst file starting from the doc/source directory
    changelog_file = doc_src_dir / whatsnew_options.get("changelog_file_name")

    # Get the number of headers to display in the what's new section in the sidebar
    # By default, it displays the first three minor versions
    sidebar_no_of_headers = whatsnew_options.get("sidebar_no_of_headers", 3)
    # Get the number of what's new content to display under each minor version in the sidebar.
    # By default, it displays all what's new dropdown titles
    sidebar_no_of_contents = whatsnew_options.get("sidebar_no_of_contents")

    # Get the doctree for the file
    changelog_file = changelog_file.stem
    doctree = app.env.get_doctree(changelog_file)
    docs_content = doctree.traverse(nodes.section)
    html_title = app.config.html_title or app.config.html_short_title or app.config.project

    if not docs_content:
        return

    whatsnew = []
    app.env.whatsnew = []

    # Get a list of nodes whose ids start with "version" that contain "What's new" sections
    versions_nodes = []

    # Find nodes that contain the minor versions and a "What's New" section
    for node in docs_content:
        node_id = node.get("ids")[0]
        # Get the nodes that contain the minor versions: "Version x.y"
        if node_id.startswith("version") and "whatsnew" not in node_id:
            sections = list(node.traverse(nodes.section))
            # If the section contains a "What's New" section, add it to the list of versions
            whatsnew_nodes = [
                section_node
                for section_node in sections
                if section_node.get("ids")[0] == f"{node_id}-whatsnew"
            ]
            if whatsnew_nodes:
                versions_nodes.append(node)

    # Get the version nodes up to the specified number of headers
    versions_nodes = versions_nodes[:sidebar_no_of_headers]

    for version_node in versions_nodes:
        # Get the version title (e.g., "Version 0.1")
        version_title = version_node[0].astext()
        # Get the sections under the version node
        sections = list(version_node.traverse(nodes.section))

        # Sections with text that contains "what's new"
        whatsnew_nodes = [node for node in sections if node[0].astext().lower() == "what's new"]

        if not whatsnew_nodes:
            continue

        # Get the children of the "What's New" section
        children = [node for node in whatsnew_nodes[0].traverse(nodes.rubric)]

        # Filter the displayed children based on the number of content specified in the config
        if sidebar_no_of_contents is not None:
            if len(children) > sidebar_no_of_contents:
                children = children[:sidebar_no_of_contents]

        contents = {
            "title": f"{html_title} {version_title}",
            "title_url": f"{changelog_file}.html#{version_node.get('ids')[0]}",
            "children": children,
            "url": f"{changelog_file}.html#{whatsnew_nodes[0]['ids'][0]}",
        }

        whatsnew.append(contents)

    app.env.whatsnew = whatsnew


def whatsnew_sidebar_pages(app: Sphinx) -> list:
    """Get the pages the what's new section should be displayed on and return the list of pages.

    Parameters
    ----------
    app : sphinx.application.Sphinx
        Application instance for rendering the documentation.

    Returns
    -------
    list
        List of pages the what's new section should be displayed on.
    """
    # Get the html_theme_options from conf.py
    config_options = app.config.html_theme_options

    # Get the whatsnew key from the html_theme_options
    whatsnew_options = config_options.get("whatsnew")

    if not whatsnew_options:
        return None

    # Get the pages the whatsnew section should be displayed on
    whatsnew_sidebar_pages = whatsnew_options.get("sidebar_pages")

    return whatsnew_sidebar_pages
