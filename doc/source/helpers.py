"""Helper classes and functions for documentation build."""

from docutils.parsers.rst import Directive
import sphinx


def get_page_vars(app: sphinx.app, pagename: str) -> dict:
    """Get page variables.

    Get each page variables.

    Parameters
    ----------
    app : app
        Sphinx app
    pagename : str
        Page name

    Returns
    -------
    dict
        Dictionary with variables as keys, and their values.
    """
    env = app.builder.env

    if (
        not hasattr(env, "pages_vars")
        or not env.pages_vars
        or not env.pages_vars.get(pagename, None)
    ):
        return

    return env.pages_vars[pagename]


class SetPageVariableDirective(Directive):
    """Set page variables.

    Set page variables.

    Parameters
    ----------
    - variable: str
    - value: str

    Example

    .. setpagevar:: my_key my_value

    The key cannot have spaces.

    .. setpagevar:: my_key my value

    """

    has_content = False
    required_arguments = 2  # Variable name and value
    optional_arguments = 0

    def run(self):
        """Run directive."""
        var_name = self.arguments[0]
        var_value = self.arguments[1]
        env = self.state.document.settings.env

        # Store the variable in the environment specific to each page
        if not hasattr(env, "pages_vars"):
            env.pages_vars = {}

        # Store the variable for the current page (env.docname is the document name)
        if env.docname not in env.pages_vars:
            env.pages_vars[env.docname] = {}

        env.pages_vars[env.docname][var_name] = var_value

        return []


def add_custom_variables_to_context(
    app: sphinx.app,
    pagename: str,
    templatename: str,
    context: sphinx.context,
    doctree: sphinx.doctree,
) -> None:
    """Add customs variables to build context.

    This is needed to be able to access the vars at the build stage.

    Parameters
    ----------
    app : Sphinx.app
        Sphinx app.
    pagename : str
        Page name
    templatename : str
        Template page
    context : Sphinx.context
        Page context
    doctree : Sphinx.doctree
        Page doctree
    """
    env = app.builder.env

    # Check if there are page-specific variables stored by the directive
    if hasattr(env, "pages_vars"):
        if pagename in env.pages_vars:
            # Add the stored variables to the context for this page
            context.update(env.pages_vars[pagename])
