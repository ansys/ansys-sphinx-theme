# Copyright (C) 2021 - 2026 Synopsys, Inc. and ANSYS, Inc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Content resolver Sphinx directive: ``include-from-url``.

Fetches reusable documentation snippets from a GitHub repository, optionally
renders Jinja2 variables defined in the directive body, and inserts the result
into the RST document tree.
"""

import asyncio
import os
from pathlib import Path
import shutil

from docutils import statemachine
from docutils.parsers.rst import directives
from sphinx.util import logging
from sphinx.util.console import bold
from sphinx.util.docutils import SphinxDirective

from ansys_sphinx_theme.extension.resolver.base import BaseInclude
from ansys_sphinx_theme.extension.resolver.github_file import GitHubFile
from ansys_sphinx_theme.extension.resolver.jinja_resolver import (
    jinja_literal_block,
    jinja_raw_block,
)
from ansys_sphinx_theme.extension.resolver.utils import add_literal_block, create_temp_file

logger = logging.getLogger(__name__)

_EXTENSION_VERSION = "0.1.dev0"

DIRECTIVE_NAME = "include-from-url"

# URLs processed in this build; reset on builder-inited to avoid cross-build leakage.
_processed_urls: set[str] = set()


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

    def _process_content(self) -> str:
        """Return the fetched text, optionally clamped to a line count.

        Returns
        -------
        str
            Processed content as a single string.
        """
        end = int(self.number_lines) if self.number_lines else len(self.text_content)
        return "\n".join(self.text_content[:end])

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
                    '"%s": line %d exceeds the limit for the line length.' % (self.url, i + 1)
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

        if self.url in _processed_urls and not self.jinja_include and not self.literal:
            # URL is already processed
            temp_file = self._get_temp_file_path(temp_folder_path)
            if Path.exists(temp_file):
                self.run_template(temp_file)
                return []
        _processed_urls.add(self.url)
        total_content = self._get_github_content()

        if not total_content:
            return []

        contents = {}
        for pair in self.content:
            if ":" in pair:
                key, value = pair.split(":", 1)
                contents[key.strip()] = value.strip()

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


def _reset_processed_urls(app):
    """Clear the URL cache at the start of each Sphinx build.

    Parameters
    ----------
    app : object
        Sphinx application object.
    """
    _processed_urls.clear()
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


def setup_content_resolver(app):
    """Register the ``include-from-url`` directive and connect Sphinx events.

    Parameters
    ----------
    app : object
        Sphinx application object.

    Returns
    -------
    dict
        Extension metadata.
    """
    app.connect("builder-inited", _reset_processed_urls)
    app.connect("build-finished", clear_url_include_folder)
    app.add_config_value("urlinclude_template_folder", "urlinclude_template_folder", "html")
    app.add_config_value("clear_urlinclude_folder", False, "html")
    return {"version": _EXTENSION_VERSION}
