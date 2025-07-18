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

"""Module to configure cheatsheet options and build the Quarto cheatsheet.

This module provides functions to configure cheatsheet options, build the Quarto cheatsheet,
and add the cheatsheet to the left navigation sidebar.
"""

import pathlib

# Excudind bandit rule B404 as we are using subprocess to run commands
# and we are handling the command execution securely.
import subprocess  # nosec: B404
from typing import List, Optional

from sphinx.application import Sphinx
from sphinx.util import logging

logger = logging.getLogger(__name__)

# Cheat sheet extension version
CHEAT_SHEET_QUARTO_EXTENTION_VERSION = "v1"


def cheatsheet_sidebar_pages(app: Sphinx) -> Optional[List[str]]:
    """
    Get the pages to display the cheat sheet sidebar and return the list of pages.

    Parameters
    ----------
    app : sphinx.application.Sphinx
        Application instance for rendering the documentation.

    Returns
    -------
    Optional[List[str]]
        List of pages to display the cheat sheet sidebar, or None if not configured.
    """
    html_theme_options = app.config.html_theme_options
    cheatsheet_options = html_theme_options.get("cheatsheet")
    if not cheatsheet_options:
        return None
    pages = cheatsheet_options.get("pages", ["index"])
    cheatsheet_pages = [pages] if isinstance(pages, str) else pages
    return cheatsheet_pages


def convert_pdf_to_png(pdf_path: pathlib.Path, output_dir: pathlib.Path, output_png: str) -> None:
    """
    Convert PDF to PNG images.

    Parameters
    ----------
    pdf_path : pathlib.Path
        Path to the PDF file.
    output_dir : pathlib.Path
        Path to the output directory.
    output_png : str
        Name of the output PNG file.
    """
    try:
        from pdf2image import convert_from_path
    except ImportError as e:
        raise ImportError(
            f"Failed to import `pdf2image`: {e}. Install the package using `pip install pdf2image`"
        )
    try:
        images = convert_from_path(pdf_path, 500)
        images[0].save(output_dir / output_png, "PNG")
    except Exception as e:
        raise RuntimeError(
            f"Failed to convert PDF to PNG: {e}. Ensure the PDF file is valid and poppler is installed."  # noqa:E501
        )


def run_quarto_command(command: List[str], cwd: str) -> None:
    """
    Run a Quarto command and log its output.

    Parameters
    ----------
    command : List[str]
        List of command arguments.
    cwd : str
        Current working directory.
    """
    command = ["quarto"] + command
    try:
        # Excluding bandit rule because subprocess is using quarto command
        # and we are handling the command execution securely.
        # The command is run in a controlled environment and not accepting user input.
        result = subprocess.run(command, cwd=cwd, check=True, capture_output=True, text=True)  # nosec: B603
        if result.stdout:
            logger.info(result.stdout)

        if result.stderr:
            # HACK: Quarto writes both stdout and stderr to stderr
            # so we need to log it as info if it's not an error
            logger.info(result.stderr)

    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Failed to run the command: {e}")


def build_quarto_cheatsheet(app: Sphinx) -> None:
    """
    Build the Quarto cheatsheet.

    Parameters
    ----------
    app : sphinx.application.Sphinx
        Application instance for rendering the documentation.
    """
    cheatsheet_options = app.config.html_theme_options.get("cheatsheet", {})

    if not cheatsheet_options:
        return

    cheatsheet_file = cheatsheet_options.get("file", "")
    if not cheatsheet_file:
        return

    output_dir = "_static"
    version = cheatsheet_options.get("version", "main")

    cheatsheet_file = pathlib.Path(app.srcdir) / cheatsheet_file
    output_dir_path = pathlib.Path(app.outdir) / output_dir
    file_name = str(cheatsheet_file.name)
    file_path = cheatsheet_file.parent

    logger.info(f"Building Quarto cheatsheet: {file_name}")

    # Adapt with new
    run_quarto_command(["--version"], file_path)
    run_quarto_command(
        [
            "add",
            f"ansys/pyansys-quarto-cheatsheet@{CHEAT_SHEET_QUARTO_EXTENTION_VERSION}",
            "--no-prompt",
        ],
        file_path,
    )
    run_quarto_command(
        [
            "render",
            file_name,
            "--to",
            "cheat_sheet-pdf",
            "--output-dir",
            output_dir_path,
            "-V",
            f"version={version}",
        ],
        file_path,
    )
    run_quarto_command(
        ["remove", "ansys/pyansys-quarto-cheatsheet", "--no-prompt"],
        file_path,
    )
    supplementary_files = [
        "_static/slash.png",
        "_static/bground.png",
        "_static/ansys.png",
    ]
    for file in supplementary_files:
        file_path = cheatsheet_file.parent / file
        if file_path.exists():
            file_path.unlink()

    # If static folder is clean, delete it
    if not list(cheatsheet_file.parent.glob("_static/*")):
        cheatsheet_file.parent.joinpath("_static").rmdir()

    output_file = output_dir_path / file_name.replace(".qmd", ".pdf")
    app.config.html_theme_options["cheatsheet"]["output_dir"] = f"{output_dir}/{output_file.name}"
    output_png = file_name.replace(".qmd", ".png")
    # Check output file exists
    if not output_file.exists():
        raise FileNotFoundError(f"Failed to build Quarto cheatsheet: {output_file} does not exist.")

    convert_pdf_to_png(output_file, output_dir_path, output_png)
    logger.info(f"Cheat sheet build finished successfully: {output_file}")
    app.config.html_theme_options["cheatsheet"]["thumbnail"] = f"{output_dir}/{output_png}"
