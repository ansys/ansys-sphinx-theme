"""This is module to create coverpage to the latex pdf."""
import os
from pathlib import Path

import jinja2

LATEX_SUBPKG = Path(os.path.dirname(os.path.abspath(__file__)))
COVER_TEX = "cover.tex"


def generate_preamble(title, watermark="watermark"):
    """Return the latex macrosfor title page."""
    variables = dict(_title=title, _watermark=watermark)

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
        loader=jinja2.FileSystemLoader(LATEX_SUBPKG),
    )
    template = latex_jinja_env.get_template(COVER_TEX)
    return template.render(variables)
