"""link code file."""
import inspect
import os
import os.path as op
import sys

from sphinx.application import Sphinx


def linkcode_resolve(domain, info, edit=False, version=None, app: Sphinx = None):
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

    repository = "ansys/pypim"  # Replace with your repository owner/repo
    kind = "main"  # Or any versioning convention you want
    print(fn)

    blob_or_edit = "edit" if edit else "blob"
    return f"http://github.com/{repository}/{blob_or_edit}/{kind}/{fn}{linespec}"
