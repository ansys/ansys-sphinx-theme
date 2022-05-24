"""This module creates the title page for a LaTeX pdf."""
from datetime import datetime
import os
from pathlib import Path

import jinja2

LATEX_SUBPKG = Path(os.path.dirname(os.path.realpath(__file__)))
COVER_TEX = LATEX_SUBPKG / "cover.tex"


def generate_preamble(title, watermark="watermark", year=None):
    """Return the latex macros for the title page."""
    if year is None:
        year = datetime.today().year
    variables = dict(_title=title, _watermark=watermark, _year=year)

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
