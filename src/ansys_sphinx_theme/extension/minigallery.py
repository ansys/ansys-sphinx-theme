# Copyright (C) 2021 - 2026 ANSYS, Inc. and/or its affiliates.
# SPDX-License-Identifier: MIT
#
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""Minigallery extension for the Ansys Sphinx Theme.

This extension scans configured example directories — including both
**sphinx-gallery** ``.py`` example scripts and **Jupyter** ``.ipynb`` notebooks
— and builds a backreferences map that links every API object (class, function,
module) to the examples that reference it.

The resulting minigallery is automatically injected at the bottom of every
``autoapi`` class, function, and module page via the
``.. ansys-minigallery::`` directive, which is also available for manual use
anywhere in the documentation.

Configuration
-------------
Options are nested inside the existing ``ansys_sphinx_theme_autoapi`` theme
option dict inside ``html_theme_options``:

.. code-block:: python

    html_theme_options = {
        "ansys_sphinx_theme_autoapi": {
            ...
            # List of example directories relative to the repository root.
            # Both sphinx-gallery .py files and Jupyter .ipynb notebooks are scanned.
            "examples_dirs": [
                "doc/source/examples/sphinx-gallery",
                "doc/source/examples/nbsphinx",
            ],
            # Only index FQNs that start with one of these package prefixes.
            # This filters out noise from numpy, matplotlib, etc.
            "fqn_prefixes": ["ansys.my_project"],
            # Optional: fallback thumbnail (relative to srcdir or absolute).
            "gallery_default_thumbnail": "_static/pyansys_light_square.png",
        }
    }

The extension also reads Sphinx config values directly (set automatically
by ``ansys_sphinx_theme.extension.autoapi``):

* ``ansys_gallery_dirs`` — list of example directory paths
* ``ansys_gallery_default_thumbnail`` — fallback thumbnail path
* ``ansys_gallery_fqn_prefixes`` — list of package-prefix strings for filtering
* ``ansys_gallery_json_sources`` — list of external-JSON config dicts
  (see ``examples_json`` below)

The examples JSON is always written automatically after each build.  The
filename is derived from the Sphinx ``project`` config value::

    {project_name}_examples.json   (e.g. ``ansys_sphinx_theme_examples.json``)

It is written to ``<outdir>/_static/`` and served as a downloadable static
asset.  Other projects can then consume this file via ``examples_json``.

Consuming external examples
---------------------------
To include examples from *another* project's docs in your own minigallery,
use the ``examples_json`` key.  Each entry is a dict with the following fields:

``file``
    **Required.** Path to the pre-built JSON file, relative to ``srcdir``
    (the ``conf.py`` directory).  The file must follow the format described
    below.

``base_url``
    URL prefix for the external docs site.  The final card link is built as
    ``base_url + "/" + <path-without-extension> + ".html"``.
    Use this for fully-hosted external examples (e.g. PyMechanical).

``base_docdir``
    Sphinx docname prefix prepended to each key stem to form a *local*
    docname (e.g. ``"examples/gallery-examples"``).  Use this when the
    other project's examples are included directly in the current doc tree.
    Ignored when ``base_url`` is set.

``fqn_prefixes``
    Per-entry filter list (e.g. ``["ansys.mechanical.core"]``).  Only FQNs
    that start with one of these prefixes are loaded from this JSON.  When
    omitted the global ``fqn_prefixes`` from ``ansys_sphinx_theme_autoapi``
    is used instead.

``base_examples_dir``
    Optional path to the actual source files (relative to ``srcdir``).  When
    provided the extension opens each file to extract the real title and
    thumbnail instead of deriving them from the filename.  Only useful for
    internal (local) JSON sources where the source files are available.

.. code-block:: python

    html_theme_options = {
        "ansys_sphinx_theme_autoapi": {
            ...
            # Consume examples from PyMechanical (external, hosted on another site).
            "examples_json": [
                {
                    "file": "_static/ansys_mechanical_core_examples.json",
                    "base_url": "https://examples.mechanical.docs.pyansys.com/examples/",
                    "fqn_prefixes": ["ansys.mechanical.core"],
                },
            ],
        }
    }

JSON file format
----------------
The JSON is a mapping of **dir-relative file paths** to lists of FQNs::

    {
        "00_basic/example_01.py":     ["pkg.math.Vector3D", "pkg.math.Point2D"],
        "01_advanced/workflow.ipynb": ["pkg.Modeler", "pkg.design.Design"]
    }

Keys are paths relative to the examples directory, preserving subdirectories
(e.g. ``"00_basic/example_01.py"`` rather than bare ``"example_01.py"``).  The
file extension determines the card type: ``.py`` → sphinx-gallery card, all
others → notebook card.  An empty list means the file was scanned but no
matching FQNs were found (these entries are omitted from the output).

Directive
---------
.. code-block:: rst

    .. ansys-minigallery:: ansys_sphinx_theme.examples.samples.ExampleClass
       :heading: Gallery examples
       :no-heading:
"""

import ast
import base64
from dataclasses import dataclass
import json
import os
from pathlib import Path
import re
from typing import Any, Dict, List, Optional

from docutils import nodes
from docutils.parsers.rst import Directive, directives
from docutils.statemachine import ViewList
from sphinx.application import Sphinx
from sphinx.util import logging as sphinx_logging

from ansys_sphinx_theme import __version__, pyansys_light_square_logo

logger = sphinx_logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------


@dataclass
class ExampleInfo:
    """Metadata about a single example that references an API object.

    Parameters
    ----------
    title : str
        Human-readable title of the example (extracted from docstring or
        markdown heading).
    doc_path : str
        Sphinx docname (relative to ``srcdir``, without extension) used for
        the ``:link:`` in the card.
    source_type : str
        Either ``"gallery"`` (sphinx-gallery ``.py``) or ``"notebook"``
        (Jupyter ``.ipynb``).
    src_file_abs : str
        Absolute path to the source file (``.py`` or ``.ipynb``).  Used to
        resolve the thumbnail lazily at directive render time, after
        sphinx-gallery has had a chance to generate its thumbnail images.
    thumbnail_uri : str
        Srcdir-relative path to the thumbnail image.  Empty string means
        "resolve lazily at render time" (used for gallery examples whose
        thumbnail is generated by sphinx-gallery during ``builder-inited``,
        which runs *after* our scan).
    """

    title: str
    doc_path: str
    source_type: str
    src_file_abs: str
    thumbnail_uri: str = ""
    link_type: str = "doc"  # "doc" for internal Sphinx docnames, "url" for external URLs


# ---------------------------------------------------------------------------
# AST helpers
# ---------------------------------------------------------------------------


def _fqn_set_from_source(source_code: str) -> set:
    """Return the set of fully-qualified names referenced in *source_code*.

    The function performs a two-pass analysis:

    1. Collect all ``import`` and ``from … import`` statements and build a
       local-alias → FQN mapping.
    2. Walk all ``Name`` and ``Attribute`` nodes, resolving them through the
       alias map to recover the original FQN.
    3. For every ``from X import Y`` import, attempt to dynamically resolve
       the *canonical* definition location (``Y.__module__ + "." +
       Y.__qualname__``) via :func:`_canonical_fqns_from_alias_map`.  This
       means that ``from ansys.dyna.core import Deck`` correctly produces
       *both* ``ansys.dyna.core.Deck`` (the import path) and
       ``ansys.dyna.core.deck.Deck`` (where autoapi generates the page).

    Parameters
    ----------
    source_code : str
        Python source code to analyse.

    Returns
    -------
    set[str]
        Every fully-qualified name encountered (imports + usages), including
        canonical definition locations resolved via the live Python runtime.
    """
    try:
        tree = ast.parse(source_code)
    except SyntaxError:
        return set()

    # Pass 1 — build alias map: local_name → fqn
    # Also keep track of which aliases came from "from X import Y" so we can
    # attempt runtime resolution.
    alias_map: Dict[str, str] = {}
    # Maps import-path FQN → (module_str, attr_name) for runtime resolution
    from_import_map: Dict[str, tuple] = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                local = alias.asname if alias.asname else alias.name
                alias_map[local] = alias.name
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ""
            for alias in node.names:
                if alias.name == "*":
                    continue
                local = alias.asname if alias.asname else alias.name
                fqn = f"{module}.{alias.name}" if module else alias.name
                alias_map[local] = fqn
                from_import_map[fqn] = (module, alias.name)

    # Pass 2 — collect referenced names
    refs: set = set(alias_map.values())  # every import is already a reference
    for node in ast.walk(tree):
        if isinstance(node, ast.Name):
            resolved = alias_map.get(node.id)
            if resolved:
                refs.add(resolved)
        elif isinstance(node, ast.Attribute):
            # Walk a.b.c chains to rebuild the dotted name
            parts: List[str] = []
            n = node
            while isinstance(n, ast.Attribute):
                parts.append(n.attr)
                n = n.value
            if isinstance(n, ast.Name) and n.id in alias_map:
                parts.append(n.id)
                parts.reverse()
                root_fqn = alias_map[parts[0]]
                remainder = ".".join(parts[1:])
                full = f"{root_fqn}.{remainder}" if remainder else root_fqn
                refs.add(full)
                # Also index every intermediate prefix so module-level lookups work
                segs = root_fqn.split(".") + parts[1:]
                for i in range(2, len(segs) + 1):
                    refs.add(".".join(segs[:i]))

    # Pass 3 — resolve canonical FQNs via the live runtime
    refs.update(_canonical_fqns_from_alias_map(from_import_map))

    return refs


def _canonical_fqns_from_alias_map(from_import_map: Dict[str, tuple]) -> set:
    """Resolve the canonical definition location for every ``from X import Y``.

    Python re-exports are common in large packages: ``ansys.dyna.core``
    re-exports ``Deck`` from ``ansys.dyna.core.deck``, so
    ``from ansys.dyna.core import Deck`` gives an AST FQN of
    ``ansys.dyna.core.Deck``, but autoapi generates a page for the definition
    site ``ansys.dyna.core.deck.Deck``.

    This function uses :mod:`importlib` to import each module and reads
    ``obj.__module__`` and ``obj.__qualname__`` to find where the object is
    actually defined.  Both the import-path FQN and the canonical FQN are
    returned so the minigallery matches either form.

    Failures (package not installed, import error, missing attribute) are
    silently skipped — the AST FQN is always kept regardless.

    Parameters
    ----------
    from_import_map : dict[str, tuple[str, str]]
        Mapping of ``import_fqn → (module_str, attr_name)`` collected during
        AST scanning.

    Returns
    -------
    set[str]
        Additional canonical FQNs to add alongside the AST-derived refs.
    """
    import importlib

    extra: set = set()
    for import_fqn, (module_str, attr_name) in from_import_map.items():
        if not module_str:
            continue
        try:
            mod = importlib.import_module(module_str)
            obj = getattr(mod, attr_name, None)
            if obj is None:
                continue
            obj_module = getattr(obj, "__module__", None)
            obj_qualname = getattr(obj, "__qualname__", None)
            if not obj_module or not obj_qualname:
                continue
            canonical = f"{obj_module}.{obj_qualname}"
            if canonical != import_fqn:
                extra.add(canonical)
                # Also add all intermediate prefixes so module-level pages match
                parts = canonical.split(".")
                for i in range(2, len(parts) + 1):
                    extra.add(".".join(parts[:i]))
        except Exception:
            logger.debug(f"ansys-minigallery: failed to resolve canonical FQN for {import_fqn}")
    return extra


# ---------------------------------------------------------------------------
# File-type parsers
# ---------------------------------------------------------------------------


def _parse_gallery_py(path: Path) -> tuple:
    """Parse a sphinx-gallery ``.py`` example file.

    Parameters
    ----------
    path : ~pathlib.Path
        Absolute path to the ``.py`` file.

    Returns
    -------
    tuple[str, set[str]]
        The human-readable title and the set of fully-qualified names
        referenced in the file.
    """
    source = path.read_text(encoding="utf-8")

    # Default: use the file stem
    title = path.stem.replace("_", " ").replace("-", " ").title()

    # Try to extract the title from the module-level docstring.
    # sphinx-gallery convention: first non-empty, non-underline line.
    try:
        tree = ast.parse(source)
        docstring = ast.get_docstring(tree) or ""
        for line in docstring.splitlines():
            stripped = line.strip()
            if stripped and not set(stripped).issubset(set("=-~^")):
                title = stripped
                break
    except SyntaxError:
        logger.info(
            f"ansys-minigallery: failed to parse {path} for title extraction; using filename."
        )

    fqns = _fqn_set_from_source(source)
    # Text-match pass: union AST results with library-JSON-guided text matching.
    _lib = getattr(_parse_gallery_py, "_lib_index", None)
    if _lib is not None:
        _, short_idx, qual_idx = _lib
        fqns = fqns | _text_match_fqns(source, short_idx, qual_idx)
    return title, fqns


def _strip_ipython_magics(source: str) -> str:
    """Strip IPython magic commands and shell commands from notebook cell source.

    Lines starting with ``%`` (line magics, e.g. ``%matplotlib inline``) or
    ``!`` (shell commands, e.g. ``!pip install foo``) are not valid Python
    syntax and cause :func:`ast.parse` to fail, silently dropping all imports
    in the same cell.  Cell magics (``%%timeit``, ``%%writefile``, etc.) make
    the *rest* of the cell non-Python as well, so the entire cell body is
    dropped when a ``%%`` line is encountered.

    Parameters
    ----------
    source : str
        Raw source of a single notebook code cell.

    Returns
    -------
    str
        Source with magic lines removed, safe to pass to :func:`ast.parse`.
    """
    lines = source.splitlines()
    cleaned: List[str] = []
    skip_rest = False
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("%%"):
            # Cell magic — the rest of the cell is non-Python (arguments/body).
            skip_rest = True
            continue
        if skip_rest:
            continue
        if stripped.startswith("%") or stripped.startswith("!"):
            # Line magic or shell command — skip this line only.
            continue
        cleaned.append(line)
    return "\n".join(cleaned)


def _parse_notebook(path: Path) -> tuple:
    """Parse a Jupyter notebook (``.ipynb``) file.

    Parameters
    ----------
    path : ~pathlib.Path
        Absolute path to the ``.ipynb`` file.

    Returns
    -------
    tuple[str, set[str], bytes | None]
        Human-readable title, set of fully-qualified names referenced in the
        notebook, and raw bytes of the first image output found (or ``None``).
    """
    try:
        nb = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return path.stem, set(), None

    cells = nb.get("cells", [])
    title = path.stem.replace("_", " ").replace("-", " ").title()
    fqns: set = set()
    thumbnail_data: Optional[bytes] = None
    title_found = False

    for cell in cells:
        cell_type = cell.get("cell_type", "")
        source_lines = cell.get("source", [])
        source = "".join(source_lines) if isinstance(source_lines, list) else str(source_lines)

        if cell_type == "markdown" and not title_found:
            for line in source.splitlines():
                stripped = line.strip()
                if stripped.startswith("# ") and not stripped.startswith("## "):
                    title = stripped[2:].strip()
                    title_found = True
                    break

        elif cell_type == "code":
            cleaned = _strip_ipython_magics(source)
            fqns.update(_fqn_set_from_source(cleaned))
            # Text-match on the RAW source (before magic stripping) so that
            # imports inside %%capture and other magic bodies are not lost.
            _lib = getattr(_parse_notebook, "_lib_index", None)
            if _lib is not None:
                _, short_idx, qual_idx = _lib
                fqns.update(_text_match_fqns(source, short_idx, qual_idx))

            # Extract the first image output as the thumbnail
            if thumbnail_data is None:
                for output in cell.get("outputs", []):
                    out_data = output.get("data", {})
                    for mime in ("image/png", "image/jpeg"):
                        if mime in out_data:
                            raw = out_data[mime]
                            if isinstance(raw, list):
                                raw = "".join(raw)
                            try:
                                thumbnail_data = base64.b64decode(raw)
                            except Exception:
                                logger.info(
                                    f"ansys-minigallery: failed to decode thumbnail image in {path}"
                                )
                            break
                    if thumbnail_data is not None:
                        break

    return title, fqns, thumbnail_data


def _parse_mystnb(path: Path) -> tuple:
    """Parse a MyST-NB (``.mystnb`` or text-based notebook) file.

    MyST-NB / Jupytext files are plain MyST Markdown documents with the
    following structure::

        ---
        jupytext:           ← YAML front-matter (skipped entirely)
          ...
        ---

        # Page Title       ← first level-1 heading becomes the title

        +++                 ← MyST-NB cell separator (ignored)

        ```{code-cell} ipython3
        from ansys.foo import Bar   ← code cells are AST-scanned for FQNs
        ```

    Parameters
    ----------
    path : ~pathlib.Path
        Absolute path to the MyST-NB file.

    Returns
    -------
    tuple[str, set[str]]
        Human-readable title and set of fully-qualified names referenced in
        the file.  No thumbnail bytes are returned (text notebooks rarely
        store embedded image output).
    """
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        return path.stem.replace("_", " ").replace("-", " ").title(), set()

    title = path.stem.replace("_", " ").replace("-", " ").title()
    fqns: set = set()
    title_found = False

    # --- State machine ---
    # States: "frontmatter", "body", "code_cell"
    state = "body"
    code_lines: List[str] = []
    fence_marker = ""  # backtick string that opened the current fence
    first_content_seen = False  # helps detect whether a leading --- starts front-matter

    for line in text.splitlines():
        stripped = line.strip()

        # ── front-matter detection ────────────────────────────────────────────
        # YAML front-matter is a `---` block at the very top of the file,
        # before any other non-empty content.
        if state == "body" and not first_content_seen:
            if stripped == "---":
                state = "frontmatter"
                continue
            if stripped:
                first_content_seen = True
            # fall through to body processing below

        if state == "frontmatter":
            if stripped == "---":
                state = "body"
                first_content_seen = True
            # skip every line inside the front-matter block
            continue

        # ── body / code-cell detection ────────────────────────────────────────
        if state == "body":
            if stripped:
                first_content_seen = True

            # MyST-NB cell separator — ignore.
            if stripped == "+++":
                continue

            # Detect the opening of a {code-cell} fence.
            # Handles: ```{code-cell}, ```{code-cell} python, ```{code-cell} ipython3
            m = re.match(r"^(`{3,})\{code-cell\}", stripped)
            if m:
                state = "code_cell"
                fence_marker = m.group(1)
                code_lines = []
                continue

            # Extract the page title from the first level-1 heading.
            if not title_found and stripped.startswith("# ") and not stripped.startswith("## "):
                title = stripped[2:].strip()
                title_found = True

        elif state == "code_cell":
            # The closing fence must be exactly the same backtick sequence,
            # optionally followed by whitespace only.
            if stripped == fence_marker:
                state = "body"
                cell_source = "\n".join(code_lines)
                fqns.update(_fqn_set_from_source(_strip_ipython_magics(cell_source)))
                _lib = getattr(_parse_mystnb, "_lib_index", None)
                if _lib is not None:
                    _, short_idx, qual_idx = _lib
                    fqns.update(_text_match_fqns(cell_source, short_idx, qual_idx))
                code_lines = []
                fence_marker = ""
            else:
                code_lines.append(line)

    # Handle an unclosed fence at EOF (shouldn't happen in valid files).
    if state == "code_cell" and code_lines:
        cell_source = "\n".join(code_lines)
        fqns.update(_fqn_set_from_source(_strip_ipython_magics(cell_source)))
        _lib = getattr(_parse_mystnb, "_lib_index", None)
        if _lib is not None:
            _, short_idx, qual_idx = _lib
            fqns.update(_text_match_fqns(cell_source, short_idx, qual_idx))

    return title, fqns


def _notebook_extensions(config: Any) -> Dict[str, str]:
    """Return a mapping of file extension → parser type for notebook files.

    Detects all file extensions that should be treated as notebooks, based on:

    * ``.ipynb`` — always included (standard Jupyter notebooks).
    * ``nbsphinx_custom_formats`` — maps extension strings to converter
      callables/lists configured by the user, e.g.
      ``{".mystnb": ["jupytext.reads", {"fmt": "mystnb"}]}``.
    * The ``myst_nb`` extension being active — when ``myst_nb`` is loaded it
      processes ``.mystnb`` and ``.md`` files that contain notebook metadata.

    Parameters
    ----------
    config : ~sphinx.config.Config
        The Sphinx config object.

    Returns
    -------
    dict[str, str]
        Mapping of file extension (with leading dot) → parser name.
        Parser name is either ``"ipynb"`` or ``"mystnb"``.
    """
    ext_map: Dict[str, str] = {".ipynb": "ipynb"}

    # nbsphinx_custom_formats: dict mapping extension → converter
    custom_formats: dict = dict(getattr(config, "nbsphinx_custom_formats", {}) or {})
    for ext in custom_formats:
        if not ext.startswith("."):
            ext = f".{ext}"
        # Treat all custom-format extensions as MyST-NB style (text-based).
        ext_map[ext] = "mystnb"

    # myst_nb registers .mystnb and optionally .md.
    extensions: List[str] = list(getattr(config, "extensions", []) or [])
    if "myst_nb" in extensions:
        ext_map.setdefault(".mystnb", "mystnb")

    return ext_map


# ---------------------------------------------------------------------------
# Thumbnail helpers
# ---------------------------------------------------------------------------


def _default_thumb_path(default_thumb: str) -> str:
    """Return the srcdir-relative path for the configured default thumbnail.

    Parameters
    ----------
    default_thumb : str
        Value of ``ansys_gallery_default_thumbnail`` config key.  May be an
        absolute-root URI (``/_static/...``), a bare ``_static/``-prefixed
        path, or a plain filename.

    Returns
    -------
    str
        Path relative to the Sphinx ``srcdir`` root (no leading ``/``).
    """
    if default_thumb:
        # Strip a leading slash so the path is always srcdir-relative
        return default_thumb.lstrip("/")
    # Fall back to a placeholder path; the actual file is copied into
    # _static/ansys-gallery/ by scan_examples() before this is used.
    return "_static/ansys-gallery/pyansys_light_square.png"


def _gallery_thumb_path(
    py_path: Path,
    sphinx_gallery_conf: Optional[dict],
    default_thumb_path: str,
    srcdir: str,
) -> str:
    """Return the srcdir-relative path for a sphinx-gallery example thumbnail.

    Sphinx-gallery writes thumbnails to
    ``<gallery_dir>/Folder/images/thumb/<stem>_thumb.png`` inside ``srcdir``.
    We locate the file and return its srcdir-relative path.  If the file
    does not yet exist (first build) we fall back to *default_thumb_path*.

    Parameters
    ----------
    py_path : ~pathlib.Path
        Absolute path to the source ``.py`` file.
    sphinx_gallery_conf : dict | None
        Value of ``sphinx_gallery_conf`` from the Sphinx config, if present.
    default_thumb_path : str
        Srcdir-relative fallback returned when the thumbnail cannot be found.
    srcdir : str
        Absolute path to the Sphinx source directory.

    Returns
    -------
    str
        Srcdir-relative path to the thumbnail (no leading ``/``).
    """
    if not sphinx_gallery_conf:
        return default_thumb_path

    examples_dirs = sphinx_gallery_conf.get("examples_dirs", [])
    gallery_dirs = sphinx_gallery_conf.get("gallery_dirs", [])
    if isinstance(examples_dirs, str):
        examples_dirs = [examples_dirs]
    if isinstance(gallery_dirs, str):
        gallery_dirs = [gallery_dirs]

    srcdir_path = Path(srcdir).resolve()
    stem = py_path.stem

    for examples_dir, gallery_dir in zip(examples_dirs, gallery_dirs):
        # Resolve examples_dir — may be relative to srcdir (e.g. "../examples")
        ex_dir = Path(examples_dir)
        if not ex_dir.is_absolute():
            ex_dir = (srcdir_path / ex_dir).resolve()

        try:
            rel_in_ex = py_path.parent.relative_to(ex_dir)
        except ValueError:
            continue  # this py file doesn't belong to this examples_dir

        # Resolve gallery_dir — usually srcdir-relative (e.g. "auto_examples")
        gdir = Path(gallery_dir)
        if not gdir.is_absolute():
            gdir = (srcdir_path / gdir).resolve()

        # sphinx-gallery thumbnail: <gallery_dir>/<subfolder>/images/thumb/sphx_glr_<stem>_thumb.png
        thumb_abs = gdir / rel_in_ex / "images" / "thumb" / f"sphx_glr_{stem}_thumb.png"
        if thumb_abs.exists():
            try:
                return str(thumb_abs.relative_to(srcdir_path)).replace(os.sep, "/")
            except ValueError:
                # gallery_dir is outside srcdir — return absolute URI as fallback
                return str(thumb_abs).replace(os.sep, "/")

    return default_thumb_path


def _gallery_output_docname(
    py_file: Path,
    sphinx_gallery_conf: Optional[dict],
    srcdir: str,
) -> Optional[str]:
    """Return the Sphinx docname for the *built* gallery page of a ``.py`` file.

    sphinx-gallery writes its RST output files into the configured
    ``gallery_dirs``, not alongside the source ``.py`` files.  The docname of
    the rendered page is therefore ``<gallery_dirs[i]>/<stem>``, not
    ``<examples_dirs[i]>/<stem>``.

    Parameters
    ----------
    py_file : ~pathlib.Path
        Absolute path to the source ``.py`` file.
    sphinx_gallery_conf : dict | None
        Value of ``sphinx_gallery_conf`` from the Sphinx config.
    srcdir : str
        Absolute path to the Sphinx source directory.

    Returns
    -------
    str | None
        Srcdir-relative docname (no extension, no leading ``/``), or ``None``
        when the mapping cannot be determined.
    """
    if not sphinx_gallery_conf:
        return None

    examples_dirs = sphinx_gallery_conf.get("examples_dirs", [])
    gallery_dirs = sphinx_gallery_conf.get("gallery_dirs", [])
    if isinstance(examples_dirs, str):
        examples_dirs = [examples_dirs]
    if isinstance(gallery_dirs, str):
        gallery_dirs = [gallery_dirs]

    srcdir_path = Path(srcdir).resolve()

    for examples_dir, gallery_dir in zip(examples_dirs, gallery_dirs):
        # Resolve examples_dir (may be srcdir-relative or absolute)
        ex_dir = Path(examples_dir)
        if not ex_dir.is_absolute():
            ex_dir = (srcdir_path / ex_dir).resolve()

        try:
            rel_to_ex = py_file.relative_to(ex_dir)
        except ValueError:
            continue

        # gallery_dir is also srcdir-relative or absolute
        gal_dir = Path(gallery_dir)
        if not gal_dir.is_absolute():
            gal_dir = gallery_dir.rstrip("/")
        else:
            gal_dir = os.path.relpath(str(gal_dir), str(srcdir_path)).replace(os.sep, "/")

        stem = rel_to_ex.with_suffix("").as_posix()
        return f"{str(gal_dir).rstrip('/')}/{stem}"

    return None


def scan_examples(app: Sphinx) -> None:
    """Scan all configured example directories and build the backrefs map.

    This function is connected to the ``builder-inited`` Sphinx event.  It
    populates ``app.env.ansys_gallery_backrefs``, a ``dict`` mapping every
    fully-qualified name to a list of :class:`ExampleInfo` objects representing
    the examples that reference it.

    Parameters
    ----------
    app : ~sphinx.application.Sphinx
        Application instance for rendering the documentation.
    """
    config_dirs: List[str] = list(getattr(app.config, "ansys_gallery_example_dirs", []) or [])
    default_thumb = str(getattr(app.config, "ansys_gallery_default_thumbnail", "") or "")
    json_sources: List[dict] = list(getattr(app.config, "ansys_gallery_example_json", []) or [])
    fqn_prefixes: List[str] = list(getattr(app.config, "ansys_gallery_fqn_prefixes", []) or [])
    library_json_str: str = str(getattr(app.config, "ansys_gallery_library_json", "") or "")

    # ---- Load library JSON for text-match scanning --------------------------
    # When a library JSON is configured, attach the lookup indexes to the
    # parser functions so they can union text-match results with AST results
    # without needing extra arguments propagated everywhere.
    lib_index = None
    if library_json_str:
        lib_json_path = (Path(app.srcdir) / library_json_str).resolve()
        if not lib_json_path.is_file():
            # Also try repo root
            lib_json_path = (Path(app.srcdir).resolve().parent.parent / library_json_str).resolve()
        if lib_json_path.is_file():
            lib_index = _fqns_from_library_json(lib_json_path)
        else:
            logger.warning(
                f"ansys-minigallery: library_json file not found: {library_json_str!r}; "
                "text-match scanning disabled."
            )
    # Attach to parser functions (thread-local-safe for sequential builds;
    # parallel builds each get their own process so this is also safe there).
    _parse_gallery_py._lib_index = lib_index  # type: ignore[attr-defined]
    _parse_notebook._lib_index = lib_index  # type: ignore[attr-defined]
    _parse_mystnb._lib_index = lib_index  # type: ignore[attr-defined]

    if not config_dirs and not json_sources:
        logger.debug(
            "ansys-minigallery: no example directories or JSON sources configured; skipping scan."
        )
        return

    if not hasattr(app.env, "ansys_gallery_backrefs"):
        app.env.ansys_gallery_backrefs = {}  # type: ignore[attr-defined]

    backrefs = app.env.ansys_gallery_backrefs
    thumb_dir = Path(app.outdir) / "_static" / "ansys-gallery" / "thumbs"
    thumb_dir.mkdir(parents=True, exist_ok=True)

    # Copy the ansys favicon into the gallery static directory so it can be
    # used as a srcdir-relative fallback thumbnail.  ansys_favicon is an
    # absolute filesystem path, not a valid srcdir-relative path on its own.
    import shutil as _shutil

    logo_dest = Path(app.outdir) / "_static" / "ansys-gallery" / "pyansys-light-square.png"
    if not logo_dest.exists():
        try:
            _shutil.copy2(pyansys_light_square_logo, logo_dest)
        except OSError:
            pass  # Non-fatal: thumbnail will fall back gracefully

    root_dir = Path(app.srcdir).resolve().parent.parent
    sphinx_gallery_conf: Optional[dict] = getattr(app.config, "sphinx_gallery_conf", None)
    # nbsphinx_thumbnails maps docname → thumbnail path (configured in conf.py)
    nbsphinx_thumbnails: dict = dict(getattr(app.config, "nbsphinx_thumbnails", {}) or {})
    default_path = _default_thumb_path(default_thumb)

    total_files = 0
    json_output: Dict[str, List[str]] = {}

    for dir_str in config_dirs:
        # Resolve relative to repo root first, then srcdir
        dir_path = (root_dir / dir_str).resolve()
        if not dir_path.is_dir():
            dir_path = (Path(app.srcdir) / dir_str).resolve()
        if not dir_path.is_dir():
            logger.warning(
                f"ansys-minigallery: examples directory not found: {dir_str!r}. Skipping."
            )
            continue

        # ---- sphinx-gallery .py files ----------------------------------------
        for py_file in sorted(dir_path.rglob("*.py")):
            if py_file.name.startswith("_") or py_file.name == "conf.py":
                continue

            title, fqns = _parse_gallery_py(py_file)
            filtered_fqns = sorted(_filter_fqns(fqns, fqn_prefixes))
            if filtered_fqns:
                # Use path relative to examples dir to preserve subdirectories
                # (e.g. "00_basic/example_01.py" not just "example_01.py").
                # This ensures base_url + key correctly reconstructs the URL.
                json_key = str(py_file.relative_to(dir_path)).replace(os.sep, "/")
                json_output[json_key] = filtered_fqns

            # The built page lives in gallery_dirs, not alongside the source .py.
            # Use sphinx_gallery_conf to find the correct output docname.
            docname = _gallery_output_docname(py_file, sphinx_gallery_conf, str(app.srcdir))
            if docname is None:
                # Fallback: use the source .py path as the docname
                try:
                    rel = py_file.relative_to(Path(app.srcdir))
                    docname = str(rel.with_suffix("")).replace(os.sep, "/")
                except ValueError:
                    logger.debug(f"ansys-minigallery: cannot determine docname for {py_file}")
                    continue

            thumb_uri = _gallery_thumb_path(
                py_file, sphinx_gallery_conf, default_path, str(app.srcdir)
            )
            info = ExampleInfo(
                title=title,
                doc_path=docname,
                source_type="gallery",
                # thumbnail_uri is intentionally left empty here.
                # sphinx-gallery generates thumbnails during its own builder-inited
                # hook, which runs AFTER ours (autoapi is listed in extensions before
                # sphinx_gallery.gen_gallery).  We resolve it lazily at directive
                # run() time, when the thumbnail file is guaranteed to exist.
                src_file_abs=str(py_file),
                thumbnail_uri="",
            )

            for fqn in _filter_fqns(fqns, fqn_prefixes):
                backrefs.setdefault(fqn, [])
                if not any(e.doc_path == docname for e in backrefs[fqn]):
                    backrefs[fqn].append(info)

            total_files += 1

        # ---- Jupyter notebooks and MyST-NB files ----------------------------
        nb_ext_map: Dict[str, str] = _notebook_extensions(app.config)
        for ext, parser_type in nb_ext_map.items():
            for nb_file in sorted(dir_path.rglob(f"*{ext}")):
                if nb_file.name.startswith(".") or ".ipynb_checkpoints" in str(nb_file):
                    continue

                # Parse according to file type.
                thumb_data: Optional[bytes] = None
                if parser_type == "ipynb":
                    title, fqns, thumb_data = _parse_notebook(nb_file)
                else:
                    title, fqns = _parse_mystnb(nb_file)
                    # MyST-NB files have no embedded image output.
                filtered_fqns = sorted(_filter_fqns(fqns, fqn_prefixes))
                if filtered_fqns:
                    json_key = str(nb_file.relative_to(dir_path)).replace(os.sep, "/")
                    json_output[json_key] = filtered_fqns

                try:
                    rel = nb_file.relative_to(Path(app.srcdir))
                    docname = str(rel.with_suffix("")).replace(os.sep, "/")
                except ValueError:
                    logger.debug(f"ansys-minigallery: cannot make {nb_file} relative to srcdir")
                    continue

                # Thumbnail priority:
                #  1. Embedded image output (ipynb only).
                #  2. nbsphinx_thumbnails mapping.
                #  3. Default fallback.
                if thumb_data is not None:
                    thumb_name = nb_file.stem + ".png"
                    thumb_abs = thumb_dir / thumb_name
                    thumb_abs.write_bytes(thumb_data)
                    thumb_uri = str(thumb_abs.relative_to(Path(app.srcdir))).replace(os.sep, "/")
                else:
                    nb_thumb_configured = nbsphinx_thumbnails.get(docname, "")
                    thumb_uri = (
                        _default_thumb_path(nb_thumb_configured)
                        if nb_thumb_configured
                        else default_path
                    )

                info = ExampleInfo(
                    title=title,
                    doc_path=docname,
                    source_type="notebook",
                    src_file_abs=str(nb_file),
                    thumbnail_uri=thumb_uri,
                )

                for fqn in _filter_fqns(fqns, fqn_prefixes):
                    backrefs.setdefault(fqn, [])
                    if not any(e.doc_path == docname for e in backrefs[fqn]):
                        backrefs[fqn].append(info)

                total_files += 1

    # ---- Always write examples JSON into _static/, named from project name --
    if json_output:
        # Sanitise: lowercase, replace spaces and hyphens with underscores.
        raw_project = str(getattr(app.config, "project", "") or "project")
        safe_name = re.sub(r"[\s\-]+", "_", raw_project).lower()
        output_filename = f"{safe_name}_examples.json"
        json_content = json.dumps(json_output, indent=4)

        static_out_dir = Path(app.outdir) / "_static"
        static_out_dir.mkdir(parents=True, exist_ok=True)
        static_out_path = static_out_dir / output_filename
        try:
            static_out_path.write_text(json_content, encoding="utf-8")
            logger.info(
                f"ansys-minigallery: wrote {len(json_output)} example(s) to {static_out_path}"
            )
        except OSError as exc:
            logger.warning(f"ansys-minigallery: failed to write examples JSON to _static: {exc}")

    # ---- Load pre-computed JSON sources -------------------------------------
    total_files += _load_json_sources(app, backrefs, default_path, root_dir, fqn_prefixes)

    n_objects = len(backrefs)
    n_refs = sum(len(v) for v in backrefs.values())
    logger.info(
        f"ansys-minigallery: scanned {total_files} example file(s); "
        f"indexed {n_refs} reference(s) across {n_objects} API object(s)."
    )


def _filter_fqns(fqns: set, prefixes: List[str]) -> set:
    """Return only the FQNs that match one of *prefixes*.

    If *prefixes* is empty, all FQNs are returned unchanged (no filtering).

    Parameters
    ----------
    fqns : set[str]
        Full set of FQNs from AST scanning.
    prefixes : list[str]
        Package prefixes to keep, e.g. ``["ansys_sphinx_theme",
        "ansys.geometry.core"]``.  A FQN matches if it equals a prefix or
        starts with ``prefix + "."``.

    Returns
    -------
    set[str]
        Filtered subset of *fqns*.
    """
    if not prefixes:
        return fqns
    return {fqn for fqn in fqns if any(fqn == p or fqn.startswith(p + ".") for p in prefixes)}


def _fqns_from_library_json(path: Path) -> Optional[frozenset]:
    """Load the set of known FQNs from a library JSON file.

    The expected format is a JSON list where each entry has a ``"name"`` field
    containing the fully-qualified name of a class, method, function, or
    module.  Names may carry a short type prefix and a signature which are
    stripped automatically::

        [{"name": "F:pkg.mod.func(arg1, arg2)"},
         {"name": "T:pkg.mod.MyClass"},
         {"name": "MOD:pkg.mod"}]

    This function strips the ``X:`` prefix and the ``(...)`` signature to
    produce clean FQNs, then builds two lookup dicts used by
    :func:`_text_match_fqns`:

    * ``short_index`` — last name segment → list of full FQNs
    * ``qualified_index`` — last two segments → list of full FQNs

    Parameters
    ----------
    path : ~pathlib.Path
        Absolute path to the library JSON file.

    Returns
    -------
    tuple[frozenset, dict, dict] | None
        ``(all_fqns, short_index, qualified_index)`` or ``None`` on error.
    """
    try:
        entries = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as exc:
        logger.warning(f"ansys-minigallery: failed to read library JSON {path}: {exc}")
        return None

    if not isinstance(entries, list):
        logger.warning(f"ansys-minigallery: library JSON {path} is not a list; skipping.")
        return None

    all_fqns: set = set()
    short_index: Dict[str, List[str]] = {}
    qualified_index: Dict[str, List[str]] = {}

    for entry in entries:
        # Accept three formats:
        #   1. Plain FQN string:           "ansys.geometry.core.modeler.Modeler"
        #   2. Dict with plain "name":     {"name": "ansys.geometry.core.modeler.Modeler"}
        #   3. Dict with prefixed "name":  {"name": "T:ansys.geometry.core.modeler.Modeler(args)"}
        if isinstance(entry, str):
            raw = entry.strip()
        elif isinstance(entry, dict):
            raw = entry.get("name", "").strip()
        else:
            continue
        if not raw:
            continue
        # Strip optional type prefix ("F:", "T:", "P:", "MOD:", etc.)
        if ":" in raw:
            raw = raw.split(":", 1)[1]
        # Strip optional signature "(args)"
        fqn = raw.split("(")[0].strip()
        if not fqn:
            continue
        all_fqns.add(fqn)
        parts = fqn.split(".")
        # short index: last segment, e.g. "repair_tools"
        short = parts[-1]
        short_index.setdefault(short, []).append(fqn)
        # qualified index: last two segments, e.g. "Modeler.repair_tools"
        if len(parts) >= 2:
            qual = ".".join(parts[-2:])
            qualified_index.setdefault(qual, []).append(fqn)

    logger.info(
        f"ansys-minigallery: loaded {len(all_fqns)} known FQNs from library JSON {path.name}"
    )
    return frozenset(all_fqns), short_index, qualified_index


def _text_match_fqns(
    source: str,
    short_index: Dict[str, List[str]],
    qualified_index: Dict[str, List[str]],
) -> set:
    """Return all library FQNs whose name segments appear in *source*.

    This is a text-match pass that catches API objects that are **never
    explicitly imported** — e.g. objects returned by method calls, objects
    accessed via chained attribute lookups, or objects in cells that were
    skipped by magic stripping.

    The matching is done in two rounds to balance recall vs. noise:

    1. **Qualified match** (``Modeler.repair_tools``) — two-segment name must
       appear as a word boundary.  Highly precise: very unlikely to appear
       accidentally in non-library code.
    2. **Short match** (``repair_tools``) — single segment, used only when the
       short name maps to exactly one FQN (unambiguous).  Multi-FQN short
       names are skipped to avoid false positives (e.g. ``get``, ``show``).

    Parameters
    ----------
    source : str
        Raw source text of an example file or notebook cell.
    short_index : dict
        Mapping of short name → list of full FQNs.
    qualified_index : dict
        Mapping of two-segment qualified name → list of full FQNs.

    Returns
    -------
    set[str]
        Full FQNs that were matched.
    """
    matched: set = set()

    # Round 1: qualified two-segment names (high precision)
    for qual_name, fqns in qualified_index.items():
        if re.search(r"\b" + re.escape(qual_name) + r"\b", source):
            matched.update(fqns)

    # Round 2: unambiguous short names only
    for short_name, fqns in short_index.items():
        if len(fqns) == 1 and re.search(r"\b" + re.escape(short_name) + r"\b", source):
            matched.update(fqns)

    return matched


def _load_json_sources(
    app: Sphinx,
    backrefs: Dict[str, List[ExampleInfo]],
    default_path: str,
    root_dir: Path,
    fqn_prefixes: Optional[List[str]] = None,
) -> int:
    """Populate *backrefs* from pre-computed JSON files.

    Reads every entry in ``ansys_gallery_json_sources`` config.  Each entry
    is a dict that supports the following keys:

    ``file``
        **Required.** Path to the examples JSON file, relative to ``srcdir``.

    ``base_url``
        URL prefix for the external docs site.  The card link is built as
        ``base_url + "/" + path_without_extension + ".html"``.
        Takes priority over ``base_docdir``.

    ``base_docdir``
        Sphinx docname prefix prepended to each key stem when ``base_url`` is
        not set (e.g. ``"examples/gallery-examples"`` → docname
        ``"examples/gallery-examples/00_basic/example_01"``).

    ``fqn_prefixes``
        Per-entry override of the global ``fqn_prefixes`` filter.  Only FQNs
        starting with one of these strings are loaded.  Falls back to the
        global *fqn_prefixes* argument when omitted.

    ``base_examples_dir``
        Optional srcdir-relative path to the actual source files.  When given,
        the extension opens each file to extract the real title and thumbnail.
        Only meaningful for internal (local) JSON sources.

    The JSON format is a mapping of dir-relative file paths to FQN lists::

        {
            "00_basic/example_01.py": ["pkg.MyClass", "pkg.func"],
            "notebooks/demo.ipynb":   ["pkg.Modeler"]
        }

    File extension determines card type: ``.py`` → ``"gallery"``,
    everything else → ``"notebook"``.

    Parameters
    ----------
    app : ~sphinx.application.Sphinx
        Application instance.
    backrefs : dict
        The ``env.ansys_gallery_backrefs`` map to populate.
    default_path : str
        Srcdir-relative fallback thumbnail path.
    root_dir : ~pathlib.Path
        Repository root (two levels above ``srcdir``).
    fqn_prefixes : list[str] | None
        Global package prefixes used to filter FQNs.  ``None`` or empty means
        no filtering.  Per-entry ``fqn_prefixes`` in the JSON config overrides
        this value for that specific source.

    Returns
    -------
    int
        Number of example files loaded from JSON.
    """
    json_sources: List[dict] = list(getattr(app.config, "ansys_gallery_json_sources", []) or [])
    if not json_sources:
        return 0

    total = 0
    for entry in json_sources:
        json_file = entry.get("file", "")
        base_docdir = entry.get("base_docdir", "").strip("/")
        if not json_file:
            logger.warning("ansys-minigallery: examples_json entry missing 'file' key; skipping.")
            continue

        # Resolve path relative to srcdir (conf.py directory)
        json_path = (Path(app.srcdir) / json_file).resolve()
        if not json_path.is_file():
            logger.warning(
                f"ansys-minigallery: examples_json file not found: {json_file!r}; skipping."
            )
            continue

        try:
            data: Dict[str, List[str]] = json.loads(json_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError) as exc:
            logger.warning(f"ansys-minigallery: failed to read {json_file!r}: {exc}")
            continue

        base_url = entry.get("base_url", "").rstrip("/")
        # Optional: directory where the actual source files live, so we can
        # extract real titles and thumbnails.  Resolved relative to srcdir.
        base_examples_dir_str = entry.get("base_examples_dir", "").strip("/")
        base_examples_dir: Optional[Path] = (
            (Path(app.srcdir) / base_examples_dir_str).resolve() if base_examples_dir_str else None
        )
        # Per-entry fqn_prefixes overrides the global filter for this source.
        entry_fqn_prefixes = entry.get("fqn_prefixes", [])
        if isinstance(entry_fqn_prefixes, str):
            entry_fqn_prefixes = [entry_fqn_prefixes]
        effective_fqn_prefixes = entry_fqn_prefixes if entry_fqn_prefixes else (fqn_prefixes or [])
        thumb_dir = Path(app.srcdir) / "_static" / "ansys-gallery" / "thumbs"
        for filename, fqn_list in data.items():
            file_path = Path(filename)
            # Preserve sub-directories: "01/sweep_chain_profile.py" → "01/sweep_chain_profile"
            path_no_ext = file_path.with_suffix("").as_posix()
            stem = file_path.stem
            suffix = file_path.suffix.lower()
            source_type = "gallery" if suffix == ".py" else "notebook"
            title = stem.replace("_", " ").replace("-", " ").title()

            # Build link: external URL takes priority over local docname.
            if base_url:
                doc_path = f"{base_url}/{path_no_ext}.html"
                link_type = "url"
            else:
                doc_path = f"{base_docdir}/{path_no_ext}" if base_docdir else path_no_ext
                link_type = "doc"

            # Filter to only the documented library's FQNs.
            # Per-entry fqn_prefixes takes priority over the global filter.
            filtered = _filter_fqns(set(fqn_list), effective_fqn_prefixes)
            if not filtered:
                continue

            # For internal entries with a base_examples_dir, locate the source
            # file on disk to extract the real title and thumbnail.
            thumbnail_uri = default_path
            src_file_abs = ""
            if not base_url and base_examples_dir is not None:
                candidate = (base_examples_dir / filename).resolve()
                if candidate.is_file():
                    src_file_abs = str(candidate)
                    if suffix == ".ipynb":
                        parsed_title, _, thumb_data = _parse_notebook(candidate)
                        title = parsed_title
                        if thumb_data is not None:
                            thumb_dir.mkdir(parents=True, exist_ok=True)
                            thumb_abs = thumb_dir / (stem + ".png")
                            thumb_abs.write_bytes(thumb_data)
                            thumbnail_uri = str(thumb_abs.relative_to(Path(app.srcdir))).replace(
                                os.sep, "/"
                            )
                    elif suffix == ".py":
                        parsed_title, _ = _parse_gallery_py(candidate)
                        title = parsed_title
                        # Leave thumbnail_uri="" so _resolve_thumbnail picks up
                        # the sphinx-gallery generated thumbnail lazily.
                        thumbnail_uri = ""

            info = ExampleInfo(
                title=title,
                doc_path=doc_path,
                source_type=source_type,
                src_file_abs=src_file_abs,
                thumbnail_uri=thumbnail_uri,
                link_type=link_type,
            )

            for fqn in filtered:
                backrefs.setdefault(fqn, [])
                if not any(e.doc_path == doc_path for e in backrefs[fqn]):
                    backrefs[fqn].append(info)

            total += 1

    if total:
        logger.info(f"ansys-minigallery: loaded {total} example(s) from JSON sources.")
    return total


# ---------------------------------------------------------------------------
# env-merge-info hook (parallel read safety)
# ---------------------------------------------------------------------------


def env_merge_info(
    app: Sphinx,
    env: Any,
    docnames: List[str],
    other: Any,
) -> None:
    """Merge backrefs from a parallel-read sub-environment.

    Parameters
    ----------
    app : ~sphinx.application.Sphinx
        Application instance.
    env : ~sphinx.environment.BuildEnvironment
        The main environment being built.
    docnames : list[str]
        Docnames processed by the sub-environment.
    other : ~sphinx.environment.BuildEnvironment
        The sub-environment whose data should be merged.
    """
    if not hasattr(other, "ansys_gallery_backrefs"):
        return
    if not hasattr(env, "ansys_gallery_backrefs"):
        env.ansys_gallery_backrefs = {}
    for fqn, examples in other.ansys_gallery_backrefs.items():
        env.ansys_gallery_backrefs.setdefault(fqn, [])
        existing = {e.doc_path for e in env.ansys_gallery_backrefs[fqn]}
        for ex in examples:
            if ex.doc_path not in existing:
                env.ansys_gallery_backrefs[fqn].append(ex)
                existing.add(ex.doc_path)


# ---------------------------------------------------------------------------
# Directive
# ---------------------------------------------------------------------------


def _srcdir_to_docrel(srcdir_path: str, docname: str) -> str:
    """Convert a srcdir-relative path to one relative to *docname*'s directory.

    Sphinx resolves ``.. image::`` (and ``:img-top:``) relative to the
    **source file** of the current document, not the site root.  Autoapi
    pages can be several directories deep, so we must account for depth.

    Parameters
    ----------
    srcdir_path : str
        Path relative to the Sphinx ``srcdir`` root (no leading ``/``).
        E.g. ``_static/pyansys_light_square.png`` or
        ``examples/gallery-examples/images/thumb/foo_thumb.png``.
    docname : str
        Current Sphinx docname, e.g.
        ``examples/api/examples/sample_func/func``.

    Returns
    -------
    str
        Relative path from the docname's directory to *srcdir_path*,
        using forward slashes.
    """
    from pathlib import PurePosixPath

    doc_dir = str(PurePosixPath(docname).parent)
    if doc_dir == ".":
        # top-level docname — no directory depth to escape
        return srcdir_path
    rel = os.path.relpath(srcdir_path, doc_dir)
    return rel.replace(os.sep, "/")


def _resolve_thumbnail(ex: "ExampleInfo", srcdir: str, default_path: str, config: Any) -> str:
    """Return the srcdir-relative thumbnail path for *ex*, resolving it freshly.

    For sphinx-gallery examples this is called at directive ``run()`` time
    rather than at ``builder-inited``, because sphinx-gallery writes its
    thumbnail PNGs during its own ``builder-inited`` hook which — due to
    extension load order — fires *after* minigallery's scan hook.

    For Jupyter notebooks, if no embedded output was stored during scanning
    we consult ``nbsphinx_thumbnails`` from the Sphinx config before falling
    back to the project default.

    Parameters
    ----------
    ex : ExampleInfo
        The example whose thumbnail to resolve.
    srcdir : str
        Absolute path to the Sphinx source directory.
    default_path : str
        Srcdir-relative fallback (e.g. ``_static/pyansys_light_square.png``).
    config : ~sphinx.config.Config
        The live Sphinx config object (``env.config``).

    Returns
    -------
    str
        Srcdir-relative path to the thumbnail image (no leading ``/``).
    """
    if ex.source_type == "gallery":
        # Re-resolve from sphinx_gallery_conf every time so we always pick up
        # the generated thumbnail regardless of when scan_examples ran.
        # Guard: JSON-sourced entries without base_examples_dir have no local file.
        if not ex.src_file_abs:
            return default_path
        sgconf: Optional[dict] = getattr(config, "sphinx_gallery_conf", None)
        return _gallery_thumb_path(Path(ex.src_file_abs), sgconf, default_path, srcdir)

    # --- notebook ---
    # Use the thumbnail that was already extracted from embedded outputs (if any)
    if ex.thumbnail_uri:
        return ex.thumbnail_uri

    # Fall back to nbsphinx_thumbnails config
    nb_thumbs: dict = dict(getattr(config, "nbsphinx_thumbnails", {}) or {})
    configured = nb_thumbs.get(ex.doc_path, "")
    if configured:
        return _default_thumb_path(configured)

    return default_path


class AnsysMinigalleryDirective(Directive):
    """Render a minigallery of examples that reference an API object.

    The directive accepts one required argument: the fully-qualified name of
    the Python object to look up in the backreferences map.

    .. code-block:: rst

        .. ansys-minigallery:: ansys_sphinx_theme.examples.samples.ExampleClass
           :heading: My custom heading

    Options
    -------
    heading : str
        Custom heading text.  Defaults to ``'Examples using "<name>"'`` where
        ``<name>`` is the last segment of the FQN argument.
    no-heading : flag
        Suppress the heading entirely.

    The directive resolves fuzzy matches: if the FQN provided matches *any*
    indexed key as a suffix or prefix, those examples are included.  This
    means that ``ExampleClass`` and
    ``ansys_sphinx_theme.examples.samples.ExampleClass`` both resolve to the
    same set of examples.
    """

    required_arguments = 1
    optional_arguments = 0
    option_spec = {
        "heading": directives.unchanged,
        "no-heading": directives.flag,
    }
    has_content = False

    def run(self) -> List[nodes.Node]:
        """Execute the directive and return docutils nodes."""
        env = self.state.document.settings.env
        fqn = self.arguments[0].strip()

        # Skip packages and subpackages (__init__.py level) — the minigallery
        # is only relevant on module, class, and function pages.
        # # TODO: to be discussed — should we allow package-level galleries? # noqa: TD003
        # all_objects = getattr(env, "autoapi_all_objects", {})
        # if fqn in all_objects:
        #     if getattr(all_objects[fqn], "type", "") == "package":
        #         return []

        backrefs: Dict[str, List[ExampleInfo]] = getattr(env, "ansys_gallery_backrefs", {})

        # Fuzzy FQN matching: allow both short names and fully qualified names.
        # Also match child members (e.g. key="Mechanical.name" when fqn="Mechanical"),
        # so class/module pages show examples that reference any of their members.
        examples: List[ExampleInfo] = []
        seen_paths: set = set()
        for key, infos in backrefs.items():
            matched = (
                key == fqn
                or key.endswith(f".{fqn}")
                or fqn.endswith(f".{key}")
                or fqn == key.split(".")[-1]
                or key.startswith(f"{fqn}.")
            )
            if matched:
                for ex in infos:
                    if ex.doc_path not in seen_paths:
                        examples.append(ex)
                        seen_paths.add(ex.doc_path)

        if not examples:
            # Return silently — no gallery section if no examples exist
            return []

        result_nodes: List[nodes.Node] = []

        short_name = fqn.split(".")[-1]
        custom_heading = self.options.get("heading", "")

        section_id = "ansys-minigallery-" + fqn.replace(".", "-").lower()
        section = nodes.section(ids=[section_id])
        section["classes"].append("ansys-minigallery")

        if "no-heading" not in self.options:
            if custom_heading:
                title_node = nodes.title(text=custom_heading)
            else:
                title_node = nodes.title()
                title_node += nodes.Text("Examples using ")
                fn_span = nodes.inline()
                fn_span["classes"].append("ansys-minigallery-fn")
                fn_span += nodes.Text(short_name)
                title_node += fn_span
            section += title_node

        # --- Build a sphinx-design grid via nested RST parsing ---
        rst_lines: List[str] = []
        rst_lines.append(".. grid:: 4 5 6 6")
        rst_lines.append("   :gutter: 2")
        rst_lines.append("   :class-container: ansys-minigallery-grid")
        rst_lines.append("")

        for ex in examples:
            # Resolve thumbnail now (directive run() time), not at scan time.
            # sphinx-gallery thumbnails are only on disk after sphinx-gallery's
            # own builder-inited hook, which fires after our scan_examples.
            default_path = _default_thumb_path(
                str(getattr(env.config, "ansys_gallery_default_thumbnail", "") or "")
            )
            thumb_srcrel = _resolve_thumbnail(ex, env.srcdir, default_path, env.config)
            # Convert srcdir-relative path to docname-relative for Sphinx image resolution
            img_rel = _srcdir_to_docrel(thumb_srcrel, env.docname)
            rst_lines.append("   .. grid-item-card::")
            rst_lines.append(f"      :img-top: {img_rel}")
            if ex.link_type == "url":
                rst_lines.append(f"      :link: {ex.doc_path}")
                rst_lines.append("      :link-type: url")
            else:
                rst_lines.append(f"      :link: /{ex.doc_path}")
                rst_lines.append("      :link-type: doc")
            rst_lines.append("      :class-card: ansys-minigallery-card")
            rst_lines.append("      :class-img-top: ansys-minigallery-thumb")
            rst_lines.append("      :shadow: sm")
            rst_lines.append("")
            rst_lines.append(f"      {ex.title}")
            rst_lines.append("")

        # Parse RST lines into docutils nodes
        vl = ViewList()
        source = env.docname
        for i, line in enumerate(rst_lines):
            vl.append(line, source, i)

        container = nodes.container()
        container["classes"].append("ansys-minigallery-grid-wrap")
        self.state.nested_parse(vl, self.content_offset, container)
        section += container
        result_nodes.append(section)

        return result_nodes


# ---------------------------------------------------------------------------
# Extension setup
# ---------------------------------------------------------------------------


def _inject_function_minigallery(app: Sphinx, docname: str, source: List[str]) -> None:
    """Append ``.. ansys-minigallery::`` to autoapi function own-pages.

    Instead of a custom Jinja template (which overwrites autoapi's built-in
    function template and breaks pydata-sphinx-theme's ``'fullname'`` HTML
    page-context lookup), this ``source-read`` hook appends the directive text
    directly to the raw RST that Sphinx has just read from disk.  By the time
    any source file is read, ``scan_examples`` (``builder-inited``) has already
    populated ``env.ansys_gallery_backrefs``, so the directive's ``run()``
    method will resolve correctly.

    Parameters
    ----------
    app : ~sphinx.application.Sphinx
        Application instance.
    docname : str
        Sphinx docname being read (e.g. ``api/mypackage/MyClass``).
    source : list[str]
        One-element mutable list containing the raw RST source text.
    """
    autoapi_root: str = str(getattr(app.config, "autoapi_root", "api") or "api").rstrip("/")
    if not docname.startswith(autoapi_root + "/"):
        return

    content = source[0]

    # Detect function own-pages: they contain ``.. py:function::`` but neither
    # ``.. py:class::`` nor ``.. py:module::`` (those are handled in the Jinja
    # templates for class.rst / module.rst).
    if ".. py:function::" not in content:
        return
    if ".. py:class::" in content or ".. py:module::" in content:
        return

    # Extract the fully-qualified name from the directive line, e.g.:
    #   .. py:function:: ansys.module.my_func(args) -> RetType
    match = re.search(r"\.\. py:function:: ([A-Za-z_][A-Za-z0-9_.]*)", content)
    if not match:
        return

    fqn = match.group(1)
    source[0] = content.rstrip() + f"\n\n.. ansys-minigallery:: {fqn}\n"


def setup(app: Sphinx) -> Dict[str, Any]:
    """Register the minigallery extension with Sphinx.

    Parameters
    ----------
    app : ~sphinx.application.Sphinx
        Application instance for rendering the documentation.

    Returns
    -------
    dict[str, Any]
        Extension metadata.
    """
    # Config values — populated by ansys_sphinx_theme.extension.autoapi from
    # html_theme_options["ansys_sphinx_theme_autoapi"]["examples_dirs"]
    app.add_config_value("ansys_gallery_example_dirs", [], "env")
    app.add_config_value("ansys_gallery_default_thumbnail", "", "env")
    app.add_config_value("ansys_gallery_example_json", [], "env")
    app.add_config_value("ansys_gallery_fqn_prefixes", [], "env")
    app.add_config_value("ansys_gallery_library_json", "", "env")

    app.add_directive("ansys-minigallery", AnsysMinigalleryDirective)
    app.connect("builder-inited", scan_examples)
    app.connect("source-read", _inject_function_minigallery)
    app.connect("env-merge-info", env_merge_info)

    return {
        "version": __version__,
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }
