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
            "examples_dirs": [
                "doc/source/examples/sphinx-gallery",
                "doc/source/examples/nbsphinx",
            ],
            # Optional: fallback thumbnail (relative to srcdir or absolute).
            "gallery_default_thumbnail": "_static/pyansys_light_square.png",
        }
    }

The extension also reads two Sphinx config values directly (set automatically
by ``ansys_sphinx_theme.extension.autoapi``):

* ``ansys_gallery_dirs`` — list of example directory paths
* ``ansys_gallery_default_thumbnail`` — fallback thumbnail path

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
from typing import Any, Dict, List, Optional

from docutils import nodes
from docutils.parsers.rst import Directive, directives
from docutils.statemachine import ViewList
from sphinx.application import Sphinx
from sphinx.util import logging as sphinx_logging

from ansys_sphinx_theme import __version__

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
    thumbnail_uri : str
        Absolute-root-relative URI for the thumbnail image
        (e.g. ``/_static/ansys-gallery/thumbs/my-notebook.png``).
    source_type : str
        Either ``"gallery"`` (sphinx-gallery ``.py``) or ``"notebook"``
        (Jupyter ``.ipynb``).
    """

    title: str
    doc_path: str
    thumbnail_uri: str
    source_type: str


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

    Parameters
    ----------
    source_code : str
        Python source code to analyse.

    Returns
    -------
    set[str]
        Every fully-qualified name encountered (imports + usages).
    """
    try:
        tree = ast.parse(source_code)
    except SyntaxError:
        return set()

    # Pass 1 — build alias map: local_name → fqn
    alias_map: Dict[str, str] = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                local = alias.asname if alias.asname else alias.name
                alias_map[local] = alias.name
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ""
            for alias in node.names:
                local = alias.asname if alias.asname else alias.name
                fqn = f"{module}.{alias.name}" if module else alias.name
                alias_map[local] = fqn

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

    return refs


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
        pass

    return title, _fqn_set_from_source(source)


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
            fqns.update(_fqn_set_from_source(source))

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
                                pass
                            break
                    if thumbnail_data is not None:
                        break

    return title, fqns, thumbnail_data


# ---------------------------------------------------------------------------
# Thumbnail helpers
# ---------------------------------------------------------------------------


def _default_thumb_uri(default_thumb: str) -> str:
    """Return the site-root-relative URI for the configured default thumbnail.

    Parameters
    ----------
    default_thumb : str
        Value of ``ansys_gallery_default_thumbnail`` config key.

    Returns
    -------
    str
        An absolute-root-relative URI string.
    """
    if default_thumb:
        if default_thumb.startswith(("/", "http://", "https://")):
            return default_thumb
        # Avoid doubling the _static/ prefix when the caller already includes it
        if default_thumb.startswith("_static/"):
            return f"/{default_thumb}"
        return f"/_static/{default_thumb}"
    # PyAnsys light square is always available via the theme
    return "/_static/pyansys_light_square.png"


def _gallery_thumb_uri(
    py_path: Path, sphinx_gallery_conf: Optional[dict], default_thumb_uri: str
) -> str:
    """Find the sphinx-gallery thumbnail for a ``.py`` example.

    Sphinx-gallery generates thumbnails at
    ``<gallery_dir>/images/thumb/<stem>_thumb.png``.  We check every configured
    ``gallery_dirs`` entry to locate the file.  If it does not yet exist (first
    build) we fall back to *default_thumb_uri*.

    Parameters
    ----------
    py_path : ~pathlib.Path
        Absolute path to the source ``.py`` file.
    sphinx_gallery_conf : dict | None
        Value of ``sphinx_gallery_conf`` from the Sphinx config, if present.
    default_thumb_uri : str
        Fallback thumbnail URI returned when the file cannot be found.

    Returns
    -------
    str
        Site-root-relative URI for the thumbnail.
    """
    if not sphinx_gallery_conf:
        return default_thumb_uri

    gallery_dirs = sphinx_gallery_conf.get("gallery_dirs", [])
    if isinstance(gallery_dirs, str):
        gallery_dirs = [gallery_dirs]

    stem = py_path.stem
    for gallery_dir in gallery_dirs:
        thumb_candidate = Path(gallery_dir) / "images" / "thumb" / f"{stem}_thumb.png"
        if thumb_candidate.exists():
            # Normalise to a /_static-relative path won't work here because
            # the gallery_dir is inside srcdir and becomes a docname-relative
            # path.  Use the Sphinx _images convention instead.
            return f"/_images/{stem}_thumb.png"
    return default_thumb_uri


# ---------------------------------------------------------------------------
# builder-inited hook
# ---------------------------------------------------------------------------


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
    config_dirs: List[str] = list(getattr(app.config, "ansys_gallery_dirs", []) or [])
    default_thumb = str(getattr(app.config, "ansys_gallery_default_thumbnail", "") or "")

    if not config_dirs:
        logger.debug("ansys-minigallery: no example directories configured; skipping scan.")
        return

    if not hasattr(app.env, "ansys_gallery_backrefs"):
        app.env.ansys_gallery_backrefs = {}  # type: ignore[attr-defined]

    backrefs = app.env.ansys_gallery_backrefs
    thumb_dir = Path(app.srcdir) / "_static" / "ansys-gallery" / "thumbs"
    thumb_dir.mkdir(parents=True, exist_ok=True)

    # Repository root: assume docs live two levels below it (e.g. doc/source/).
    root_dir = Path(app.srcdir).resolve().parent.parent
    sphinx_gallery_conf: Optional[dict] = getattr(app.config, "sphinx_gallery_conf", None)
    default_uri = _default_thumb_uri(default_thumb)

    total_files = 0

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

            # Build docname relative to srcdir
            try:
                rel = py_file.relative_to(Path(app.srcdir))
                docname = str(rel.with_suffix("")).replace(os.sep, "/")
            except ValueError:
                logger.debug(f"ansys-minigallery: cannot make {py_file} relative to srcdir")
                continue

            thumb_uri = _gallery_thumb_uri(py_file, sphinx_gallery_conf, default_uri)
            info = ExampleInfo(
                title=title,
                doc_path=docname,
                thumbnail_uri=thumb_uri,
                source_type="gallery",
            )

            for fqn in fqns:
                backrefs.setdefault(fqn, [])
                if not any(e.doc_path == docname for e in backrefs[fqn]):
                    backrefs[fqn].append(info)

            total_files += 1

        # ---- Jupyter notebooks -----------------------------------------------
        for nb_file in sorted(dir_path.rglob("*.ipynb")):
            if nb_file.name.startswith(".") or ".ipynb_checkpoints" in str(nb_file):
                continue

            title, fqns, thumb_data = _parse_notebook(nb_file)

            try:
                rel = nb_file.relative_to(Path(app.srcdir))
                docname = str(rel.with_suffix("")).replace(os.sep, "/")
            except ValueError:
                logger.debug(f"ansys-minigallery: cannot make {nb_file} relative to srcdir")
                continue

            # Save extracted thumbnail so Sphinx picks it up as a static file
            if thumb_data is not None:
                thumb_name = nb_file.stem + ".png"
                thumb_abs = thumb_dir / thumb_name
                thumb_abs.write_bytes(thumb_data)
                thumb_uri = f"/_static/ansys-gallery/thumbs/{thumb_name}"
            else:
                thumb_uri = default_uri

            info = ExampleInfo(
                title=title,
                doc_path=docname,
                thumbnail_uri=thumb_uri,
                source_type="notebook",
            )

            for fqn in fqns:
                backrefs.setdefault(fqn, [])
                if not any(e.doc_path == docname for e in backrefs[fqn]):
                    backrefs[fqn].append(info)

            total_files += 1

    n_objects = len(backrefs)
    n_refs = sum(len(v) for v in backrefs.values())
    logger.info(
        f"ansys-minigallery: scanned {total_files} example file(s); "
        f"indexed {n_refs} reference(s) across {n_objects} API object(s)."
    )


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


class AnsysMinigalleryDirective(Directive):
    """Render a minigallery of examples that reference an API object.

    The directive accepts one required argument: the fully-qualified name of
    the Python object to look up in the backreferences map.

    .. code-block:: rst

        .. ansys-minigallery:: ansys_sphinx_theme.examples.samples.ExampleClass
           :heading: Gallery examples

    Options
    -------
    heading : str
        Custom heading text.  Defaults to ``"Gallery examples"``.
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
        backrefs: Dict[str, List[ExampleInfo]] = getattr(env, "ansys_gallery_backrefs", {})

        # Fuzzy FQN matching: allow both short names and fully qualified names
        examples: List[ExampleInfo] = []
        seen_paths: set = set()
        for key, infos in backrefs.items():
            matched = (
                key == fqn
                or key.endswith(f".{fqn}")
                or fqn.endswith(f".{key}")
                or fqn == key.split(".")[-1]
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

        # --- Heading (rubric) ---
        if "no-heading" not in self.options:
            heading_text = self.options.get("heading", "Gallery examples")
            rubric = nodes.rubric(text=heading_text)
            rubric["classes"].append("ansys-minigallery-heading")
            result_nodes.append(rubric)

        # --- Build a sphinx-design grid via nested RST parsing ---
        rst_lines: List[str] = []
        rst_lines.append(".. grid:: 1 2 3 3")
        rst_lines.append("   :gutter: 2")
        rst_lines.append("   :class-container: ansys-minigallery-grid")
        rst_lines.append("")

        for ex in examples:
            rst_lines.append("   .. grid-item-card::")
            rst_lines.append(f"      :img-top: {ex.thumbnail_uri}")
            rst_lines.append(f"      :link: /{ex.doc_path}")
            rst_lines.append("      :link-type: url")
            rst_lines.append("      :class-card: ansys-minigallery-card")
            rst_lines.append("      :class-img-top: ansys-minigallery-thumb")
            rst_lines.append("")
            rst_lines.append(f"      {ex.title}")
            rst_lines.append("")
            badge_class = "badge-primary" if ex.source_type == "gallery" else "badge-secondary"
            badge_label = "sphinx-gallery" if ex.source_type == "gallery" else "notebook"
            # Each string in rst_lines is a single ViewList line — embedded \n breaks parsing.
            # Split the raw directive into separate lines so the content block is recognised.
            rst_lines.append("      .. raw:: html")
            rst_lines.append("")
            rst_lines.append(
                f'         <span class="badge {badge_class} ansys-minigallery-badge">'
                f"{badge_label}</span>"
            )
            rst_lines.append("")

        # Parse RST lines into docutils nodes
        vl = ViewList()
        source = env.docname
        for i, line in enumerate(rst_lines):
            vl.append(line, source, i)

        container = nodes.container()
        container["classes"].append("ansys-minigallery")
        self.state.nested_parse(vl, self.content_offset, container)
        result_nodes.append(container)

        return result_nodes


# ---------------------------------------------------------------------------
# Extension setup
# ---------------------------------------------------------------------------


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
    app.add_config_value("ansys_gallery_dirs", [], "env")
    app.add_config_value("ansys_gallery_default_thumbnail", "", "env")

    app.add_directive("ansys-minigallery", AnsysMinigalleryDirective)
    app.connect("builder-inited", scan_examples)
    app.connect("env-merge-info", env_merge_info)

    return {
        "version": __version__,
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }
