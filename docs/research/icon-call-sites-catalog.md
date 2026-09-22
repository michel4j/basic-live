# Audit and Migration Catalog: `show_icon` Call Sites

> **Context**: Work package for ticket [#111](https://github.com/michel4j/basic-live/issues/111) under Wayfinder Map [#110](https://github.com/michel4j/basic-live/issues/110) (*Pluggable Icon Backend and Semantic show_icon Migration*).

## Executive Summary

This document provides a comprehensive audit and migration catalog for all `show_icon` template tag invocations across the BasicLIVE codebase. Every invocation has been extracted, analyzed, mapped to canonical plain icon names and standardized size tokens, and evaluated for edge cases (including compound utility classes, anomalous token placements, vestigial color parameters, and dynamic model-driven icons).

### Key Inventory Statistics

- **Total `show_icon` Invocations**: 165
- **Total Template Files**: 49
- **Apps Surveyed**: 6 distinct Django applications (`lims`, `schedule`, `notebooks`, `acl`, `crm`, `publications`)

#### Distribution by Application

| Application | Template Files | Total `show_icon` Calls | Percentage |
| :--- | :--- | :--- | :--- |
| `basiclive.core.lims` | 37 | 126 | 76.4% |
| `basiclive.core.schedule` | 5 | 17 | 10.3% |
| `basiclive.core.notebooks` | 3 | 7 | 4.2% |
| `basiclive.core.acl` | 2 | 5 | 3.0% |
| `basiclive.core.crm` | 1 | 5 | 3.0% |
| `basiclive.core.publications` | 1 | 5 | 3.0% |
| **Total** | **49** | **165** | **100.0%** |

#### Distribution by Size Token

| Size Token | Call Count | Percentage | Target Framework Class | Typical Context |
| :--- | :--- | :--- | :--- | :--- |
| `'md'` | 115 (114 static + 1 dynamic) | 69.7% | `.bl-icon-md` (1.5rem) | Action buttons, toolbars, detail card tools, navigation |
| `'sm'` | 27 | 16.4% | `.bl-icon-sm` (1.1rem) | Inline badges, list item metadata, compact toolboxes |
| `(none)` / unscaled | 23 | 13.9% | Inherits text font size | Top navbar items, dropdown items, comment headers |
| **Total** | **165** | **100.0%** | | |

## Canonical Glyph Inventory and Themify Mapping

Across all 165 calls, **58 unique static icon glyphs** and **1 dynamic icon property** (`entry_type.icon`) are utilized. Under the hybrid translation design specified in Map [#110](https://github.com/michel4j/basic-live/issues/110) and Task [#112](https://github.com/michel4j/basic-live/issues/112), `ThemifyBackend` maps canonical icon names directly to `ti-{name}` fallback while supporting high-level aliases.

| Canonical Plain Icon Name | Call Count | Legacy Themify Class | Recommended Aliases / Semantics | Category |
| :--- | :--- | :--- | :--- | :--- |
| `trash` | 9 | `ti-trash` | *(direct {prefix}-{name})* | Editing & Actions |
| `bar-chart-alt` | 7 | `ti-bar-chart-alt` | `chart` | Metrics & Charts |
| `calendar` | 7 | `ti-calendar` | *(direct {prefix}-{name})* | Date & Time |
| `layout-grid3` | 7 | `ti-layout-grid3` | `grid` | Layout & Data Views |
| `paint-bucket` | 7 | `ti-paint-bucket` | `samples-tool` | Logistics & Samples |
| `lock` | 6 | `ti-lock` | *(direct {prefix}-{name})* | Identity & Access |
| `pencil` | 6 | `ti-pencil` | *(direct {prefix}-{name})* | Editing & Actions |
| `pulse` | 6 | `ti-pulse` | `activity`, `stats` | Metrics & Charts |
| `download` | 5 | `ti-download` | *(direct {prefix}-{name})* | Logistics & Samples |
| `pencil-alt` | 5 | `ti-pencil-alt` | `edit` | Editing & Actions |
| `timer` | 5 | `ti-timer` | *(direct {prefix}-{name})* | Date & Time |
| `check-box` | 4 | `ti-check-box` | *(direct {prefix}-{name})* | Editing & Actions |
| `headphone-alt` | 4 | `ti-headphone-alt` | `support` | Identity & Access |
| `key` | 4 | `ti-key` | *(direct {prefix}-{name})* | Identity & Access |
| `location-arrow` | 4 | `ti-location-arrow` | *(direct {prefix}-{name})* | Logistics & Samples |
| `star` | 4 | `ti-star` | *(direct {prefix}-{name})* | Navigation & System |
| `tag` | 4 | `ti-tag` | *(direct {prefix}-{name})* | General |
| `user` | 4 | `ti-user` | *(direct {prefix}-{name})* | Identity & Access |
| `comment-alt` | 3 | `ti-comment-alt` | *(direct {prefix}-{name})* | Communication |
| `info-alt` | 3 | `ti-info-alt` | `info` | Navigation & System |
| `layout-accordion-list` | 3 | `ti-layout-accordion-list` | *(direct {prefix}-{name})* | Layout & Data Views |
| `move` | 3 | `ti-move` | *(direct {prefix}-{name})* | Editing & Actions |
| `plus` | 3 | `ti-plus` | *(direct {prefix}-{name})* | Editing & Actions |
| `rss-alt` | 3 | `ti-rss-alt` | *(direct {prefix}-{name})* | General |
| `ruler-pencil` | 3 | `ti-ruler-pencil` | *(direct {prefix}-{name})* | Editing & Actions |
| `book` | 2 | `ti-book` | *(direct {prefix}-{name})* | Layout & Data Views |
| `comments` | 2 | `ti-comments` | *(direct {prefix}-{name})* | Communication |
| `comments-alt` | 2 | `ti-comments-alt` | *(direct {prefix}-{name})* | Communication |
| `control-backward` | 2 | `ti-control-backward` | `rewind`, `recall` | Navigation Arrows |
| `email` | 2 | `ti-email` | `mail` | Communication |
| `home` | 2 | `ti-home` | *(direct {prefix}-{name})* | Navigation & System |
| `list` | 2 | `ti-list` | *(direct {prefix}-{name})* | Layout & Data Views |
| `pie-chart` | 2 | `ti-pie-chart` | *(direct {prefix}-{name})* | Metrics & Charts |
| `shopping-cart-full` | 2 | `ti-shopping-cart-full` | `cart` | Logistics & Samples |
| `target` | 2 | `ti-target` | *(direct {prefix}-{name})* | Identity & Access |
| `time` | 2 | `ti-time` | `clock` | Date & Time |
| `view-list-alt` | 2 | `ti-view-list-alt` | `table-list` | Layout & Data Views |
| `alert` | 1 | `ti-alert` | `warning`, `danger` | Navigation & System |
| `angle-left` | 1 | `ti-angle-left` | *(direct {prefix}-{name})* | Navigation Arrows |
| `angle-right` | 1 | `ti-angle-right` | *(direct {prefix}-{name})* | Navigation Arrows |
| `archive` | 1 | `ti-archive` | *(direct {prefix}-{name})* | Logistics & Samples |
| `arrow-left` | 1 | `ti-arrow-left` | *(direct {prefix}-{name})* | Navigation Arrows |
| `arrow-right` | 1 | `ti-arrow-right` | *(direct {prefix}-{name})* | Navigation Arrows |
| `bag` | 1 | `ti-bag` | *(direct {prefix}-{name})* | Logistics & Samples |
| `check` | 1 | `ti-check` | *(direct {prefix}-{name})* | Editing & Actions |
| `clipboard` | 1 | `ti-clipboard` | *(direct {prefix}-{name})* | Layout & Data Views |
| `comment` | 1 | `ti-comment` | *(direct {prefix}-{name})* | Communication |
| `drupal` | 1 | `ti-drupal` | `dark`, `moon` | Navigation & System |
| `entry_type.icon` | 1 | `f'entry-selector-{name}'` | `entry-selector-*` (e.g. text, sketch, data, image, video, file) | Dynamic (Notebooks) |
| `layout` | 1 | `ti-layout` | *(direct {prefix}-{name})* | Layout & Data Views |
| `layout-list-post` | 1 | `ti-layout-list-post` | `post-list` | Layout & Data Views |
| `layout-width-full` | 1 | `ti-layout-width-full` | *(direct {prefix}-{name})* | Layout & Data Views |
| `location-pin` | 1 | `ti-location-pin` | *(direct {prefix}-{name})* | Logistics & Samples |
| `package` | 1 | `ti-package` | *(direct {prefix}-{name})* | Logistics & Samples |
| `settings` | 1 | `ti-settings` | *(direct {prefix}-{name})* | Navigation & System |
| `shine` | 1 | `ti-shine` | `light`, `sun` | Navigation & System |
| `truck` | 1 | `ti-truck` | *(direct {prefix}-{name})* | Logistics & Samples |
| `unlock` | 1 | `ti-unlock` | *(direct {prefix}-{name})* | Identity & Access |
| `widget` | 1 | `ti-widget` | `auto`, `system` | Navigation & System |

## Identified Edge Cases & Migration Strategies

During the comprehensive scan, 16 call sites exhibited non-standard patterns that require explicit handling during migration.

### 1. Compound Styling Classes Embedded in `icon` (1 site)
- **Call site**: `basiclive/core/schedule/templates/schedule/beamtime.html:11`
- **Legacy argument**: `icon='ti ti-sm ti-alert text-danger'`
- **Analysis**: The Bootstrap color utility `text-danger` was concatenated directly into the icon class string to render the warning alert in red.
- **Migration Target**: Extract the utility class into the `extra_class` argument: `{% show_icon icon='alert' size='sm' extra_class='text-danger' %}`.
- **Downstream Dependency**: Ticket [#114](https://github.com/michel4j/basic-live/issues/114) must include `extra_class` in `show_icon` and pass it to the rendered template.

### 2. Anomaly: Sizing Token at End of Icon String (7 sites)
- **Call sites**:
  - `basiclive/core/lims/templates/lims/details/project-profile.html:53` (`icon="ti ti-key ti-sm"`)
  - `basiclive/core/lims/templates/lims/details/user.html:85` (`icon="ti ti-key ti-sm"`)
  - `basiclive/core/lims/templates/lims/forms/container-spreadsheet.html:45` (`icon="ti ti-info-alt ti-md"`)
  - `basiclive/core/lims/templates/lims/forms/seat-samples.html:13` (`icon="ti ti-paint-bucket ti-md"`)
  - `basiclive/core/lims/templates/lims/forms/seat-samples.html:77` (`icon="ti ti-info-alt ti-md"`)
  - `basiclive/core/notebooks/templates/notebooks/notebook.html:23` (`icon="ti ti-calendar ti-md"`)
  - `basiclive/core/notebooks/templates/notebooks/notebook.html:27` (`icon="ti ti-settings ti-md"`)
  - `basiclive/core/notebooks/templates/notebooks/notebook_list.html:17` (`icon="ti ti-plus ti-md"`)
- **Analysis**: In standard calls, the size token was the second token (`ti ti-md ti-...`). In these 8 calls (7 distinct glyph patterns across 8 sites), the size token was placed at the end.
- **Migration Target**: Discard string token order; cleanly map to `icon='<name>' size='<size>'`.

### 3. Vestigial `color` Attribute Without `badge` (6 sites)
- **Call sites**:
  - `basiclive/core/lims/templates/lims/details/container.html:51` (`color="primary"`)
  - `basiclive/core/lims/templates/lims/details/group.html:35` (`color="primary"`)
  - `basiclive/core/lims/templates/lims/details/request-list-item.html:25` (`color="primary"`)
  - `basiclive/core/lims/templates/lims/tools-shipment-edit.html:22` (`color="primary"`)
  - `basiclive/core/schedule/templates/schedule/beamtime-list-item.html:36` (`color='info'`)
  - `basiclive/core/schedule/templates/schedule/beamtime-list-item.html:41` (`color='info'`)
- **Analysis**: In `icon-info.html`, `color` is only evaluated when `badge` is present (`{% if badge is not None %}<span class="... text-bg-{{ color }}">...{% endif %}`). In `container.html:51`, `group.html:35`, and `tools-shipment-edit.html:22`, lines were duplicated from an `{% if not object.samples.exists %}` branch where `badge="+" color="primary"` was used, leaving orphaned `color="primary"` in the `{% else %}` block. In `beamtime-list-item.html`, the author likely expected `color='info'` to tint the icon.
- **Migration Target**: Retain `color` in the tag call if desired for future icon coloring in #114, or clean up vestigial color if strictly reserved for badge backgrounds.

### 4. Dynamic Model-Driven Icon Expression (1 site)
- **Call site**: `basiclive/core/notebooks/templates/notebooks/notebook.html:39`
- **Legacy invocation**: `{% show_icon icon=entry_type.icon label=entry_type.name|title %}`
- **Analysis**: `entry_type.icon` is a method on `basiclive.core.notebooks.models.EntryType` that returns `f'ti-md entry-selector-{self.name.lower()}'`. This tightly couples the model to the `ti-md` class.
- **Migration Target**:
  1. In `EntryType.icon(self)` (or a new property `canonical_icon`), return plain `f'entry-selector-{self.name.lower()}'`.
  2. In `notebook.html`, update tag to `{% show_icon label=entry_type.name|title icon=entry_type.icon size='md' %}`.
  3. In `ThemifyBackend` (#112), provide canonical alias mappings for `entry-selector-text`, `entry-selector-video`, `entry-selector-image`, `entry-selector-sketch`, `entry-selector-data`, and `entry-selector-file`.

## Detailed Migration Catalog (All 165 Call Sites)

The tables below catalog every single `show_icon` call site in the repository, organized by Django application and file.

### Core LIMS (`basiclive/core/lims`) — 126 Call Sites

#### `basiclive/core/lims/templates/lims/comments.html` (2 calls)

| Line | Current Legacy Call | Proposed Replacement Tag | Plain Icon | Size | Notes / Edge Cases |
| :--- | :--- | :--- | :--- | :--- | :--- |
| 7 | `{% show_icon icon="ti ti-comments" %}` | `{% show_icon icon="comments" %}` | `comments` | *(none)* | Clean standard migration |
| 16 | `{% show_icon icon="ti ti-comments" %}` | `{% show_icon icon="comments" %}` | `comments` | *(none)* | Clean standard migration |

#### `basiclive/core/lims/templates/lims/data/data-frames.html` (2 calls)

| Line | Current Legacy Call | Proposed Replacement Tag | Plain Icon | Size | Notes / Edge Cases |
| :--- | :--- | :--- | :--- | :--- | :--- |
| 98 | `{% show_icon icon="ti ti-arrow-left" %}` | `{% show_icon icon="arrow-left" %}` | `arrow-left` | *(none)* | Clean standard migration |
| 101 | `{% show_icon icon="ti ti-arrow-right" %}` | `{% show_icon icon="arrow-right" %}` | `arrow-right` | *(none)* | Clean standard migration |

#### `basiclive/core/lims/templates/lims/data/data.html` (2 calls)

| Line | Current Legacy Call | Proposed Replacement Tag | Plain Icon | Size | Notes / Edge Cases |
| :--- | :--- | :--- | :--- | :--- | :--- |
| 71 | `{% show_icon label="Download" icon="ti ti-md ti-download" %}` | `{% show_icon label="Download" icon="download" size='md' %}` | `download` | `md` | Clean standard migration |
| 75 | `{% show_icon label="Download" icon="ti ti-md ti-download" %}` | `{% show_icon label="Download" icon="download" size='md' %}` | `download` | `md` | Clean standard migration |

#### `basiclive/core/lims/templates/lims/details/beamline.html` (5 calls)

| Line | Current Legacy Call | Proposed Replacement Tag | Plain Icon | Size | Notes / Edge Cases |
| :--- | :--- | :--- | :--- | :--- | :--- |
| 29 | `{% show_icon label='History' icon='ti ti-md ti-timer' %}` | `{% show_icon label='History' icon='timer' size='md' %}` | `timer` | `md` | Clean standard migration |
| 33 | `{% show_icon label='Stats' icon='ti ti-md ti-pulse' %}` | `{% show_icon label='Stats' icon='pulse' size='md' %}` | `pulse` | `md` | Clean standard migration |
| 36 | `{% show_icon label='Usage' icon='ti ti-md ti-pie-chart' %}` | `{% show_icon label='Usage' icon='pie-chart' size='md' %}` | `pie-chart` | `md` | Clean standard migration |
| 39 | `{% show_icon label='Sessions' icon='ti ti-md ti-calendar' %}` | `{% show_icon label='Sessions' icon='calendar' size='md' %}` | `calendar` | `md` | Clean standard migration |
| 43 | `{% show_icon label='Comment' icon='ti ti-md ti-comment-alt' %}` | `{% show_icon label='Comment' icon='comment-alt' size='md' %}` | `comment-alt` | `md` | Clean standard migration |

#### `basiclive/core/lims/templates/lims/details/container.html` (5 calls)

| Line | Current Legacy Call | Proposed Replacement Tag | Plain Icon | Size | Notes / Edge Cases |
| :--- | :--- | :--- | :--- | :--- | :--- |
| 22 | `{% show_icon icon="ti ti-lock" %}` | `{% show_icon icon="lock" %}` | `lock` | *(none)* | Clean standard migration |
| 49 | `{% show_icon label='Samples' icon='ti ti-md ti-paint-bucket' badge="+" color="primary" %}` | `{% show_icon label='Samples' icon='paint-bucket' size='md' badge="+" color="primary" %}` | `paint-bucket` | `md` | Clean standard migration |
| 51 | `{% show_icon label='Samples' icon='ti ti-md ti-paint-bucket' color="primary" %}` | `{% show_icon label='Samples' icon='paint-bucket' size='md' color="primary" %}` | `paint-bucket` | `md` | Specified `color="primary"` without `badge` (vestigial in legacy template; had no visual effect). |
| 58 | `{% show_icon label='History' icon='ti ti-md ti-timer' %}` | `{% show_icon label='History' icon='timer' size='md' %}` | `timer` | `md` | Clean standard migration |
| 63 | `{% show_icon label='Load History' icon='ti ti-md ti-timer' %}` | `{% show_icon label='Load History' icon='timer' size='md' %}` | `timer` | `md` | Clean standard migration |

#### `basiclive/core/lims/templates/lims/details/group-list-item.html` (2 calls)

| Line | Current Legacy Call | Proposed Replacement Tag | Plain Icon | Size | Notes / Edge Cases |
| :--- | :--- | :--- | :--- | :--- | :--- |
| 10 | `{% show_icon icon='ti ti-md ti-move' tooltip='Priority' %}` | `{% show_icon icon='move' size='md' tooltip='Priority' %}` | `move` | `md` | Clean standard migration |
| 33 | `{% show_icon label='Request' icon="ti ti-md ti-ruler-pencil" badge="+" color="primary" %}` | `{% show_icon label='Request' icon="ruler-pencil" size='md' badge="+" color="primary" %}` | `ruler-pencil` | `md` | Clean standard migration |

#### `basiclive/core/lims/templates/lims/details/group-samples.html` (3 calls)

| Line | Current Legacy Call | Proposed Replacement Tag | Plain Icon | Size | Notes / Edge Cases |
| :--- | :--- | :--- | :--- | :--- | :--- |
| 24 | `{% show_icon icon="ti ti-comments-alt" %}` | `{% show_icon icon="comments-alt" %}` | `comments-alt` | *(none)* | Clean standard migration |
| 34 | `{% show_icon icon="ti ti-comments-alt" %}` | `{% show_icon icon="comments-alt" %}` | `comments-alt` | *(none)* | Clean standard migration |
| 37 | `{% show_icon icon="ti ti-check-box" %}` | `{% show_icon icon="check-box" %}` | `check-box` | *(none)* | Clean standard migration |

#### `basiclive/core/lims/templates/lims/details/group.html` (5 calls)

| Line | Current Legacy Call | Proposed Replacement Tag | Plain Icon | Size | Notes / Edge Cases |
| :--- | :--- | :--- | :--- | :--- | :--- |
| 16 | `{% show_icon icon="ti ti-lock" %}` | `{% show_icon icon="lock" %}` | `lock` | *(none)* | Clean standard migration |
| 33 | `{% show_icon label='Samples' icon='ti ti-md ti-paint-bucket' badge="+" color="primary" %}` | `{% show_icon label='Samples' icon='paint-bucket' size='md' badge="+" color="primary" %}` | `paint-bucket` | `md` | Clean standard migration |
| 35 | `{% show_icon label='Samples' icon='ti ti-md ti-paint-bucket' color="primary" %}` | `{% show_icon label='Samples' icon='paint-bucket' size='md' color="primary" %}` | `paint-bucket` | `md` | Specified `color="primary"` without `badge` (vestigial in legacy template; had no visual effect). |
| 40 | `{% show_icon label='Request' icon="ti ti-md ti-ruler-pencil" badge="+" color="primary" %}` | `{% show_icon label='Request' icon="ruler-pencil" size='md' badge="+" color="primary" %}` | `ruler-pencil` | `md` | Clean standard migration |
| 81 | `{% show_icon icon="ti ti-move" %}` | `{% show_icon icon="move" %}` | `move` | *(none)* | Clean standard migration |

#### `basiclive/core/lims/templates/lims/details/project-profile.html` (5 calls)

| Line | Current Legacy Call | Proposed Replacement Tag | Plain Icon | Size | Notes / Edge Cases |
| :--- | :--- | :--- | :--- | :--- | :--- |
| 24 | `{% show_icon label='My Stats' icon='ti ti-md ti-pulse' %}` | `{% show_icon label='My Stats' icon='pulse' size='md' %}` | `pulse` | `md` | Clean standard migration |
| 27 | `{% show_icon label='Add SSH Key' icon='ti ti-md ti-key' %}` | `{% show_icon label='Add SSH Key' icon='key' size='md' %}` | `key` | `md` | Clean standard migration |
| 30 | `{% show_icon label='Edit Profile' icon='ti ti-md ti-pencil' %}` | `{% show_icon label='Edit Profile' icon='pencil' size='md' %}` | `pencil` | `md` | Clean standard migration |
| 53 | `{% show_icon icon="ti ti-key ti-sm" %}` | `{% show_icon icon="key" size='sm' %}` | `key` | `sm` | Size token `ti-sm` positioned at end of icon string in legacy call. |
| 59 | `{% show_icon label='Delete' icon='ti ti-md ti-trash' %}` | `{% show_icon label='Delete' icon='trash' size='md' %}` | `trash` | `md` | Clean standard migration |

#### `basiclive/core/lims/templates/lims/details/project-statistics.html` (1 call)

| Line | Current Legacy Call | Proposed Replacement Tag | Plain Icon | Size | Notes / Edge Cases |
| :--- | :--- | :--- | :--- | :--- | :--- |
| 24 | `{% show_icon label='My Profile' icon='ti ti-md ti-user' %}` | `{% show_icon label='My Profile' icon='user' size='md' %}` | `user` | `md` | Clean standard migration |

#### `basiclive/core/lims/templates/lims/details/report.html` (2 calls)

| Line | Current Legacy Call | Proposed Replacement Tag | Plain Icon | Size | Notes / Edge Cases |
| :--- | :--- | :--- | :--- | :--- | :--- |
| 18 | `{% show_icon label="Download" icon="ti ti-md ti-download" %}` | `{% show_icon label="Download" icon="download" size='md' %}` | `download` | `md` | Clean standard migration |
| 22 | `{% show_icon label="Download" icon="ti ti-md ti-download" %}` | `{% show_icon label="Download" icon="download" size='md' %}` | `download` | `md` | Clean standard migration |

#### `basiclive/core/lims/templates/lims/details/request-list-item.html` (2 calls)

| Line | Current Legacy Call | Proposed Replacement Tag | Plain Icon | Size | Notes / Edge Cases |
| :--- | :--- | :--- | :--- | :--- | :--- |
| 10 | `{% show_icon icon='ti ti-md ti-move' tooltip='Priority' %}` | `{% show_icon icon='move' size='md' tooltip='Priority' %}` | `move` | `md` | Clean standard migration |
| 25 | `{% show_icon icon="ti ti-md ti-pencil" color="primary" %}` | `{% show_icon icon="pencil" size='md' color="primary" %}` | `pencil` | `md` | Specified `color="primary"` without `badge` (vestigial in legacy template; had no visual effect). |

#### `basiclive/core/lims/templates/lims/details/request-summary.html` (4 calls)

| Line | Current Legacy Call | Proposed Replacement Tag | Plain Icon | Size | Notes / Edge Cases |
| :--- | :--- | :--- | :--- | :--- | :--- |
| 15 | `{% show_icon label=request.get_status_display icon='ti ti-md ti-comment-alt' %}` | `{% show_icon label=request.get_status_display icon='comment-alt' size='md' %}` | `comment-alt` | `md` | Clean standard migration |
| 17 | `{% show_icon label=request.get_status_display icon='ti ti-md ti-comment' %}` | `{% show_icon label=request.get_status_display icon='comment' size='md' %}` | `comment` | `md` | Clean standard migration |
| 22 | `{% show_icon label=request.get_status_display icon='ti ti-md ti-check-box' tooltip=request.get_status_display %}` | `{% show_icon label=request.get_status_display icon='check-box' size='md' tooltip=request.get_status_display %}` | `check-box` | `md` | Clean standard migration |
| 24 | `{% show_icon label=request.get_status_display icon='ti ti-md ti-layout-width-full' tooltip=request.get_status_display %}` | `{% show_icon label=request.get_status_display icon='layout-width-full' size='md' tooltip=request.get_status_display %}` | `layout-width-full` | `md` | Clean standard migration |

#### `basiclive/core/lims/templates/lims/details/request.html` (1 call)

| Line | Current Legacy Call | Proposed Replacement Tag | Plain Icon | Size | Notes / Edge Cases |
| :--- | :--- | :--- | :--- | :--- | :--- |
| 17 | `{% show_icon icon="ti ti-lock" %}` | `{% show_icon icon="lock" %}` | `lock` | *(none)* | Clean standard migration |

#### `basiclive/core/lims/templates/lims/details/requesttype-list.html` (1 call)

| Line | Current Legacy Call | Proposed Replacement Tag | Plain Icon | Size | Notes / Edge Cases |
| :--- | :--- | :--- | :--- | :--- | :--- |
| 6 | `{% show_icon label="Add Request Type" icon="ti ti-md ti-plus" %}` | `{% show_icon label="Add Request Type" icon="plus" size='md' %}` | `plus` | `md` | Clean standard migration |

#### `basiclive/core/lims/templates/lims/details/requesttype.html` (3 calls)

| Line | Current Legacy Call | Proposed Replacement Tag | Plain Icon | Size | Notes / Edge Cases |
| :--- | :--- | :--- | :--- | :--- | :--- |
| 29 | `{% show_icon label='Layout' icon='ti ti-md ti-layout' %}` | `{% show_icon label='Layout' icon='layout' size='md' %}` | `layout` | `md` | Clean standard migration |
| 33 | `{% show_icon label='Edit' icon='ti ti-md ti-pencil-alt' %}` | `{% show_icon label='Edit' icon='pencil-alt' size='md' %}` | `pencil-alt` | `md` | Clean standard migration |
| 36 | `{% show_icon label='Delete' icon='ti ti-md ti-trash' %}` | `{% show_icon label='Delete' icon='trash' size='md' %}` | `trash` | `md` | Clean standard migration |

#### `basiclive/core/lims/templates/lims/details/sample.html` (3 calls)

| Line | Current Legacy Call | Proposed Replacement Tag | Plain Icon | Size | Notes / Edge Cases |
| :--- | :--- | :--- | :--- | :--- | :--- |
| 24 | `{% show_icon label='Request' icon="ti ti-md ti-ruler-pencil" badge="+" color="primary" %}` | `{% show_icon label='Request' icon="ruler-pencil" size='md' badge="+" color="primary" %}` | `ruler-pencil` | `md` | Clean standard migration |
| 31 | `{% show_icon label='Edit' icon='ti ti-md ti-pencil-alt' %}` | `{% show_icon label='Edit' icon='pencil-alt' size='md' %}` | `pencil-alt` | `md` | Clean standard migration |
| 34 | `{% show_icon label='Delete' icon='ti ti-md ti-trash' %}` | `{% show_icon label='Delete' icon='trash' size='md' %}` | `trash` | `md` | Clean standard migration |

#### `basiclive/core/lims/templates/lims/details/session-data.html` (1 call)

| Line | Current Legacy Call | Proposed Replacement Tag | Plain Icon | Size | Notes / Edge Cases |
| :--- | :--- | :--- | :--- | :--- | :--- |
| 18 | `{% show_icon label='Reports' icon='ti ti-md ti-bar-chart-alt' badge=session.num_reports %}` | `{% show_icon label='Reports' icon='bar-chart-alt' size='md' badge=session.num_reports %}` | `bar-chart-alt` | `md` | Clean standard migration |

#### `basiclive/core/lims/templates/lims/details/session-list-item.html` (4 calls)

| Line | Current Legacy Call | Proposed Replacement Tag | Plain Icon | Size | Notes / Edge Cases |
| :--- | :--- | :--- | :--- | :--- | :--- |
| 10 | `{% show_icon label='Feedback' icon='ti ti-sm ti-star' %}` | `{% show_icon label='Feedback' icon='star' size='sm' %}` | `star` | `sm` | Clean standard migration |
| 13 | `{% show_icon label=session.start.date|date:"M j"|upper icon='ti ti-sm ti-time' %}` | `{% show_icon label=session.start.date|date:"M j"|upper icon='time' size='sm' %}` | `time` | `sm` | Clean standard migration |
| 28 | `{% show_icon label='Data' badge=session.data_count icon='ti ti-sm ti-layout-grid3' %}` | `{% show_icon label='Data' icon='layout-grid3' size='sm' badge=session.data_count %}` | `layout-grid3` | `sm` | Clean standard migration |
| 31 | `{% show_icon label='Reports' badge=session.report_count icon='ti ti-sm ti-bar-chart-alt' %}` | `{% show_icon label='Reports' icon='bar-chart-alt' size='sm' badge=session.report_count %}` | `bar-chart-alt` | `sm` | Clean standard migration |

#### `basiclive/core/lims/templates/lims/details/session-reports.html` (1 call)

| Line | Current Legacy Call | Proposed Replacement Tag | Plain Icon | Size | Notes / Edge Cases |
| :--- | :--- | :--- | :--- | :--- | :--- |
| 15 | `{% show_icon label='Data' icon='ti ti-md ti-layout-grid3' badge=session.datasets.count %}` | `{% show_icon label='Data' icon='layout-grid3' size='md' badge=session.datasets.count %}` | `layout-grid3` | `md` | Clean standard migration |

#### `basiclive/core/lims/templates/lims/details/session-statistics.html` (1 call)

| Line | Current Legacy Call | Proposed Replacement Tag | Plain Icon | Size | Notes / Edge Cases |
| :--- | :--- | :--- | :--- | :--- | :--- |
| 11 | `{% show_icon label='History' icon='ti ti-md ti-timer' %}` | `{% show_icon label='History' icon='timer' size='md' %}` | `timer` | `md` | Clean standard migration |

#### `basiclive/core/lims/templates/lims/details/session.html` (6 calls)

| Line | Current Legacy Call | Proposed Replacement Tag | Plain Icon | Size | Notes / Edge Cases |
| :--- | :--- | :--- | :--- | :--- | :--- |
| 23 | `{% show_icon label='Reports' icon='ti ti-md ti-bar-chart-alt' badge=object.num_reports %}` | `{% show_icon label='Reports' icon='bar-chart-alt' size='md' badge=object.num_reports %}` | `bar-chart-alt` | `md` | Clean standard migration |
| 26 | `{% show_icon label='Data' icon='ti ti-md ti-layout-grid3' badge=object.datasets.count %}` | `{% show_icon label='Data' icon='layout-grid3' size='md' badge=object.datasets.count %}` | `layout-grid3` | `md` | Clean standard migration |
| 29 | `{% show_icon label='History' icon='ti ti-md ti-timer' %}` | `{% show_icon label='History' icon='timer' size='md' %}` | `timer` | `md` | Clean standard migration |
| 33 | `{% show_icon label='Statistics' icon='ti ti-md ti-pulse' %}` | `{% show_icon label='Statistics' icon='pulse' size='md' %}` | `pulse` | `md` | Clean standard migration |
| 39 | `{% show_icon label='Download' icon='ti ti-md ti-download' %}` | `{% show_icon label='Download' icon='download' size='md' %}` | `download` | `md` | Clean standard migration |
| 45 | `{% show_icon label='Feedback' icon='ti ti-md ti-star' %}` | `{% show_icon label='Feedback' icon='star' size='md' %}` | `star` | `md` | Clean standard migration |

#### `basiclive/core/lims/templates/lims/details/shipment-base.html` (5 calls)

| Line | Current Legacy Call | Proposed Replacement Tag | Plain Icon | Size | Notes / Edge Cases |
| :--- | :--- | :--- | :--- | :--- | :--- |
| 18 | `{% show_icon icon="ti ti-lock" %}` | `{% show_icon icon="lock" %}` | `lock` | *(none)* | Clean standard migration |
| 31 | `{% show_icon label="Data" icon="ti ti-md ti-layout-grid3" badge=shipment.num_datasets %}` | `{% show_icon label="Data" icon="layout-grid3" size='md' badge=shipment.num_datasets %}` | `layout-grid3` | `md` | Clean standard migration |
| 36 | `{% show_icon label="Reports" icon="ti ti-md ti-bar-chart-alt" badge=shipment.num_reports %}` | `{% show_icon label="Reports" icon="bar-chart-alt" size='md' badge=shipment.num_reports %}` | `bar-chart-alt` | `md` | Clean standard migration |
| 41 | `{% show_icon label="Requests" icon="ti ti-md ti-layout-accordion-list" %}` | `{% show_icon label="Requests" icon="layout-accordion-list" size='md' %}` | `layout-accordion-list` | `md` | Clean standard migration |
| 46 | `{% show_icon label='Samples' icon='ti ti-md ti-view-list-alt' %}` | `{% show_icon label='Samples' icon='view-list-alt' size='md' %}` | `view-list-alt` | `md` | Clean standard migration |

#### `basiclive/core/lims/templates/lims/details/shipment-list-item.html` (10 calls)

| Line | Current Legacy Call | Proposed Replacement Tag | Plain Icon | Size | Notes / Edge Cases |
| :--- | :--- | :--- | :--- | :--- | :--- |
| 6 | `{% show_icon label='DRAFT' icon='ti ti-sm ti-clipboard' tooltip='Draft' %}` | `{% show_icon label='DRAFT' icon='clipboard' size='sm' tooltip='Draft' %}` | `clipboard` | `sm` | Clean standard migration |
| 8 | `{% show_icon label=shipment.date_shipped|date:"M j"|upper icon='ti ti-sm ti-truck' tooltip='Incoming' %}` | `{% show_icon label=shipment.date_shipped|date:"M j"|upper icon='truck' size='sm' tooltip='Incoming' %}` | `truck` | `sm` | Clean standard migration |
| 10 | `{% show_icon label=shipment.date_shipped|date:"M j"|upper icon='ti ti-sm ti-location-pin' tooltip='On-site' %}` | `{% show_icon label=shipment.date_shipped|date:"M j"|upper icon='location-pin' size='sm' tooltip='On-site' %}` | `location-pin` | `sm` | Clean standard migration |
| 12 | `{% show_icon label=shipment.date_returned|date:"M j"|upper icon='ti ti-sm ti-check-box' tooltip='Returned' %}` | `{% show_icon label=shipment.date_returned|date:"M j"|upper icon='check-box' size='sm' tooltip='Returned' %}` | `check-box` | `sm` | Clean standard migration |
| 14 | `{% show_icon label=shipment.date_returned|date:"M j"|upper icon='ti ti-sm ti-archive' tooltip='Archived' %}` | `{% show_icon label=shipment.date_returned|date:"M j"|upper icon='archive' size='sm' tooltip='Archived' %}` | `archive` | `sm` | Clean standard migration |
| 34 | `{% show_icon label='Data' badge=shipment.data_count icon='ti ti-sm ti-layout-grid3' color='primary' %}` | `{% show_icon label='Data' icon='layout-grid3' size='sm' badge=shipment.data_count color='primary' %}` | `layout-grid3` | `sm` | Clean standard migration |
| 37 | `{% show_icon label='Reports' badge=shipment.report_count icon='ti ti-sm ti-bar-chart-alt' color='primary' %}` | `{% show_icon label='Reports' icon='bar-chart-alt' size='sm' badge=shipment.report_count color='primary' %}` | `bar-chart-alt` | `sm` | Clean standard migration |
| 43 | `{% show_icon label='Return' icon='ti ti-sm ti-location-arrow' %}` | `{% show_icon label='Return' icon='location-arrow' size='sm' %}` | `location-arrow` | `sm` | Clean standard migration |
| 47 | `{% show_icon label='Receive' icon='ti ti-sm ti-shopping-cart-full' %}` | `{% show_icon label='Receive' icon='shopping-cart-full' size='sm' %}` | `shopping-cart-full` | `sm` | Clean standard migration |
| 52 | `{% show_icon label='Send' icon='ti ti-sm ti-location-arrow' %}` | `{% show_icon label='Send' icon='location-arrow' size='sm' %}` | `location-arrow` | `sm` | Clean standard migration |

#### `basiclive/core/lims/templates/lims/details/shipment.html` (1 call)

| Line | Current Legacy Call | Proposed Replacement Tag | Plain Icon | Size | Notes / Edge Cases |
| :--- | :--- | :--- | :--- | :--- | :--- |
| 25 | `{% show_icon icon="ti ti-lock" %}` | `{% show_icon icon="lock" %}` | `lock` | *(none)* | Clean standard migration |

#### `basiclive/core/lims/templates/lims/details/user-list.html` (1 call)

| Line | Current Legacy Call | Proposed Replacement Tag | Plain Icon | Size | Notes / Edge Cases |
| :--- | :--- | :--- | :--- | :--- | :--- |
| 6 | `{% show_icon label="Add Account" icon="ti ti-md ti-plus" %}` | `{% show_icon label="Add Account" icon="plus" size='md' %}` | `plus` | `md` | Clean standard migration |

#### `basiclive/core/lims/templates/lims/details/user.html` (7 calls)

| Line | Current Legacy Call | Proposed Replacement Tag | Plain Icon | Size | Notes / Edge Cases |
| :--- | :--- | :--- | :--- | :--- | :--- |
| 24 | `{% show_icon label="Data" icon="ti ti-md ti-layout-grid3" badge=object.datasets.count %}` | `{% show_icon label="Data" icon="layout-grid3" size='md' badge=object.datasets.count %}` | `layout-grid3` | `md` | Clean standard migration |
| 27 | `{% show_icon label="Reports" icon="ti ti-md ti-bar-chart-alt" badge=object.reports.count %}` | `{% show_icon label="Reports" icon="bar-chart-alt" size='md' badge=object.reports.count %}` | `bar-chart-alt` | `md` | Clean standard migration |
| 30 | `{% show_icon label="Sessions" icon="ti ti-md ti-calendar" badge=object.sessions.count %}` | `{% show_icon label="Sessions" icon="calendar" size='md' badge=object.sessions.count %}` | `calendar` | `md` | Clean standard migration |
| 35 | `{% show_icon label="Labels" icon="ti ti-md ti-tag" %}` | `{% show_icon label="Labels" icon="tag" size='md' %}` | `tag` | `md` | Clean standard migration |
| 38 | `{% show_icon label="Edit" icon="ti ti-md ti-pencil-alt" %}` | `{% show_icon label="Edit" icon="pencil-alt" size='md' %}` | `pencil-alt` | `md` | Clean standard migration |
| 41 | `{% show_icon label="Reset Key" icon="ti ti-md ti-key" %}` | `{% show_icon label="Reset Key" icon="key" size='md' %}` | `key` | `md` | Clean standard migration |
| 85 | `{% show_icon icon="ti ti-key ti-sm" %}` | `{% show_icon icon="key" size='sm' %}` | `key` | `sm` | Size token `ti-sm` positioned at end of icon string in legacy call. |

#### `basiclive/core/lims/templates/lims/forms/container-spreadsheet.html` (2 calls)

| Line | Current Legacy Call | Proposed Replacement Tag | Plain Icon | Size | Notes / Edge Cases |
| :--- | :--- | :--- | :--- | :--- | :--- |
| 34 | `{% show_icon icon="ti ti-trash" %}` | `{% show_icon icon="trash" %}` | `trash` | *(none)* | Clean standard migration |
| 45 | `{% show_icon icon="ti ti-info-alt ti-md" %}` | `{% show_icon icon="info-alt" size='md' %}` | `info-alt` | `md` | Size token `ti-md` positioned at end of icon string in legacy call. |

#### `basiclive/core/lims/templates/lims/forms/seat-samples.html` (2 calls)

| Line | Current Legacy Call | Proposed Replacement Tag | Plain Icon | Size | Notes / Edge Cases |
| :--- | :--- | :--- | :--- | :--- | :--- |
| 13 | `{% show_icon icon="ti ti-paint-bucket ti-md" %}` | `{% show_icon icon="paint-bucket" size='md' %}` | `paint-bucket` | `md` | Size token `ti-md` positioned at end of icon string in legacy call. |
| 77 | `{% show_icon icon="ti ti-info-alt ti-md" %}` | `{% show_icon icon="info-alt" size='md' %}` | `info-alt` | `md` | Size token `ti-md` positioned at end of icon string in legacy call. |

#### `basiclive/core/lims/templates/lims/list-plots.html` (1 call)

| Line | Current Legacy Call | Proposed Replacement Tag | Plain Icon | Size | Notes / Edge Cases |
| :--- | :--- | :--- | :--- | :--- | :--- |
| 27 | `{% show_icon label='List' icon='ti ti-md ti-list' %}` | `{% show_icon label='List' icon='list' size='md' %}` | `list` | `md` | Clean standard migration |

#### `basiclive/core/lims/templates/lims/list.html` (1 call)

| Line | Current Legacy Call | Proposed Replacement Tag | Plain Icon | Size | Notes / Edge Cases |
| :--- | :--- | :--- | :--- | :--- | :--- |
| 11 | `{% show_icon label='Stats' icon='ti ti-md ti-pulse' %}` | `{% show_icon label='Stats' icon='pulse' size='md' %}` | `pulse` | `md` | Clean standard migration |

#### `basiclive/core/lims/templates/lims/navs.html` (8 calls)

| Line | Current Legacy Call | Proposed Replacement Tag | Plain Icon | Size | Notes / Edge Cases |
| :--- | :--- | :--- | :--- | :--- | :--- |
| 11 | `{% show_icon icon="ti ti-unlock" %}` | `{% show_icon icon="unlock" %}` | `unlock` | *(none)* | Clean standard migration |
| 17 | `{% show_icon icon="ti ti-home" %}` | `{% show_icon icon="home" %}` | `home` | *(none)* | Clean standard migration |
| 23 | `{% show_icon icon="ti ti-book" %}` | `{% show_icon icon="book" %}` | `book` | *(none)* | Clean standard migration |
| 30 | `{% show_icon icon="ti ti-list" %}` | `{% show_icon icon="list" %}` | `list` | *(none)* | Clean standard migration |
| 56 | `{% show_icon icon="ti ti-user" %}` | `{% show_icon icon="user" %}` | `user` | *(none)* | Clean standard migration |
| 62 | `{% show_icon icon="ti ti-shine" %}` | `{% show_icon icon="shine" %}` | `shine` | *(none)* | Clean standard migration |
| 65 | `{% show_icon icon="ti ti-drupal" %}` | `{% show_icon icon="drupal" %}` | `drupal` | *(none)* | Clean standard migration |
| 68 | `{% show_icon icon="ti ti-widget" %}` | `{% show_icon icon="widget" %}` | `widget` | *(none)* | Clean standard migration |

#### `basiclive/core/lims/templates/lims/tools-base.html` (2 calls)

| Line | Current Legacy Call | Proposed Replacement Tag | Plain Icon | Size | Notes / Edge Cases |
| :--- | :--- | :--- | :--- | :--- | :--- |
| 5 | `{% show_icon label='Edit' icon='ti ti-md ti-pencil-alt' %}` | `{% show_icon label='Edit' icon='pencil-alt' size='md' %}` | `pencil-alt` | `md` | Clean standard migration |
| 8 | `{% show_icon label='Delete' icon='ti ti-md ti-trash' %}` | `{% show_icon label='Delete' icon='trash' size='md' %}` | `trash` | `md` | Clean standard migration |

#### `basiclive/core/lims/templates/lims/tools-shipment-edit.html` (5 calls)

| Line | Current Legacy Call | Proposed Replacement Tag | Plain Icon | Size | Notes / Edge Cases |
| :--- | :--- | :--- | :--- | :--- | :--- |
| 4 | `{% show_icon icon="ti ti-md ti-package" label="Containers" %}` | `{% show_icon label="Containers" icon="package" size='md' %}` | `package` | `md` | Clean standard migration |
| 7 | `{% show_icon icon="ti ti-md ti-layout-accordion-list" label="Groups" %}` | `{% show_icon label="Groups" icon="layout-accordion-list" size='md' %}` | `layout-accordion-list` | `md` | Clean standard migration |
| 20 | `{% show_icon label='Samples' icon='ti ti-md ti-paint-bucket' badge="+" color="primary" %}` | `{% show_icon label='Samples' icon='paint-bucket' size='md' badge="+" color="primary" %}` | `paint-bucket` | `md` | Clean standard migration |
| 22 | `{% show_icon label='Samples' icon='ti ti-md ti-paint-bucket' color="primary" %}` | `{% show_icon label='Samples' icon='paint-bucket' size='md' color="primary" %}` | `paint-bucket` | `md` | Specified `color="primary"` without `badge` (vestigial in legacy template; had no visual effect). |
| 28 | `{% show_icon label='Done' icon='ti ti-md ti-check' %}` | `{% show_icon label='Done' icon='check' size='md' %}` | `check` | `md` | Clean standard migration |

#### `basiclive/core/lims/templates/lims/tools-shipment.html` (15 calls)

| Line | Current Legacy Call | Proposed Replacement Tag | Plain Icon | Size | Notes / Edge Cases |
| :--- | :--- | :--- | :--- | :--- | :--- |
| 7 | `{% show_icon label='Requests' icon='ti ti-md ti-layout-accordion-list' %}` | `{% show_icon label='Requests' icon='layout-accordion-list' size='md' %}` | `layout-accordion-list` | `md` | Clean standard migration |
| 11 | `{% show_icon label='Samples' icon='ti ti-md ti-view-list-alt' %}` | `{% show_icon label='Samples' icon='view-list-alt' size='md' %}` | `view-list-alt` | `md` | Clean standard migration |
| 14 | `{% show_icon label='Data' icon='ti ti-md ti-layout-grid3' badge=shipment.num_datasets color='info' %}` | `{% show_icon label='Data' icon='layout-grid3' size='md' badge=shipment.num_datasets color='info' %}` | `layout-grid3` | `md` | Clean standard migration |
| 17 | `{% show_icon label='Reports' icon='ti ti-md ti-bar-chart-alt' badge=shipment.num_reports color='info' %}` | `{% show_icon label='Reports' icon='bar-chart-alt' size='md' badge=shipment.num_reports color='info' %}` | `bar-chart-alt` | `md` | Clean standard migration |
| 26 | `{% show_icon label='Delete' icon='ti ti-md ti-trash' %}` | `{% show_icon label='Delete' icon='trash' size='md' %}` | `trash` | `md` | Clean standard migration |
| 29 | `{% show_icon label='Edit' icon='ti ti-md ti-pencil-alt' %}` | `{% show_icon label='Edit' icon='pencil-alt' size='md' %}` | `pencil-alt` | `md` | Clean standard migration |
| 32 | `{% show_icon label='Send' icon='ti ti-md ti-location-arrow' %}` | `{% show_icon label='Send' icon='location-arrow' size='md' %}` | `location-arrow` | `md` | Clean standard migration |
| 37 | `{% show_icon label='Recall' icon='ti ti-md ti-control-backward' %}` | `{% show_icon label='Recall' icon='control-backward' size='md' %}` | `control-backward` | `md` | Clean standard migration |
| 42 | `{% show_icon label='Labels' icon='ti ti-md ti-tag' %}` | `{% show_icon label='Labels' icon='tag' size='md' %}` | `tag` | `md` | Clean standard migration |
| 49 | `{% show_icon label='Labels' icon='ti ti-md ti-tag' %}` | `{% show_icon label='Labels' icon='tag' size='md' %}` | `tag` | `md` | Clean standard migration |
| 52 | `{% show_icon label='Comment' icon='ti ti-md ti-comment-alt' %}` | `{% show_icon label='Comment' icon='comment-alt' size='md' %}` | `comment-alt` | `md` | Clean standard migration |
| 56 | `{% show_icon label='Receive' icon='ti ti-md ti-shopping-cart-full' %}` | `{% show_icon label='Receive' icon='shopping-cart-full' size='md' %}` | `shopping-cart-full` | `md` | Clean standard migration |
| 60 | `{% show_icon label='Return' icon='ti ti-md ti-location-arrow' %}` | `{% show_icon label='Return' icon='location-arrow' size='md' %}` | `location-arrow` | `md` | Clean standard migration |
| 64 | `{% show_icon label='Revise' icon='ti ti-md ti-pencil' %}` | `{% show_icon label='Revise' icon='pencil' size='md' %}` | `pencil` | `md` | Clean standard migration |
| 68 | `{% show_icon label='Recall' icon='ti ti-md ti-control-backward' %}` | `{% show_icon label='Recall' icon='control-backward' size='md' %}` | `control-backward` | `md` | Clean standard migration |

#### `basiclive/core/lims/templates/lims/tools-user.html` (4 calls)

| Line | Current Legacy Call | Proposed Replacement Tag | Plain Icon | Size | Notes / Edge Cases |
| :--- | :--- | :--- | :--- | :--- | :--- |
| 7 | `{% show_icon label='Sessions' icon='ti ti-md ti-calendar' %}` | `{% show_icon label='Sessions' icon='calendar' size='md' %}` | `calendar` | `md` | Clean standard migration |
| 11 | `{% show_icon label="Schedule" icon="ti ti-md ti-time" %}` | `{% show_icon label="Schedule" icon="time" size='md' %}` | `time` | `md` | Clean standard migration |
| 16 | `{% show_icon label='My Stats' icon='ti ti-md ti-pulse' %}` | `{% show_icon label='My Stats' icon='pulse' size='md' %}` | `pulse` | `md` | Clean standard migration |
| 21 | `{% show_icon label='My Profile' icon='ti ti-md ti-user' %}` | `{% show_icon label='My Profile' icon='user' size='md' %}` | `user` | `md` | Clean standard migration |

#### `basiclive/core/lims/templates/lims/warning.html` (1 call)

| Line | Current Legacy Call | Proposed Replacement Tag | Plain Icon | Size | Notes / Edge Cases |
| :--- | :--- | :--- | :--- | :--- | :--- |
| 14 | `{% show_icon icon="ti ti-lock" %}` | `{% show_icon icon="lock" %}` | `lock` | *(none)* | Clean standard migration |

### Schedule (`basiclive/core/schedule`) — 17 Call Sites

#### `basiclive/core/schedule/templates/schedule/beamline-support.html` (3 calls)

| Line | Current Legacy Call | Proposed Replacement Tag | Plain Icon | Size | Notes / Edge Cases |
| :--- | :--- | :--- | :--- | :--- | :--- |
| 16 | `{% show_icon icon='ti ti-sm ti-pencil' %}` | `{% show_icon icon='pencil' size='sm' %}` | `pencil` | `sm` | Clean standard migration |
| 19 | `{% show_icon icon='ti ti-sm ti-trash' %}` | `{% show_icon icon='trash' size='sm' %}` | `trash` | `sm` | Clean standard migration |
| 24 | `{% show_icon icon='ti ti-md ti-user' %}` | `{% show_icon icon='user' size='md' %}` | `user` | `md` | Clean standard migration |

#### `basiclive/core/schedule/templates/schedule/beamtime-list-item.html` (3 calls)

| Line | Current Legacy Call | Proposed Replacement Tag | Plain Icon | Size | Notes / Edge Cases |
| :--- | :--- | :--- | :--- | :--- | :--- |
| 36 | `{% show_icon label=session.name|truncatechars:6 icon='ti ti-md ti-calendar' color='info' %}` | `{% show_icon label=session.name|truncatechars:6 icon='calendar' size='md' color='info' %}` | `calendar` | `md` | Specified `color='info'` without `badge` (vestigial in legacy template; had no visual effect). |
| 41 | `{% show_icon label='Info' icon='ti ti-md ti-info-alt' color='info' %}` | `{% show_icon label='Info' icon='info-alt' size='md' color='info' %}` | `info-alt` | `md` | Specified `color='info'` without `badge` (vestigial in legacy template; had no visual effect). |
| 47 | `{% show_icon label='Support' icon='ti ti-md ti-headphone-alt' %}` | `{% show_icon label='Support' icon='headphone-alt' size='md' %}` | `headphone-alt` | `md` | Clean standard migration |

#### `basiclive/core/schedule/templates/schedule/beamtime.html` (5 calls)

| Line | Current Legacy Call | Proposed Replacement Tag | Plain Icon | Size | Notes / Edge Cases |
| :--- | :--- | :--- | :--- | :--- | :--- |
| 9 | `{% show_icon icon='ti ti-sm ti-check-box' %}` | `{% show_icon icon='check-box' size='sm' %}` | `check-box` | `sm` | Clean standard migration |
| 11 | `{% show_icon icon='ti ti-sm ti-alert text-danger' %}` | `{% show_icon icon='alert' size='sm' extra_class='text-danger' %}` | `alert` | `sm` | Compound styling class `text-danger` extracted to `extra_class`. |
| 13 | `{% show_icon icon='ti ti-sm ti-email' %}` | `{% show_icon icon='email' size='sm' %}` | `email` | `sm` | Clean standard migration |
| 22 | `{% show_icon icon='ti ti-sm ti-pencil' %}` | `{% show_icon icon='pencil' size='sm' %}` | `pencil` | `sm` | Clean standard migration |
| 25 | `{% show_icon icon='ti ti-sm ti-trash' %}` | `{% show_icon icon='trash' size='sm' %}` | `trash` | `sm` | Clean standard migration |

#### `basiclive/core/schedule/templates/schedule/schedule.html` (2 calls)

| Line | Current Legacy Call | Proposed Replacement Tag | Plain Icon | Size | Notes / Edge Cases |
| :--- | :--- | :--- | :--- | :--- | :--- |
| 24 | `{% show_icon label='Usage' icon='ti ti-md ti-pie-chart' %}` | `{% show_icon label='Usage' icon='pie-chart' size='md' %}` | `pie-chart` | `md` | Clean standard migration |
| 27 | `{% show_icon label='Emails' icon='ti ti-md ti-email' %}` | `{% show_icon label='Emails' icon='email' size='md' %}` | `email` | `md` | Clean standard migration |

#### `basiclive/core/schedule/templates/schedule/week.html` (4 calls)

| Line | Current Legacy Call | Proposed Replacement Tag | Plain Icon | Size | Notes / Edge Cases |
| :--- | :--- | :--- | :--- | :--- | :--- |
| 38 | `{% show_icon icon="ti ti-md ti-angle-left" %}` | `{% show_icon icon="angle-left" size='md' %}` | `angle-left` | `md` | Clean standard migration |
| 41 | `{% show_icon icon="ti ti-md ti-calendar" %}` | `{% show_icon icon="calendar" size='md' %}` | `calendar` | `md` | Clean standard migration |
| 44 | `{% show_icon icon="ti ti-md ti-angle-right" %}` | `{% show_icon icon="angle-right" size='md' %}` | `angle-right` | `md` | Clean standard migration |
| 47 | `{% show_icon icon="ti ti-md ti-home" %}` | `{% show_icon icon="home" size='md' %}` | `home` | `md` | Clean standard migration |

### Notebooks (`basiclive/core/notebooks`) — 7 Call Sites

#### `basiclive/core/notebooks/templates/notebooks/entries/entry.html` (3 calls)

| Line | Current Legacy Call | Proposed Replacement Tag | Plain Icon | Size | Notes / Edge Cases |
| :--- | :--- | :--- | :--- | :--- | :--- |
| 18 | `{% show_icon icon="ti ti-md ti-pencil" %}` | `{% show_icon icon="pencil" size='md' %}` | `pencil` | `md` | Clean standard migration |
| 21 | `{% show_icon icon="ti ti-md ti-tag" %}` | `{% show_icon icon="tag" size='md' %}` | `tag` | `md` | Clean standard migration |
| 24 | `{% show_icon icon="ti ti-md ti-trash" %}` | `{% show_icon icon="trash" size='md' %}` | `trash` | `md` | Clean standard migration |

#### `basiclive/core/notebooks/templates/notebooks/notebook.html` (3 calls)

| Line | Current Legacy Call | Proposed Replacement Tag | Plain Icon | Size | Notes / Edge Cases |
| :--- | :--- | :--- | :--- | :--- | :--- |
| 23 | `{% show_icon icon="ti ti-calendar ti-md" label="Calendar" %}` | `{% show_icon label="Calendar" icon="calendar" size='md' %}` | `calendar` | `md` | Size token `ti-md` positioned at end of icon string in legacy call. |
| 27 | `{% show_icon icon="ti ti-settings ti-md" label="Settings" %}` | `{% show_icon label="Settings" icon="settings" size='md' %}` | `settings` | `md` | Size token `ti-md` positioned at end of icon string in legacy call. |
| 39 | `{% show_icon icon=entry_type.icon label=entry_type.name|title %}` | `{% show_icon label=entry_type.name|title icon=entry_type.icon size='md' %}` | `entry_type.icon` | `md` | Dynamic model property (`entry_type.icon` returns `ti-md entry-selector-...`). IconBackend requires canonical alias. |

#### `basiclive/core/notebooks/templates/notebooks/notebook_list.html` (1 call)

| Line | Current Legacy Call | Proposed Replacement Tag | Plain Icon | Size | Notes / Edge Cases |
| :--- | :--- | :--- | :--- | :--- | :--- |
| 17 | `{% show_icon icon="ti ti-plus ti-md" label="Notebook" %}` | `{% show_icon label="Notebook" icon="plus" size='md' %}` | `plus` | `md` | Size token `ti-md` positioned at end of icon string in legacy call. |

### Access Control / ACL (`basiclive/core/acl`) — 5 Call Sites

#### `basiclive/core/acl/templates/acl/connection-list-item.html` (4 calls)

| Line | Current Legacy Call | Proposed Replacement Tag | Plain Icon | Size | Notes / Edge Cases |
| :--- | :--- | :--- | :--- | :--- | :--- |
| 11 | `{% show_icon label='Support' icon='ti ti-sm ti-headphone-alt' %}` | `{% show_icon label='Support' icon='headphone-alt' size='sm' %}` | `headphone-alt` | `sm` | Clean standard migration |
| 50 | `{% show_icon label=access|upper icon='ti ti-sm ti-rss-alt' %}` | `{% show_icon label=access|upper icon='rss-alt' size='sm' %}` | `rss-alt` | `sm` | Clean standard migration |
| 52 | `{% show_icon label=access|upper badge=conn|length icon='ti ti-sm ti-rss-alt' %}` | `{% show_icon label=access|upper icon='rss-alt' size='sm' badge=conn|length %}` | `rss-alt` | `sm` | Clean standard migration |
| 58 | `{% show_icon label=session.start.date|date:"M j"|upper icon='ti ti-sm ti-calendar' %}` | `{% show_icon label=session.start.date|date:"M j"|upper icon='calendar' size='sm' %}` | `calendar` | `sm` | Clean standard migration |

#### `basiclive/core/acl/templates/acl/tools-access.html` (1 call)

| Line | Current Legacy Call | Proposed Replacement Tag | Plain Icon | Size | Notes / Edge Cases |
| :--- | :--- | :--- | :--- | :--- | :--- |
| 4 | `{% show_icon label='Connections' icon='ti ti-md ti-rss-alt' %}` | `{% show_icon label='Connections' icon='rss-alt' size='md' %}` | `rss-alt` | `md` | Clean standard migration |

### CRM (`basiclive/core/crm`) — 5 Call Sites

#### `basiclive/core/crm/templates/crm/tools-support.html` (5 calls)

| Line | Current Legacy Call | Proposed Replacement Tag | Plain Icon | Size | Notes / Edge Cases |
| :--- | :--- | :--- | :--- | :--- | :--- |
| 4 | `{% show_icon label='Areas' icon='ti ti-md ti-target' %}` | `{% show_icon label='Areas' icon='target' size='md' %}` | `target` | `md` | Clean standard migration |
| 7 | `{% show_icon label='Support' icon='ti ti-md ti-headphone-alt' %}` | `{% show_icon label='Support' icon='headphone-alt' size='md' %}` | `headphone-alt` | `md` | Clean standard migration |
| 10 | `{% show_icon label='Feedback' icon='ti ti-md ti-star' %}` | `{% show_icon label='Feedback' icon='star' size='md' %}` | `star` | `md` | Clean standard migration |
| 14 | `{% show_icon label='Support' icon='ti ti-md ti-headphone-alt' badge='+' color='primary' %}` | `{% show_icon label='Support' icon='headphone-alt' size='md' badge='+' color='primary' %}` | `headphone-alt` | `md` | Clean standard migration |
| 17 | `{% show_icon label='New Area' icon='ti ti-md ti-target' badge='+' color='primary' %}` | `{% show_icon label='New Area' icon='target' size='md' badge='+' color='primary' %}` | `target` | `md` | Clean standard migration |

### Publications (`basiclive/core/publications`) — 5 Call Sites

#### `basiclive/core/publications/templates/publications/tools.html` (5 calls)

| Line | Current Legacy Call | Proposed Replacement Tag | Plain Icon | Size | Notes / Edge Cases |
| :--- | :--- | :--- | :--- | :--- | :--- |
| 4 | `{% show_icon label='Publications' icon='ti ti-md ti-layout-list-post' %}` | `{% show_icon label='Publications' icon='layout-list-post' size='md' %}` | `layout-list-post` | `md` | Clean standard migration |
| 7 | `{% show_icon label='PDB Entries' icon='ti ti-md ti-star' %}` | `{% show_icon label='PDB Entries' icon='star' size='md' %}` | `star` | `md` | Clean standard migration |
| 10 | `{% show_icon label='Metrics' icon='ti ti-md ti-pulse' %}` | `{% show_icon label='Metrics' icon='pulse' size='md' %}` | `pulse` | `md` | Clean standard migration |
| 13 | `{% show_icon label='Subject Areas' icon='ti ti-md ti-bag' %}` | `{% show_icon label='Subject Areas' icon='bag' size='md' %}` | `bag` | `md` | Clean standard migration |
| 16 | `{% show_icon label='Journals' icon='ti ti-md ti-book' %}` | `{% show_icon label='Journals' icon='book' size='md' %}` | `book` | `md` | Clean standard migration |

## Recommendations for Downstream Work Packages

This audit provides concrete inputs for the remaining work packages in Map [#110](https://github.com/michel4j/basic-live/issues/110):

1. **Issue [#112](https://github.com/michel4j/basic-live/issues/112) (`BaseIconBackend` and `ThemifyBackend`)**:
   - Ensure `ThemifyBackend` implements the hybrid fallback `{prefix}-{name}` (i.e. `ti-{name}`).
   - Populate the canonical mapping dictionary with aliases for all 58 icons cataloged above, notably aliases like `edit -> ti-pencil-alt`, `support -> ti-headphone-alt`, `activity -> ti-pulse`, `warning -> ti-alert`, `mail -> ti-email`, `clock -> ti-time`.
   - Register notebooks aliases (`entry-selector-*`) mapping to `.mi .mi-...` or `.entry-selector-*` CSS definitions.
2. **Issue [#113](https://github.com/michel4j/basic-live/issues/113) (`basiclive.scss` sizing classes)**:
   - The 2 active size tokens in call sites are `sm` (27 calls) and `md` (115 calls). Provide `.bl-icon-xs`, `.bl-icon-sm`, `.bl-icon-md`, `.bl-icon-lg`, `.bl-icon-xl` utility classes while preserving backwards compatibility aliases `.ti-sm`, `.ti-md`, etc.
3. **Issue [#114](https://github.com/michel4j/basic-live/issues/114) (`show_icon` template tag & `{% show_icon_css %}`)**:
   - Update `show_icon` signature to accept `size=None` and `extra_class=""`.
   - Update `lims/components/icon-info.html` to invoke the active backend's `get_css_classes(icon, size, extra_class)`.
   - Clarify behavior when `color` is provided without `badge` (either render `text-{{ color }}` on the icon or ignore).
4. **Issue [#115](https://github.com/michel4j/basic-live/issues/115) (Core LIMS migration)**:
   - Migrate the 126 call sites across 37 core LIMS templates strictly following the catalog mappings in Section 4.1.
5. **Issue [#116](https://github.com/michel4j/basic-live/issues/116) (ACL, CRM, Schedule, Notebooks, Publications migration)**:
   - Migrate the 39 call sites across the remaining 12 templates in `acl` (5), `crm` (5), `schedule` (17), `notebooks` (7), and `publications` (5) following Sections 4.2–4.6.
6. **Issue [#117](https://github.com/michel4j/basic-live/issues/117) (`render_icon` helper & Python forms)**:
   - Modernize Python form definitions in `basiclive/core/lims/forms.py` using `render_icon(icon, size, extra_class)`.

