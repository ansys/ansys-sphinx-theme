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

"""Jinja include module contains the JinjaRead class."""

from jinja2 import Environment, meta
from sphinx.util import logging

from ansys_sphinx_theme.extension.url_include import add_literal_block, create_temp_file

logger = logging.getLogger(__name__)


class JinjaRead:
    """JinjaRead class."""

    TITLE_LEVELS = ["#", "*", "=", "-", "^", '"', "~"]

    def __init__(self, text_content, line_number, state):
        """Initialize JinjaRead.

        Parameters
        ----------
        text_content : str
            The text content of the include directive.
        line_number : int
            The line number in the document.
        state : object
            The state object.
        """
        self.text_content = text_content
        self.variable_count = None
        self.unique_variables = None
        self.variable_values = None
        self.lineno = line_number
        self.state = state
        self.title_level = self.state.memo.title_styles
        self.starting_level = None
        self.template_env = Environment()

    def get_variable_count(self):
        """Get the number of variables."""
        parsed_template = self.template_env.parse(self.text_content)
        self.unique_variables = meta.find_undeclared_variables(parsed_template)
        self.variable_count = len(self.unique_variables)

    def get_variable_values(self, contents):
        """Get the values of the variables."""
        self.get_variable_count()
        self.variable_values = {}
        if "render_header_level" not in contents and "render_header_level" in self.unique_variables:
            contents["render_header_level"] = self.render_header_level

        missing_variables = self.unique_variables - set(contents.keys())
        missing_variables_str = ", ".join(missing_variables)
        if len(contents) < self.variable_count:
            logger.warning(
                f"Contents does not have all the variables. Expected {self.variable_count} variables.\n\t{missing_variables_str} are missing in {self.state.document.current_source}:{self.lineno}"  # noqa: E501
            )

        for variable in self.unique_variables:
            if contents.get(variable):
                self.variable_values[variable] = contents.get(variable)

    def render_header_level(self, title="", level=0):
        """Render the header level.

        Parameters
        ----------
        title : str, optional
            The title of the header, by default ""
        level : int, optional
            The level of the header, by default 0

        Returns
        -------
        str
            The title times the underline character.

        Examples
        --------
        >>> render_header_level("test", 0)
        '####'
        >>> render_header_level("test", 1)
        '****'
        """
        header_length = len(title)

        previous_title_level = "=" if not self.title_level else self.title_level[-1]

        if self.starting_level is None:
            self.starting_level = self.TITLE_LEVELS.index(previous_title_level) + 1

        current_section_level = self.starting_level + level
        underline_char = self.TITLE_LEVELS[current_section_level]

        return underline_char * header_length

    def get_jinja_template(self):
        """Get the jinja template.

        Returns
        -------
        str
            The jinja template.
        """
        template = self.template_env.from_string(self.text_content)
        j2_template = template.render(self.variable_values)
        return j2_template


def jinja_literal_block(text, contents, language, lineno, state):
    """Create a literal text block with Jinja variables rendered.

    Parameters
    ----------
    text : str
        The text content of the include directive.
    contents : dict
        The contents of the include directive.

    Returns
    -------
    str
        The rendered Jinja template.
    """
    jinja_read = JinjaRead(text, line_number=lineno, state=state)
    jinja_read.get_variable_values(contents)
    j2_template = jinja_read.get_jinja_template()
    return add_literal_block(j2_template, language)


def jinja_raw_block(temp_folder_name, filename, text, url, contents, lineno, state):
    """Create a Jinja raw block.

    Parameters
    ----------
    temp_folder_name : str
        The temporary folder name.
    filename : str
        The filename.
    text : str
        The text content of the include directive.
    url : str
        The URL of the file.
    contents : dict
        The contents of the include directive.
    lineno : int
        The line number in the document.
    state : object
        The state object.

    Returns
    -------
    str
        The temporary file path.
    """
    jinja_read = JinjaRead(text, line_number=lineno, state=state)
    jinja_read.get_variable_values(contents)
    temp_file = create_temp_file(temp_folder_name, jinja_read.get_jinja_template(), filename)
    return temp_file
