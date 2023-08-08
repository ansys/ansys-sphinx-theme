"""Docstring missing."""
import inspect
import os
import os.path as op
import sys

from docutils import nodes
from docutils.nodes import Node
import sphinx
from sphinx import addnodes
from sphinx.application import Sphinx
from sphinx.locale import _


def sphinx_linkcode_resolve(
    domain: str, info: dict, library: str, source_path, github_version, edit: bool = False
) -> str or None:
    """Resolve the URL corresponding to a Python object for linking to the source code.

    Parameters
    ----------
    domain : str
        The domain of the object (e.g., 'py' for Python).

    info : dict
        Dictionary containing the information about the object.
        It must have the keys 'module' and 'fullname'.

    library : str
        The repository/library name where the source code is hosted.
        For example, 'ansys/ansys-sphinx-theme'.

    version : str
        The version of the library. It can be a specific version like '1.2.0' or 'dev'.
        For versioned links, the version will be used in the URL.

    edit : bool, optional, default=False
        If ``True`` , the link should point to the edit page for the source code.
        Otherwise, it will point to the view page.

    Returns
    -------
    str or None
        The code URL or None if it cannot be determined.

    Notes
    -----
    This function is used by the `sphinx.ext.linkcode` extension to create the "[Source]"
    button whose link is edited in this function.

    References
    ----------
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
    """Automatically add "View Source" links to the documentation.

    This function is an event handler that automatically adds "View Source" links to the
    documentation for Python, C, C++, and JavaScript objects. It is designed to work with
    the Sphinx documentation tool.

    Parameters
    ----------
    app : sphinx.application.Sphinx
        The Sphinx application instance.
    doctree : docutils.nodes.Node
        The document tree for the current page.

    Notes
    -----
    The function uses the `sphinx_linkcode_resolve` function to res
    olve the link for each
    documented object. The link is added as a "View Source" link to the documentation
    when rendered.

    For Python, the function extracts information such as module name and fullname from
    the signature node to create the link.

    The `link_code_library` configuration option can be used to specify a custom library
    for link resolution.

    Notes
    -----
    Sphinx GitHub repository for `linkcode` extension:
    https://github.com/sphinx-doc/sphinx/blob/main/sphinx/ext/linkcode.py

    """
    env = app.builder.env
    html_context = getattr(env.config, "html_context")
    github_user = html_context.get("github_user", "")
    github_repo = html_context.get("github_repo", "")
    github_source = html_context.get("source_path", "")
    github_version = html_context.get("github_version", "main")
    if github_user and github_repo:
        library = f"{github_user}/{github_repo}"
    elif hasattr(env.config, "link_code_library") and hasattr(env.config, "link_code_source"):
        library = getattr(env.config, "link_code_library")
        github_source = getattr(env.config, "link_code_source")
        github_version = getattr(env.config, "link_code_branch")

    else:
        raise AttributeError("The library should have either html_context or link_code_library.")
    if not library:
        raise AttributeError(
            "The conf.py file either should have html_context or link_code_library with github_repo and github_user."  # noqa: E501
        )
    domain_keys = {
        "py": ["module", "fullname"],
        "c": ["names"],
        "cpp": ["names"],
        "js": ["object", "fullname"],
    }

    for objnode in list(doctree.findall(addnodes.desc)):
        domain = objnode.get("domain")
        uris: set[str] = set()
        for signode in objnode:
            if not isinstance(signode, addnodes.desc_signature):
                continue

            # Convert signode to a specified format
            info = {}
            for key in domain_keys.get(domain, []):
                value = signode.get(key)
                if not value:
                    value = ""
                info[key] = value
            if not info:
                continue

            # Call user code to resolve the link
            uri = sphinx_linkcode_resolve(
                domain=domain,
                info=info,
                library=library,
                source_path=github_source,
                github_version=github_version,
            )
            if not uri:
                # no source
                continue

            if uri in uris or not uri:
                # only one link per name, please
                continue
            uris.add(uri)

            inline = nodes.inline("", _("[source]"), classes=["viewcode-link"])
            onlynode = addnodes.only(expr="html")
            onlynode += nodes.reference("", "", inline, internal=False, refuri=uri)
            signode += onlynode


def setup(app: Sphinx):
    """Initialize the linkcode extension for Sphinx.

    This function initializes the linkcode extension for Sphinx. It connects the
    `linkcode` function to the "doctree-read" event and adds the "link_code_library"
    configuration option.

    Parameters
    ----------
    app : sphinx.application.Sphinx
        The Sphinx application instance.

    Returns
    -------
    dict
        A dictionary containing configuration values for the extension.

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
