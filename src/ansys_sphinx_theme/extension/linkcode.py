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


def sphinx_linkcode_resolve(domain, info, library, version, edit=False):
    """Determine the URL corresponding to a Python object.

    Parameters
    ----------
    domain : str
        The domain of the object (e.g., 'py' for Python).

    info : dict
        Dictionary containing the information about the object.
        It must have the keys 'module' and 'fullname'.

    edit : bool, default=False
        If True, the link should point to the edit page.

    app : Sphinx, optional
        The Sphinx application instance for rendering the documentation.
        This argument is optional, but if not provided, the library version check will be skipped.

    Returns
    -------
    str or None
        The code URL or None if it cannot be determined.

    Notes
    -----
    This function is used by the `sphinx.ext.linkcode` extension to create the "[Source]"
    button whose link is edited in this function.
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

    # deal with our decorators properly
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
    repo_index = fn_components.index("src")
    fn = "/".join(fn_components[repo_index:])  # in case on Windows

    try:
        source, lineno = inspect.getsourcelines(obj)
    except Exception:  # pragma: no cover
        lineno = None

    if lineno and not edit:
        linespec = f"#L{lineno}-L{lineno + len(source) - 1}"
    else:
        linespec = ""

    repository = (
        library  # Replace with your repository owner/repo  # Or any versioning convention you want
    )
    library_version = version
    if "dev" in library_version:
        kind = "main"
    else:  # pragma: no cover
        kind = "release/%s" % (".".join(library_version.split(".")[:2]))

    blob_or_edit = "edit" if edit else "blob"
    return f"http://github.com/{repository}/{blob_or_edit}/{kind}/{fn}{linespec}"


def linkcode(app: Sphinx, doctree: Node):
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

    References
    ----------
    Sphinx GitHub repository for `linkcode` extension:
    https://github.com/sphinx-doc/sphinx/blob/main/sphinx/ext/linkcode.py

    """
    env = app.builder.env
    version = getattr(env.config, "version", None)

    domain_keys = {
        "py": ["module", "fullname"],
        "c": ["names"],
        "cpp": ["names"],
        "js": ["object", "fullname"],
    }

    library = getattr(env.config, "link_code_library", "")

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
            uri = sphinx_linkcode_resolve(domain, info, library, version)
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

    References
    ----------
    Sphinx GitHub repository for `linkcode` extension:
    https://github.com/sphinx-doc/sphinx/blob/main/sphinx/ext/linkcode.py

    """
    app.connect("doctree-read", linkcode)
    app.add_config_value("link_code_library", None, "")
    return {"version": sphinx.__display_version__, "parallel_read_safe": True}
