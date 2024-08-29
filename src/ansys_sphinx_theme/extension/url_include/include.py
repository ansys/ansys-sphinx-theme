# Copyright (C) 2021 - 2024 ANSYS, Inc. and/or its affiliates.
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

"""``urlinclude`` Sphinx extension."""

import asyncio
import os
from pathlib import Path
import shutil

from docutils import statemachine
from docutils.parsers.rst import directives
from sphinx.util import logging
from sphinx.util.console import bold
from sphinx.util.docutils import SphinxDirective

from ansys_sphinx_theme.extension.url_include import __version__
from ansys_sphinx_theme.extension.url_include.base import BaseInclude
from ansys_sphinx_theme.extension.url_include.github_file import GitHubFile
from ansys_sphinx_theme.extension.url_include.jinja_include import (
    jinja_literal_block,
    jinja_raw_block,
)
from ansys_sphinx_theme.extension.url_include.utils import add_literal_block, create_temp_file

logger = logging.getLogger(__name__)

DIRECTIVE_NAME = "include-from-url"
processed_url_set = set()


class UrlIncludeDirective(BaseInclude, SphinxDirective):
    """UrlIncludeDirective class.

    This class is responsible for fetching the content from the URL and
    including it in the document.

    Parameters
    ----------
    BaseInclude : class
        BaseInclude class.
    SphinxDirective : class
        SphinxDirective class.
    """

    required_arguments = 1
    optional_arguments = 0
    has_content = True
    option_spec = {
        "language": directives.unchanged,
        "literal-include": directives.flag,
        "jinja-include": directives.flag,
        "number-lines": directives.unchanged,
        "tab-width": int,
        "file-name": directives.unchanged,
        "encoding": directives.encoding,
    }

    def _process_content(self):
        """Process the content.

        Process the file content of file fetched from the URL, based on the number of lines.

        Returns
        -------
        str
            Processed content.
        """
        total_lines = len(self.text_content)

        self.start_line = 1
        # Simplify condition
        self.end_line = total_lines
        total_content = "".join(self.text_content[0 : self.end_line])

        number_lines = self.number_lines if self.number_lines else 0

        if number_lines:
            number_lines = int(number_lines)
            total_content = "\n".join(self.text_content[self.start_line - 1 : number_lines])
        else:
            total_content = "\n".join(self.text_content[self.start_line - 1 : self.end_line])

        return total_content

    def _get_language(self):
        """Get the language of the content."""
        language = self.options.get("language", None)
        return language if language else Path(self.url).suffix[1:]

    def _get_temp_folder_path(self):
        """Get the path of the temporary folder."""
        temp_folder_name = (
            self.config.urlinclude_template_folder
            if self.config.urlinclude_template_folder
            else "temporary"
        )
        return self.env.app.srcdir / temp_folder_name

    def _get_temp_file_path(self, temp_folder):
        """Get the path of the temporary file."""
        return temp_folder / self.file_name

    def run_template(self, temp_file):
        """Run the template.

        Parameters
        ----------
        temp_file : str
            Temporary file path.

        Returns
        -------
        list
            List of nodes.
        """
        filename = Path(temp_file)
        self.env.note_included(filename)
        return super().run(path=filename)

    def _get_github_content(self):
        """Get the content from the GitHub URL.

        Returns
        -------
        str
            Content from the GitHub URL.
        """
        try:
            file = GitHubFile(self.url, self.access_token)
            self.text_content = asyncio.run(file.fetch_content()).splitlines()

        except Exception as e:
            logger.warning(f"Failed to fetch content from {self.url}: {e}.")

        if not self.text_content:
            return []

        total_content = self._process_content()
        self.include_lines = statemachine.string2lines(
            total_content, self.tab_width, convert_whitespace=True
        )

        for i, line in enumerate(self.include_lines):
            if len(line) > self.state.document.settings.line_length_limit:
                raise self.warning(
                    '"%s": line %d exceeds the' " limit for the line length." % (self.url, i + 1)
                )
        return total_content

    def run(self):
        """Run the directive.

        Parameters
        ----------
        url : str
            URL to fetch the content.
        number-lines : str
            Number of lines to include.
        literal-include : bool
            Include the content as a literal block.
        jinja-include : bool
            Include the content as a Jinja block.
        tab-width : int
            Tab width.
        file-name : str
            File name.

        Returns
        -------
        list
            List of nodes.

        """
        self.url = self.arguments[0]
        self.number_lines = self.options.get("number-lines", None)
        self.literal = "literal-include" in self.options
        self.jinja_include = "jinja-include" in self.options
        self.e_handler = self.state.document.settings.input_encoding_error_handler
        self.tab_width = self.options.get("tab-width", self.state.document.settings.tab_width)
        self.file_name = self.options.get("file-name", None)

        self.access_token = os.environ.get("GITHUB_ACCESS_TOKEN", None)
        self.text_content = []

        if not self.literal:
            language = None
        else:
            language = self._get_language()

        self.file_name = self.file_name if self.file_name else Path(self.url).name.split("@")[0]
        temp_folder_path = self._get_temp_folder_path()

        if self.url in processed_url_set and not self.jinja_include and not self.literal:
            # URL is already processed
            temp_file = self._get_temp_file_path(temp_folder_path)
            if Path.exists(temp_file):
                self.run_template(temp_file)
                return []
        processed_url_set.add(self.url)
        total_content = self._get_github_content()

        if not total_content:
            return []

        if self.has_content:
            contents = {
                key.strip(): value.strip()
                for key, value in (pair.split(":", 1) for pair in self.content)
            }
        else:
            contents = {}

        if self.literal:
            if self.jinja_include:
                return [
                    jinja_literal_block(
                        "".join(total_content),
                        contents,
                        language,
                        self.lineno,
                        self.state,
                    )
                ]
            else:
                return [add_literal_block("".join(total_content), language)]
        else:
            if self.jinja_include:
                temp_file = jinja_raw_block(
                    temp_folder_path,
                    self.file_name,
                    "".join(total_content),
                    self.url,
                    contents,
                    self.lineno,
                    self.state,
                )
                self.run_template(temp_file)
            else:
                temp_file = create_temp_file(
                    temp_folder_path, "".join(total_content), self.file_name
                )
                self.run_template(temp_file)

        logger.info(bold("Successfully fetched content from: ") + self.url)

        return []


def process_raw_content(app, docname, source):
    """Process the raw content.

    Parameters
    ----------
    app : object
        Sphinx application object.
    docname : str
        Document name.
    source : str
        Source content.
    """
    # Reset the url include folder
    directives.register_directive(DIRECTIVE_NAME, UrlIncludeDirective)


def clear_url_include_folder(app, exception):
    """Clear the URL include folder after the build is finished.

    Parameters
    ----------
    app : object
        Sphinx application object.
    exception : object
        Exception object.
    """
    # Clear the URL include folder
    if exception:
        logger.warning(bold("URL include folder not cleared."))
        return

    temp_folder_path = app.srcdir / app.config.urlinclude_template_folder
    if Path.exists(temp_folder_path) and app.config.clear_urlinclude_folder:
        logger.info(bold("Clearing the URL include folder..."), nonl=True)
        shutil.rmtree(temp_folder_path)
        logger.info("done")


def setup_url_include(app):
    """Set up the URL include directive.

    Parameters
    ----------
    app : object
        Sphinx application object.

    Returns
    -------
    dict
        Dictionary containing the version.
    """
    app.connect("source-read", process_raw_content)
    app.connect("build-finished", clear_url_include_folder)
    app.add_config_value("urlinclude_template_folder", "urlinclude_template_folder", "html")
    app.add_config_value("clear_urlinclude_folder", False, "html")
    return {"version": __version__}
