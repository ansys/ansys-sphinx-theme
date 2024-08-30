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

"""Module creates the title page for a LaTeX pdf."""

from datetime import datetime
from pathlib import Path

import jinja2

LATEX_SUBPKG = Path(__file__).resolve().parent
COVER_TEX = LATEX_SUBPKG / "cover.tex"
PAGE_404 = LATEX_SUBPKG / "404.html"


def generate_preamble(title, watermark="watermark", date=None):
    """Generate the preamble for the PDF documentation.

    Parameters
    ----------
    title : str
        Title of the document.
    watermark : str, optional
        Name of the watermark image.
    date : ~datetime.datetime, optional
        Date of document generation. If not provided, today's date is used.

    Returns
    -------
    str
        A string representing the LaTeX source code for the preamble.

    """
    if date is None:
        date = datetime.today()
    variables = dict(_title=title, _watermark=watermark, _date=date)

    latex_jinja_env = jinja2.Environment(
        block_start_string="\\BLOCK{",
        block_end_string="}",
        variable_start_string="\\pyvar{",
        variable_end_string="}",
        comment_start_string="\\#{",
        comment_end_string="}",
        line_statement_prefix="%%",
        line_comment_prefix="%#",
        trim_blocks=True,
        autoescape=False,
        loader=jinja2.FileSystemLoader(COVER_TEX),
    )
    template = latex_jinja_env.get_template(".")
    return template.render(variables)


def generate_404(
    owner="ansys",
    project_name="ansys-sphinx-theme",
    mail_id="pyansys.support@ansys.com",
    team_name="PyAnsys",
):
    """Generate the html body for 404 page.

    Parameters
    ----------
    owner : str, default: "ansys"
        GitHub organisation in which the project belongs to.
    project_name : str, default: "ansys-sphinx-theme"
        Name of the project.
    mail_id : str, default: "pyansys.support@ansys.com"
        E-mail address to contact.
    team_name : str, default: "PyAnsys"
       Name of the team.

    Returns
    -------
    str
        A string representing the html source code for the 404 page.

    """
    issue_page = f"https://github.com/{owner}/{project_name}/issues/"
    variables = dict(
        issue_page=issue_page, project_name=project_name, mail_id=mail_id, team_name=team_name
    )
    html_env = jinja2.Environment(loader=jinja2.FileSystemLoader(PAGE_404))
    template = html_env.get_template(".")
    return template.render(variables)
