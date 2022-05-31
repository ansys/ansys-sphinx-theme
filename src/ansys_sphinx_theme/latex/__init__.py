"""This module creates the title page for a LaTeX pdf."""
from datetime import datetime
import os
from pathlib import Path

import jinja2

LATEX_SUBPKG = Path(os.path.dirname(os.path.realpath(__file__)))
COVER_TEX = LATEX_SUBPKG / "cover.tex"


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
        block_start_string="\BLOCK{",
        block_end_string="}",
        variable_start_string="\pyvar{",
        variable_end_string="}",
        comment_start_string="\#{",
        comment_end_string="}",
        line_statement_prefix="%%",
        line_comment_prefix="%#",
        trim_blocks=True,
        autoescape=False,
        loader=jinja2.FileSystemLoader(COVER_TEX),
    )
    template = latex_jinja_env.get_template(".")
    return template.render(variables)
