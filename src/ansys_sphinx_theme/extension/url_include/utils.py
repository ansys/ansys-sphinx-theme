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

"""Utility functions and classes for the urlinclude extension."""

from pathlib import Path

from docutils import nodes
from sphinx.util import logging

logger = logging.getLogger(__name__)


def add_literal_block(text: str, language: str) -> nodes.literal_block:
    """Create a literal text block with the given text and language.

    Parameters
    ----------
    text : str
        The text to include in the literal block.
    language : str
        The language for the literal block.

    Returns
    -------
    nodes.literal_block
        The literal block node.
    """
    literal = nodes.literal_block(text, text)
    literal["language"] = language
    return literal


def create_temp_file(temp_folder_path: str, content: str, file_name: str) -> Path:
    """Create a temporary file with the given content.

    Parameters
    ----------
    temp_folder_path : str
        The path to the temporary folder.
    content : str
        The content to write to the file.
    file_name : str
        The name of the file.

    Returns
    -------
    Path
        The path to the temporary file.
    """
    temp_folder = Path(temp_folder_path)
    Path(temp_folder).mkdir(parents=True, exist_ok=True)

    file_path = Path(temp_folder) / file_name
    with Path.open(file_path, "w", encoding="utf-8") as f:
        f.write(content)
    return file_path
