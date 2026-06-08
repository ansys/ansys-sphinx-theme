---
description: "ansys-sphinx-theme workflows: update, review, latest"
agent: agent
argument-hint: "update | review | latest"
tools: [read, edit, search, execute, web, todo]
---

<!-- Installed from ansys-sphinx-theme {{theme_version}} -->

Based on the keyword provided, execute the matching workflow below. If no keyword was given, ask the user which one they want: **update**, **review**, or **latest**.

The latest available theme version is **{{theme_version}}** (the version this prompt was installed from).
If `{{theme_version}}` contains `dev` (e.g. `1.9.dev0`), this is a development build — treat it as the latest and do not prompt to upgrade.

---

## Workflow: `update`

Update `ansys-sphinx-theme` to the latest version in this PyAnsys library project.

### 1. Check current version
Run: `pip show ansys-sphinx-theme`

### 2. Check latest version
The latest theme version is **{{theme_version}}** (from the prompt header above). No network call needed.
If `{{theme_version}}` contains `dev`, the project is already on the development tip — skip the upgrade step and tell the user.

### 3. Fetch the release notes
Fetch: https://sphinxdocs.ansys.com/version/stable/changelog.html
Show only sections for versions newer than the project pin and up to **{{theme_version}}**. Summarise new options, deprecations, and breaking changes.

### 4. Find the version pin
Run: `grep -r "ansys-sphinx-theme" pyproject.toml requirements*.txt setup.cfg tox.ini doc/ 2>/dev/null`

### 5. Propose the update
Show: current pin → proposed new pin, any extras that need updating.
Ask for confirmation before making any changes.

### 6. Update the pin and install
- Edit the pin in the relevant file
- Run: `pip install --upgrade "ansys-sphinx-theme[<extras>]"`
- Verify: `pip show ansys-sphinx-theme`

### 7. List new and missing options
Find conf.py: `find . -name "conf.py" -path "*/doc/*" -o -name "conf.py" -path "*/source/*" 2>/dev/null`

Present all new and missing `html_theme_options` in a table. Do **not** make any changes yet.

| Option | Required? | Default | What it does | Already set? |
|--------|-----------|---------|--------------|-------------|
| `example_option` | Optional | `None` | Brief description of feature/behaviour | ✗ |

For each **Optional** row, ask the user: "Would you like to add any of these? (list numbers or 'none')".
For each **Mandatory** row, add automatically after confirmation of the version bump.

### 8. Apply selected options
Add only the options the user confirmed. Never remove or overwrite existing values.

### 9. Build docs to verify
- If `tox.ini` exists: `tox -e doc-html`
- If `doc/Makefile` exists: `make -C doc html`
- Fallback: `sphinx-build doc/source doc/_build/html -b html -W --keep-going`

### 10. Report
Summarise: old version → new version, files changed, new conf.py options added, build result.

---

## Workflow: `review`

Review the current `ansys-sphinx-theme` setup in this project and report findings without making any changes.

### 1. Detect installed version
Run: `pip show ansys-sphinx-theme`

### 2. Check if up-to-date
The latest theme version is **{{theme_version}}** (from the prompt header). Compare against the installed version from step 1.
If `{{theme_version}}` contains `dev`, the project is on a development build — report it as the latest and skip any upgrade suggestion.

### 3. Find all theme references
Run: `grep -r "ansys-sphinx-theme\|html_theme\|html_theme_options" pyproject.toml requirements*.txt tox.ini doc/ 2>/dev/null`

### 4. Read conf.py
Find and read `conf.py`. List all `html_theme_options` currently set.

### 5. Cross-check against known options
Fetch: https://sphinxdocs.ansys.com/version/stable/changelog.html
Show only sections for versions newer than the installed version and up to **{{theme_version}}**. Extract new options and deprecations.

### 6. Report (read-only)
Produce two tables. No files are modified.

**Version & pin status**

| | Value |
|---|---|
| Installed | `x.y.z` |
| Latest stable | `x.y.z` |
| Status | Current / Outdated |

**Options audit**

| Option | Required? | Default | What it does | Status |
|--------|-----------|---------|--------------|--------|
| `github_url` | Mandatory | — | Links the GitHub icon in the navbar | ✓ set |
| `some_new_option` | Optional | `False` | Hides the secondary sidebar TOC | ✗ missing |
| `old_option` | Removed | — | Was used for X, now deprecated | ⚠ still set |

Legend: ✓ present · ✗ missing · ⚠ deprecated/removed
---

## Workflow: `latest`

List all the new features, options, and deprecations in the latest `ansys-sphinx-theme` version **{{theme_version}}**
compared to the installed version, without making any changes.

### 1. Detect installed version
Run: `pip show ansys-sphinx-theme` or read from the `review` workflow if already executed.

### 2. Fetch the release notes
Fetch: https://sphinxdocs.ansys.com/version/stable/changelog.html
Show only sections for versions newer than the installed version and up to **{{theme_version}}**
Summarise new options, deprecations, and breaking changes in a table.

| Option | Required? | Default | What it does | Status |
|--------|-----------|---------|--------------|--------|
| `example_option` | Optional | `None` | Brief description of feature/behaviour | New in 1.9 |
| `old_option` | Removed | — | Was used for X, now deprecated | Removed in 1.8 |

Legend: New in X.Y · Removed in X.Y