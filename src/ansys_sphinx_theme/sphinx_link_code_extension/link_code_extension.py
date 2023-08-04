"""Module containing linkcode extension."""

import inspect
import os.path as op


def linkcode_resolve(domain, info, library, edit=False):
    """Determine the URL corresponding to a Python object.

    Parameters
    ----------
    domain : str
        The domain of the object (e.g., 'py' for Python).

    info : dict
        Dictionary containing the information about the object.
        It must have the keys 'module' and 'fullname'.

    library : module
        The module representing the library for which the code link is generated.

    edit : bool, default=False
        If True, the link should point to the edit page.

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

    fn = op.relpath(fn, start=op.dirname(library.__file__))
    fn = "/".join(op.normpath(fn).split(os.sep))  # in case on Windows

    try:
        source, lineno = inspect.getsourcelines(obj)
    except Exception:  # pragma: no cover
        lineno = None

    if lineno and not edit:
        linespec = f"#L{lineno}-L{lineno + len(source) - 1}"
    else:
        linespec = ""

    # Get the library version from the module's '__version__' attribute
    version = getattr(library, "__version__", "")
    if "dev" in version:
        kind = "main"
    else:  # pragma: no cover
        kind = "release/%s" % (".".join(version.split(".")[:2]))

    blob_or_edit = "edit" if edit else "blob"

    return f"http://github.com/{library}/{blob_or_edit}/{kind}/{fn}{linespec}"
