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
