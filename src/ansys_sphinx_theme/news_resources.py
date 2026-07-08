# Copyright (C) 2021 - 2026 Synopsys, Inc. and ANSYS, Inc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Module to configure the News & Resources section.

This module provides a custom RST directive (``.. news-item::``) to define
individual news and resource entries, and a table directive
(``.. news-resources-table::``) that renders all collected entries as a
filtered card list in the documentation page.

Example usage in an RST file::

    .. news-item::
        :type: Video
        :title: PyAnsys 2025 R1 walkthrough
        :author: PyAnsys Team
        :date: 2025-01-15
        :link: https://example.com/video

        Full support for the new solver API and improved mesh handling.

    .. news-item::
        :type: Blog
        :title: Getting Started with PyMechanical
        :author: Jane Doe

        Step-by-step guide for new users.

    .. news-resources-table::

To wire it into the sidebar configure ``html_theme_options`` in ``conf.py``::

    html_theme_options = {
        "news_resources": {
            "pages": ["index"],       # pages that show the sidebar widget
            "link": "news_resources", # pagename (without .rst) of the table page
            "title": "News & Resources",  # optional, sidebar widget title
        }
    }
"""

import html as _html  # noqa: F401 (used in _e helper below)
from typing import List, Optional
import uuid as _uuid

from docutils import nodes
from docutils.parsers.rst import Directive, directives
from sphinx.application import Sphinx
from sphinx.util import logging

logger = logging.getLogger(__name__)


class NewsResourcesTableNode(nodes.General, nodes.Element):
    """Placeholder node replaced by the real table during ``doctree-resolved``."""


class NewsItemDirective(Directive):
    """RST directive to define a single news or resource entry.

    Options
    -------
    type : str
        Category/type label (e.g., "Release", "Tutorial", "Article").
    title : str
        Short title for the entry.
    author : str
        Author name(s).
    date : str, optional
        Publication date (free-form string, e.g., ``2025-01-15``).

    Body
    ----
    The directive body is the description of the entry.
    """

    required_arguments = 0
    optional_arguments = 0
    final_argument_whitespace = False
    has_content = True
    option_spec = {
        "type": directives.unchanged_required,
        "title": directives.unchanged_required,
        "author": directives.unchanged_required,
        "date": directives.unchanged,
        "link": directives.unchanged,
    }

    def run(self) -> list:
        """Parse the directive and store the entry on ``env.news_resources``."""
        env = self.state.document.settings.env

        if not hasattr(env, "news_resources"):
            env.news_resources = []

        description = "\n".join(self.content)

        entry = {
            "type": self.options["type"],
            "title": self.options["title"],
            "author": self.options["author"],
            "date": self.options.get("date", ""),
            "link": self.options.get("link", ""),
            "description": description,
            "docname": env.docname,
        }
        env.news_resources.append(entry)

        # Produce no visible output — all rendering happens in the table directive.
        return []


class NewsResourcesTableDirective(Directive):
    """RST directive that inserts the collected news entries as a table.

    Place this directive once on the page where the table should appear::

        .. news-resources-table::
    """

    required_arguments = 0
    optional_arguments = 0
    has_content = False

    def run(self) -> list:
        """Insert a placeholder node that will be resolved later."""
        node = NewsResourcesTableNode()
        node.document = self.state.document
        self.state.nested_parse(self.content, self.content_offset, node)
        return [node]


def purge_news_resources(app: Sphinx, env, docname: str) -> None:
    """Remove stale news entries for *docname* before the document is re-read.

    Connected to the ``env-purge-doc`` Sphinx event so that incremental builds
    do not accumulate duplicate entries.
    """
    if not hasattr(env, "news_resources"):
        return
    env.news_resources = [e for e in env.news_resources if e["docname"] != docname]


def merge_news_resources(app: Sphinx, env, docnames, other) -> None:
    """Merge news entries collected by parallel-read worker envs into the main env.

    Connected to the ``env-merge-info`` Sphinx event so that entries defined on
    pages read in worker processes are not lost when the envs are merged back.
    """
    if not hasattr(other, "news_resources"):
        return
    if not hasattr(env, "news_resources"):
        env.news_resources = []
    # Avoid duplicates in case of re-merge
    existing = {(e["docname"], e["title"]) for e in env.news_resources}
    for entry in other.news_resources:
        if (entry["docname"], entry["title"]) not in existing:
            env.news_resources.append(entry)


def resolve_news_resources_table(app: Sphinx, doctree: nodes.document, docname: str) -> None:
    """Replace ``news_resources_table_node`` placeholders with a real table.

    Connected to the ``doctree-resolved`` Sphinx event.  Only entries whose
    ``docname`` matches the current document are included, so multiple pages
    can each have their own independent card list.

    Parameters
    ----------
    app : sphinx.application.Sphinx
        Application instance for rendering the documentation.
    doctree : docutils.nodes.document
        The resolved document tree.
    docname : str
        Name of the document being resolved.
    """
    placeholder_list = list(
        doctree.traverse(lambda n: n.__class__.__name__ == "NewsResourcesTableNode")
    )

    # Collect all entries regardless of which document defined them
    entries: list = getattr(app.env, "news_resources", [])

    if not placeholder_list:
        # Auto-inject the table when the page has news-item directives but no
        # explicit news-resources-table directive.
        if any(e["docname"] == docname for e in entries):
            doctree.append(_build_table(entries))
        return

    for placeholder in placeholder_list:
        raw_node = _build_table(entries)
        placeholder.replace_self(raw_node)


# ---------------------------------------------------------------------------
# HTML helpers
# ---------------------------------------------------------------------------

import html as _html_mod  # noqa: E402 (needed after node definitions)


def _e(text: str) -> str:
    """HTML-escape a string for safe inline insertion."""
    return _html_mod.escape(str(text), quote=True)


# Badge CSS modifier per type (case-insensitive); unknown types get 'other'.
_BADGE_TYPE_MAP = {
    "video": "video",
    "blog": "blog",
    "event": "event",
    "news": "news",
}


def _badge_cls(entry_type: str) -> str:
    return _BADGE_TYPE_MAP.get(entry_type.lower(), "other")


def _build_table(entries: list) -> nodes.raw:
    """Build a raw HTML card list with type/author filter buttons.

    Parameters
    ----------
    entries : list[dict]
        List of news/resource entry dicts.

    Returns
    -------
    nodes.raw
        Raw HTML node ready for insertion into the document.
    """
    if not entries:
        html = '<p class="nr-empty">No news or resource entries have been defined.</p>'
        return nodes.raw("", html, format="html")

    # Collect unique types (deduplicated case-insensitively) and authors.
    # seen_types: lowercase key -> display label (title-case of first occurrence)
    seen_types: dict = {}
    seen_authors: list = []
    for e in entries:
        key = e["type"].lower()
        if key not in seen_types:
            seen_types[key] = e["type"].title()
        if e["author"] not in seen_authors:
            seen_authors.append(e["author"])

    parts: list = []
    wrapper_id = "nr-" + _uuid.uuid4().hex[:8]
    parts.append(f'<div class="nr-wrapper" id="{wrapper_id}">')

    # --- Filter bar ---
    parts.append('<div class="nr-filters" aria-label="Filter news and resources">')

    def _dropdown(filter_type: str, label: str, options) -> None:
        parts.append(f'<div class="nr-dropdown" data-filter-type="{_e(filter_type)}">')
        parts.append(
            f'<button class="nr-dropdown-toggle" type="button" '
            f'aria-haspopup="true" aria-expanded="false">'
            f'<span class="nr-dropdown-label">{_e(label)}</span>'
            f'<span class="nr-dropdown-chevron" aria-hidden="true"></span>'
            f"</button>"
        )
        parts.append(
            '<div class="nr-dropdown-menu" hidden role="listbox" aria-multiselectable="true">'
        )
        parts.append(
            f'<label class="nr-dropdown-item">'
            f'<input type="checkbox" value="__all__" checked> {_e(label)}'
            f"</label>"
        )
        # options is dict {value: display} for types, list for authors
        items = options.items() if isinstance(options, dict) else [(o, o) for o in options]
        for val, display in items:
            parts.append(
                f'<label class="nr-dropdown-item">'
                f'<input type="checkbox" value="{_e(val)}"> {_e(display)}'
                f"</label>"
            )
        parts.append("</div>")  # .nr-dropdown-menu
        parts.append("</div>")  # .nr-dropdown

    _dropdown("type", "All Types", seen_types)
    _dropdown("author", "All Authors", seen_authors)

    parts.append("</div>")  # .nr-filters

    # --- Card list ---
    parts.append('<div class="nr-table">')

    for entry in entries:
        etype = entry["type"]
        bc = _badge_cls(etype)
        title = entry["title"]
        link = entry.get("link", "")
        description = entry.get("description", "")
        author = entry["author"]
        date = entry.get("date", "")

        parts.append(
            f'<div class="nr-row" data-type="{_e(etype.lower())}" data-author="{_e(author)}">'
        )

        # Type badge
        parts.append(f'<span class="nr-badge nr-badge--{_e(bc)}">{_e(etype)}</span>')

        # Content: title (linked if :link: provided) + description
        parts.append('<div class="nr-content">')
        if link:
            parts.append(
                f'<a href="{_e(link)}" class="nr-title"'
                f' target="_blank" rel="noopener noreferrer">{_e(title)}</a>'
            )
        else:
            parts.append(f'<span class="nr-title">{_e(title)}</span>')
        if description.strip():
            parts.append(f'<p class="nr-desc">{_e(description)}</p>')
        parts.append("</div>")  # .nr-content

        # Meta: author + optional date
        parts.append('<div class="nr-meta">')
        parts.append(f'<span class="nr-author">{_e(author)}</span>')
        if date:
            parts.append(f'<span class="nr-date">{_e(date)}</span>')
        parts.append("</div>")  # .nr-meta

        parts.append("</div>")  # .nr-row

    parts.append("</div>")  # .nr-table
    parts.append('<div class="nr-pagination" aria-label="Pagination"></div>')

    # Inline filter + dropdown + pagination script — scoped by unique wrapper ID
    parts.append(f"""
<script>
(function () {{
  var PAGE_SIZE = 10;
  var currentPage = 1;
  var scope = document.getElementById('{wrapper_id}');
  if (!scope) return;

  // ── Filter helpers ───────────────────────────────────
  function getSelected(dropdown) {{
    return Array.from(dropdown.querySelectorAll('input[type=checkbox]:checked'))
      .map(function (cb) {{ return cb.value; }})
      .filter(function (v) {{ return v !== '__all__'; }});
  }}

  function getMatchingRows() {{
    var typeDD   = scope.querySelector('.nr-dropdown[data-filter-type="type"]');
    var authorDD = scope.querySelector('.nr-dropdown[data-filter-type="author"]');
    var selTypes   = typeDD   ? getSelected(typeDD)   : [];
    var selAuthors = authorDD ? getSelected(authorDD) : [];
    return Array.from(scope.querySelectorAll('.nr-row')).filter(function (row) {{
      var typeOk = selTypes.length === 0
        || selTypes.indexOf(row.dataset.type) !== -1;
      var authorOk = selAuthors.length === 0
        || selAuthors.indexOf(row.dataset.author) !== -1;
      return typeOk && authorOk;
    }});
  }}

  // ── Pagination ───────────────────────────────────────
  function applyPage(page) {{
    currentPage = page;
    var matching = getMatchingRows();
    var all = Array.from(scope.querySelectorAll('.nr-row'));
    var start = (page - 1) * PAGE_SIZE;
    var end   = start + PAGE_SIZE;
    all.forEach(function (row) {{ row.hidden = true; }});
    matching.slice(start, end).forEach(function (row) {{ row.hidden = false; }});
    renderPagination(matching.length);
  }}

  function renderPagination(total) {{
    var bar = scope.querySelector('.nr-pagination');
    if (!bar) return;
    var totalPages = Math.ceil(total / PAGE_SIZE);
    bar.innerHTML = '';
    if (totalPages <= 1) return;

    function makeBtn(label, page, active, disabled) {{
      var btn = document.createElement('button');
      btn.textContent = label;
      btn.className = 'nr-page-btn' + (active ? ' nr-page-btn--active' : '');
      btn.disabled = disabled;
      if (!disabled) {{
        btn.addEventListener('click', function () {{ applyPage(page); }});
      }}
      return btn;
    }}

    bar.appendChild(makeBtn('\u2039', currentPage - 1, false, currentPage === 1));
    for (var i = 1; i <= totalPages; i++) {{
      bar.appendChild(makeBtn(String(i), i, i === currentPage, false));
    }}
    bar.appendChild(makeBtn('\u203a', currentPage + 1, false, currentPage === totalPages));
  }}

  // ── Filters ──────────────────────────────────────────
  function applyFilters() {{
    currentPage = 1;
    applyPage(1);
  }}

  function updateLabel(dropdown) {{
    var allText = dropdown.querySelector('input[value="__all__"]')
      .parentElement.textContent.trim();
    var selected = getSelected(dropdown);
    var labelEl  = dropdown.querySelector('.nr-dropdown-label');
    if (selected.length === 0)      labelEl.textContent = allText;
    else if (selected.length === 1) labelEl.textContent = selected[0];
    else                            labelEl.textContent = selected.length + ' selected';
  }}

  function closeAll() {{
    scope.querySelectorAll('.nr-dropdown-menu').forEach(function (m) {{
      m.hidden = true;
    }});
    scope.querySelectorAll('.nr-dropdown-toggle').forEach(function (t) {{
      t.setAttribute('aria-expanded', 'false');
    }});
  }}

  scope.querySelectorAll('.nr-dropdown').forEach(function (dropdown) {{
    var toggle      = dropdown.querySelector('.nr-dropdown-toggle');
    var menu        = dropdown.querySelector('.nr-dropdown-menu');
    var allCb       = dropdown.querySelector('input[value="__all__"]');
    var specificCbs = Array.from(dropdown.querySelectorAll('input[type=checkbox]'))
      .filter(function (cb) {{ return cb.value !== '__all__'; }});

    toggle.addEventListener('click', function (e) {{
      e.stopPropagation();
      var wasOpen = !menu.hidden;
      closeAll();
      if (!wasOpen) {{
        menu.hidden = false;
        toggle.setAttribute('aria-expanded', 'true');
      }}
    }});

    allCb.addEventListener('change', function () {{
      if (allCb.checked) specificCbs.forEach(function (cb) {{ cb.checked = false; }});
      updateLabel(dropdown);
      applyFilters();
    }});

    specificCbs.forEach(function (cb) {{
      cb.addEventListener('change', function () {{
        allCb.checked = !specificCbs.some(function (c) {{ return c.checked; }});
        updateLabel(dropdown);
        applyFilters();
      }});
    }});

    menu.addEventListener('click', function (e) {{ e.stopPropagation(); }});
  }});

  document.addEventListener('click', closeAll);

  // Initial render
  applyPage(1);
}})();
</script>
""")

    parts.append("</div>")  # .nr-wrapper

    return nodes.raw("", "\n".join(parts), format="html")


def news_resources_sidebar_pages(app: Sphinx) -> Optional[List[str]]:
    """Return the list of pages that should display the news & resources sidebar widget.

    Parameters
    ----------
    app : sphinx.application.Sphinx
        Application instance for rendering the documentation.

    Returns
    -------
    Optional[List[str]]
        List of page names, or ``None`` if the feature is not configured.
    """
    html_theme_options = app.config.html_theme_options
    news_resources_options = html_theme_options.get("news_resources")
    if not news_resources_options:
        return None
    pages = news_resources_options.get("pages", ["index"])
    return [pages] if isinstance(pages, str) else pages


def get_news_resources_context(app: Sphinx) -> Optional[dict]:
    """Return the news & resources context dict for Jinja templates.

    Parameters
    ----------
    app : sphinx.application.Sphinx
        Application instance for rendering the documentation.

    Returns
    -------
    Optional[dict]
        Context dict with ``link`` and ``title`` keys, or ``None`` if not configured.
    """
    html_theme_options = app.config.html_theme_options
    news_resources_options = html_theme_options.get("news_resources")
    if not news_resources_options:
        return None

    link = news_resources_options.get("link")
    if not link:
        logger.warning(
            "The 'news_resources' theme option is missing the required 'link' key. "
            "The sidebar widget will not render correctly."
        )
    return {
        "link": link or "",
        "title": news_resources_options.get("title", "News & Resources"),
    }
