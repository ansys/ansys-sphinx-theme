"""A module containing the an extension for creating links to original source code files."""
import inspect
import logging
import os
import os.path as op
import sys

from docutils import nodes
from docutils.nodes import Node
import sphinx
from sphinx import addnodes
from sphinx.application import Sphinx
from sphinx.locale import _

"""
DOMAIN_KEYS: Dictionary containing information about supported
programming languages and their corresponding domain keys.

This dictionary maps programming language codes to a list of domain keys that
can be used to extract specific information related to the language.

- 'py': Python language information keys:
  - 'module': Key to access module information.
  - 'fullname': Key to access full name information.

- 'c': C language information keys:
  - 'names': Key to access name information.

- 'cpp': C++ language information keys:
  - 'names': Key to access name information.

- 'js': JavaScript language information keys:
  - 'object': Key to access object information.
  - 'fullname': Key to access full name information.

"""
DOMAIN_KEYS = {
    "py": ["module", "fullname"],
    "c": ["names"],
    "cpp": ["names"],
    "js": ["object", "fullname"],
}


def sphinx_linkcode_resolve(
    domain: str, info: dict, library: str, source_path: str, github_version: str, edit: bool = False
) -> str or None:
    """
    Resolve the URL corresponding to a Python object for linking to the source code.

    Parameters
    ----------
    domain : str
        Domain of the object (e.g., 'py' for Python).
    info : dict
        Dictionary containing the information about the object.
        It must have the keys 'module' and 'fullname'.
    library : str
        Repository/library name where the source code is hosted.
        For example, 'ansys/ansys-sphinx-theme'.
    source_path : str
        Relative path of the source code file within the repository.
        For example, 'src'.
    github_version : str
        Version of the library in github. It can be a specific version like
        'main' or 'release/branch'.For versioned links, the version will be used in the URL.
    edit : bool, default : False
        If ``True``, the link should point to the edit page for the source code.
        Otherwise, it will point to the view page.

    Returns
    -------
    str or None
        Code URL or ``None`` if it cannot be determined.

    Notes
    -----
    This function is used by the `sphinx.ext.linkcode` extension to create the "[Source]"
    button whose link is edited in this function.

    Adapted from the link_code extension implemented in pyvista. See
    GitHub pull request: https://github.com/pyvista/pyvista/pull/4113
    (Author: Alex kaszynski <https://github.com/akaszynski>)
    """
    if domain != "py":
        return None

    modname = info["module"]
    fullname = info["fullname"]

    # Little clean up to avoid library.library
    if fullname.startswith(modname):
        fullname = fullname[len(modname) + 1 :]

    submod = sys.modules.get(modname)
    if submod is None:
        return None

    obj = submod
    for part in fullname.split("."):
        try:
            obj = getattr(obj, part)
        except Exception:
            return None

    # Deal with our decorators properly
    while hasattr(obj, "fget"):
        obj = obj.fget

    try:
        fn = inspect.getsourcefile(obj)
    except Exception:  # pragma: no cover
        fn = None

    if not fn:  # pragma: no cover
        try:
            fn = inspect.getsourcefile(sys.modules[obj.__module__])
        except Exception:
            return None
        return None

    fn = op.relpath(fn, start=os.path.dirname(os.path.abspath(__file__)))
    fn_components = op.normpath(fn).split(os.sep)

    if not source_path:
        module = modname.split(".")[0]
        repo_index = fn_components.index(module)
    else:
        if source_path in fn_components:
            repo_index = fn_components.index(source_path)
        else:
            module = modname.split(".")[0]
            repo_index = fn_components.index(module)
            fn_components.insert(repo_index, source_path)
    fn = "/".join(fn_components[repo_index:])

    try:
        source, lineno = inspect.getsourcelines(obj)
    except Exception:  # pragma: no cover
        lineno = None

    if lineno and not edit:
        linespec = f"#L{lineno}-L{lineno + len(source) - 1}"
    else:
        linespec = ""

    blob_or_edit = "edit" if edit else "blob"
    return f"http://github.com/{library}/{blob_or_edit}/{github_version}/{fn}{linespec}"


def link_code(app: Sphinx, doctree: Node):
    """
    Automatically add "View Source" links to the documentation.

    This function is an event handler that automatically adds "View Source" links to the
    documentation for Python, C, C++, and JavaScript objects. It is designed to work with
    the Sphinx documentation tool.

    Parameters
    ----------
    app : sphinx.application.Sphinx
        Sphinx application instance.
    doctree : docutils.nodes.Node
        Document tree for the current page.

    Notes
    -----
    The function uses the `sphinx_linkcode_resolve` function to resolve the link for each
    documented object. The link is added as a "View Source" link to the documentation
    when rendered.

    For Python, the function extracts information such as module name and fullname from
    the signature node to create the link.

    The `link_code_library` configuration option can be used to specify a custom library
    for link resolution.

    Notes
    -----
    Adapted from the original `linkcode` extension in Sphinx, see
    https://github.com/sphinx-doc/sphinx/blob/main/sphinx/ext/linkcode.py
    """
    env = app.builder.env
    html_context = getattr(env.config, "html_context", {})
    github_user = html_context.get("github_user", "")
    github_repo = html_context.get("github_repo", "")
    source_path = html_context.get("source_path", "")
    github_version = html_context.get("github_version", "main")

    if getattr(env.config, "link_code_library"):
        library = getattr(env.config, "link_code_library")

    elif github_user and github_repo:
        library = f"{github_user}/{github_repo}"

    else:
        raise AttributeError("The library should have either html_context or link_code_library.")

    github_source = (
        env.config.link_code_source if getattr(env.config, "link_code_source") else source_path
    )
    github_version = (
        env.config.link_code_branch if getattr(env.config, "link_code_branch") else github_version
    )

    if not library:
        raise AttributeError(
            "The conf.py file either should have html_context or link_code_library with github_repo and github_user."  # noqa: E501
        )

    for objnode in list(doctree.findall(addnodes.desc)):
        domain = objnode.get("domain")
        uris: set[str] = set()
        for signode in objnode:
            if not isinstance(signode, addnodes.desc_signature):
                continue

            # Convert signode to a specified format
            info = {}
            for key in DOMAIN_KEYS.get(domain, []):
                value = signode.get(key)
                if not value:
                    value = ""
                info[key] = value
            if not info:
                continue

            # Call user code to resolve the link
            try:
                # Resolve the URI for source code link
                uri = sphinx_linkcode_resolve(
                    domain=domain,
                    info=info,
                    library=library,
                    source_path=github_source,
                    github_version=github_version,
                )

                # Check if the URI is already processed
                if not uri or uri in uris:
                    # Skip processing if the URI is already in the set
                    continue
                uris.add(uri)

                inline = nodes.inline("", _("[source]"), classes=["viewcode-link"])
                onlynode = addnodes.only(expr="html")
                onlynode += nodes.reference("", "", inline, internal=False, refuri=uri)
                signode += onlynode

            except ValueError as e:
                logging.debug(f"An error occurred: {e}")


def setup(app: Sphinx):
    """
    Initialize the linkcode extension for Sphinx.

    This function initializes the linkcode extension for Sphinx. It connects the
    `link_code` function to the "doctree-read" event and adds the "link_code_library"
    configuration option.

    Parameters
    ----------
    app : sphinx.application.Sphinx
        Sphinx application instance.

    Returns
    -------
    dict
        Dictionary containing configuration values for the extension.

    Notes
    -----
    Sphinx GitHub repository for `linkcode` extension:
    https://github.com/sphinx-doc/sphinx/blob/main/sphinx/ext/linkcode.py
    """
    app.connect("doctree-read", link_code)
    app.add_config_value("link_code_library", None, "")
    app.add_config_value("link_code_source", None, "")
    app.add_config_value("link_code_branch", None, "")
    return {"version": sphinx.__display_version__, "parallel_read_safe": True}
