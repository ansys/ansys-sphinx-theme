"""This is module to create coverpage to the latex pdf."""
import os

import jinja2


def generate_preamble(title, watermark="watermark"):
    """Return the latex macrosfor title page."""
    variables = dict(Project_title=title, Watermark=watermark)

    latex_jinja_env = jinja2.Environment(
        block_start_string="\BLOCK{",
        block_end_string="}",
        variable_start_string="\VAR{",
        variable_end_string="}",
        comment_start_string="\#{",
        comment_end_string="}",
        line_statement_prefix="%%",
        line_comment_prefix="%#",
        trim_blocks=True,
        autoescape=False,
        loader=jinja2.FileSystemLoader(os.path.dirname(os.path.realpath(__file__))),
    )
    template = latex_jinja_env.get_template("cover.tex")
    return template.render(variables)
