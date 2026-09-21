# Electronic Lab Notebooks Component Architecture (basiclive.core.notebooks)

## Context

Scientific beamline experiments produce continuous observational logs, protocol adjustments, and exploratory data that complement structured LIMS sample tracking and automated dataset collection. Previously, the standalone electronic lab notebook application `myeln` provided rich digital note-taking (supporting Markdown, LaTeX math via KaTeX, sketches, datasets, file attachments, and collaborative annotations). However, maintaining it as an external service caused data fragmentation, duplicate authentication systems, and missed opportunities to link notebook entries directly with beamline sessions, shipments, and research projects.

We decided to integrate the electronic lab notebook application directly into BasicLIVE as a core component (`basiclive.core.notebooks`), modernizing its architecture to comply with framework standards established in ADR-0001 (Pluggable framework architecture), ADR-0020 (Namespaced template hierarchy), ADR-0021 (Bootstrap 5 migration), and ADR-0022 (django-crisp-modals).

## Architectural Decisions

### 1. Component Modularity and Configuration
- **Pluggable Application**: Located at `basiclive/core/notebooks/` with application configuration `NotebooksConfig` (`label = "notebooks"`).
- **Settings Hierarchy**: App-level configuration is encapsulated in `basiclive/core/notebooks/conf.py` using `AppSettings("NOTEBOOKS", DEFAULTS)`, allowing host deployments to override settings via `NOTEBOOKS_*` prefixes.
- **Framework Integration**: Toggleable globally via `lims_settings.USE_NOTEBOOKS` (default `True`). The `export_settings` context processor exports `USE_NOTEBOOKS` to all templates, and `lims/navs.html` conditionally renders Notebook navigation links on the main navbar and in the global Search menu.

### 2. Domain Models and Relational Integrity
- **Identity & Ownership**: `Notebook` ownership references `settings.AUTH_USER_MODEL` (`lims.Project` in standard light-source deployments).
- **Beamline & Shift Association**: `Notebook` includes optional foreign keys to `lims.Project` (for research group scopes) and `lims.Session` (for linking experimental shifts and beamtime runs directly to a notebook).
- **Access Control & Permissions**:
  - `access` levels: `private` (0), `internal` (1), `public` (2).
  - `editor` roles: `owner` (0), `team` (1), `users` (2).
  - `members` ManyToMany relationship for granting shared team access.
- **Direct Entry Attachment & Native Temporal Partitioning**:
  - `Entry` records individual content items classified by `EntryType` (`text`, `data`, `file`, `sketch`, `image`, `video`) and links directly to `Notebook` via a ForeignKey (`related_name='entries'`).
  - Native ORM Partitioning: Date partitioning and calendar indexing are handled natively via the Django ORM using indexed timestamp queries (`created__date`, `dates('created', 'day')`, `TruncDate`). The obsolete `Page` intermediary model has been eliminated.
  - Windowed Pagination: Entries are loaded in count-based batches (`PAGE_SIZE`), rendering dynamic date separators (`page-separator`) when the calendar day changes across consecutive entries.
  - Immutability rule: `Entry.is_editable()` permits modification and deletion only on the calendar day of creation, provided no `Annotation` records have been attached. Historical entries are permanent audit records.
  - `Annotation` Architecture:
    - Unified Comment Model: All annotations are comments containing a required message (`text`) and optional text selection (`quote`). Standalone highlights without comments, DOM `node_index` positioning, and multi-line selection arrays were eliminated.
    - Quote-Based Anchoring: Matching occurs at the entry level via `mark.js` (`mark.annotation-quote`), gracefully degrading to general entry comments if the quoted text cannot be anchored.
    - RESTful Endpoints & Access Control: `EntryAnnotations` (`GET` list, `POST` create returning 201 Created + JSON) and `EntryAnnotationDetail` (`DELETE` returning 204 No Content). Viewers (`can_view`) may comment; deletions are restricted to the author or superusers. Attaching an annotation permanently locks the entry against author edits (`Entry.is_editable() == False`).
    - Dedicated Frontend Controller: `NotebookAnnotations` encapsulates popover creation, comment submission, badge toggling, quote highlighting, and deletion without global mutable state or inline event handlers.

### 3. Vendor Asset Management via `assets.json`
- **Zero Committed Vendor Binaries**: In accordance with project conventions, third-party vendor libraries are excluded from version control.
- **Manifest Architecture**: Vendor packages are declared in `basiclive/core/notebooks/static/notebooks/assets.json` specifying canonical CDN URLs, target relative paths, and Subresource Integrity (SRI) hashes (`sha256`, `sha384`, `sha512`):
  - SimpleMDE, KaTeX & Auto-render, Dropzone, Atrament, PapaParse, D3 & D3-legend, CLNDR, Moment.js, TinyColorPicker, HTML5Sortable, Highlight.js, and Mark.js.
- **Asset Fetching**: Automated retrieval via `python manage.py collectassets` validates SRI hashes upon download.
- **Native Assets**: Only native SCSS/CSS styles (`notebooks.scss`), custom calendar styling, `Myeln-Icons` fonts, and `notebooks.js` are tracked in git. Dead `/static/ext` references were eliminated in favor of clean relative paths.

### 4. Modal Forms and django-crisp-modals
- **Crispy Modal Forms**: `NotebookForm` inherits from `crisp_modals.forms.ModalModelForm`.
- **Semantic Layout**: Utilizes `crisp_modals.forms` layout components (`Row`, `FullWidth`, `ThirdWidth`, `HalfWidth`, `Button`) instead of legacy `col-*` grid wrappers.
- **Modal Views**: `CreateNotebook` and `UpdateNotebook` subclass `ModalCreateView` and `ModalUpdateView` rendering into `lims/modal/form.html`.
- **Ajax Standardization**: Deprecated `request.is_ajax()` was purged in favor of standard request headers and content-type detection.

### 5. Bootstrap 5 and Template Modernization
- **Template Namespacing**: All 12 templates reside under `basiclive/core/notebooks/templates/notebooks/` and extend `lims/base.html`.
- **Bootstrap 5 Conventions**: Replaced all legacy Bootstrap 4 classes and attributes (`text-right`, `float-right`, `custom-select`, `data-toggle`, `data-target`, `data-dismiss`) with modern equivalents (`text-end`, `float-end`, `form-select`, `data-bs-*`).
- **Markdown & Templatetags**: Deprecated `django-markdown2` was replaced with BasicLIVE's native `markup` library (`{% load markup %}` and `{{ text|markdown }}`). Templatetags in `bl_notebooks.py` provide data loading and JSON formatting.
- **JavaScript Modernization**: `notebooks.js` was refactored to use standard `bootstrap.Popover` and `bootstrap.Modal` instances.

### 6. Metrics and Template Integrity
- **Metrics API**: `basiclive.core.notebooks.stats` provides `notebook_metrics(user=None)` and `project_notebook_metrics(project)` for aggregate reporting (`total_notebooks`, `total_entries`, `total_days`). Active days are computed natively via `entries.dates('created', 'day').count()`.
- **Integrity Suite**: Registered in `tests/test_template_integrity.py` to continuously verify template compilation, view template existence, URL routing, modal form inheritance, Bootstrap 5 compliance, and `assets.json` integrity.
