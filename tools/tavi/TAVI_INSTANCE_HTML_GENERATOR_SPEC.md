# Tavi instance metadata to static HTML Phase 1 specification

## Purpose and status

Historical logical script name: `tools/tavi/tavi_inst_json_to_html.py`. That local implementation is retired and absent from the current Canonical set. This document retains its technical contract and historical verification scope; it is not an installation or execution guide for an available local tool. Published static HTML demonstrations remain distinct from local HTML generation and from formal XBRL/Tavi validation.

The viewer generates all data and CSS in Python. Its left Properties pane has two native radio-controlled CSS tabs: Table Template (initial) and Tavi Taxonomy. Its right pane shows a literal CSV transpose. No Concept/Dimension/Cube/Network meaning, row-class reconstruction, fact selection or linked Properties is implemented.

## Inputs and exact source ranges

One input entry point: `--metadata`. One output: `--output`. There are no CSV, template, taxonomy or browser-fetch overrides. Both examples use the same code regardless of filename.

Case A is Canonical `tavi-inst.json`: `tables.accountingEntries.template` selects `/tableTemplates/accountingEntries` in that metadata file. Case B is Canonical `tavi-inst-hmd-view.json`: `tables.journalEntriesSingleAccount.template` selects `/tableTemplates/journalEntriesSingleAccount`. The templates are inline objects in instance metadata, not independent physical JSON files and not their referenced taxonomies. The enclosing metadata file is the Table Template source file; its selected value span is the displayed source range. No alternate file or re-serialised metadata is used.

The exact object span begins at the original opening `{` and ends immediately after the matching `}`. A JSON lexical decoder records these character offsets without altering the text. All keys, values, order, indentation, whitespace, arrays and interior newlines in that span remain verbatim. The `tableTemplates` container, other templates and unrelated metadata are outside the selected span. The HTML pre element records the source offsets and selected template ID. These are zero-based character offsets, not byte offsets. Source bytes/SHA are recorded separately.

Taxonomy selection uses `documentInfo.taxonomy`: exactly one explicit local JSON reference. Case A selects `canonical/tavi-poc/taxonomy/tavi-tax.json`; Case B selects the registered Single Account Date r2 view taxonomy under `canonical/tavi-poc/profiles/single-account-date-r2/taxonomy/`. The full UTF-8 text of that actual file is displayed unchanged. Parsing checks JSON syntax/duplicate keys only; it does not interpret taxonomy definitions.

CSV selection uses each `tables.<id>.url`, relative to the metadata directory. References must be local files; network URLs, fragments and query strings are rejected. URI percent-encoded path characters are decoded. No file search, Full-v3 substitution or missing-file fallback exists. The two examples resolve to the same shared `tavi-inst.csv`.

## Supported structure and stop conditions

The implemented input contract is the verified inline-metadata structure with explicit tables and template IDs. Multiple explicitly named tables are rendered in metadata order, each with its own selected template; a reference must resolve uniquely. Exactly one taxonomy JSON must be selected. An external/extended/composite template schema without a verified source-resolution rule is rejected with HOLD and exit 2, rather than guessed. Standalone external templates and taxonomy-hosted templates are not assumed or invented; the two authorised cases do not use them.

Other HOLD conditions include missing metadata/CSV/taxonomy, duplicate JSON keys, invalid JSON/UTF-8, non-object template, missing template reference, empty CSV/header and ragged CSV records. All inputs are read before output creation. Existing output files are refused to protect previous artefacts. The output must be `.html` and cannot overwrite metadata or CSV.

## CSV and transpose

The standard CSV reader uses `newline=''` and UTF-8 with input BOM tolerance. Values remain strings: leading zeros, decimals, dates, multiline cells, empty strings and repeated headers are preserved. No DictReader or numerical/date conversion is used. Missing cells in ragged rows are not silently replaced by empty strings.

For N fields and R data records, the displayed body has N rows and R+1 columns, including Field. The header has Field plus Record 1 through Record R. Header-only input produces N field rows with no data cells; it does not create facts or populated records. Each CSV column becomes one distinct HTML row, even if names repeat.

Positions use one-based CSV column numbers and one-based logical data-record numbers (excluding the header), not physical line numbers when a cell contains embedded newlines. `data-csv-column`, `data-csv-data-row`, `data-html-row` and `data-html-column` record the mapping; Field occupies HTML column 1 and record R occupies R+1. These attributes contain no Concept/Dimension inference.

## HTML, tabs and text safety

Both panes scroll independently in both directions as needed. Each left tab has its own scroll region. Two same-name radio inputs and CSS `:checked` selectors control visibility; Table Template is checked initially. Labels activate the native controls by mouse or keyboard. Switching does not replace, filter or modify the right table.

HTML text and attributes are escaped, including JSON/CSV content. Carriage returns are emitted as character references so HTML newline normalisation cannot discard them. Preformatted monospace source is not pretty-printed, trimmed or reordered. CSV cells preserve whitespace with CSS. Empty cells have empty text, not substitute markers.

The document contains inline CSS and all data. It has no script, event handler, external stylesheet, browser fetch, image, library or taxonomy/CSV request. A restrictive content policy disables scripts and connections. It can be opened as a standalone file or hosted later as a static GitHub Pages artefact. Publishing is outside scope.

## CLI and verification

The historical interface accepted `--metadata` and `--output` for the Simple and HMD View examples described above. Runnable commands targeting the retired local script are intentionally omitted. The following paragraph describes historical verification, not tests to execute as a prerequisite for using the published static pages.

Case-specific static checks independently resolve metadata/template/taxonomy and compare decoded HTML sources with the exact input text. Shared CSV value/order/blank/transpose verification is performed once, then the equivalent rendered body is reused for the second case. Edge fixtures cover escaped markup, leading zeros, repeated column names, Unicode, CRLF, multiline values and invalid/ambiguous references. Browser checks use local HTML with page JavaScript disabled, inspect real tab switching and screenshots, and verify the right table remains unchanged. Browser automation code is QA only and is not included in generated HTML.

Historical source specifications: the existing Detailed Program Specification, Requirements Specification, Part 3 section 8, the Canonical registration ledger and Arelle `oim/Load.py` format declarations. Their original SHA values and exact input records are preserved in WORK evidence; that internal record is not an input required by the current public package. DOCX documents were read for technical content only; no layout acceptance, editing or TOC update is asserted.

Phase 2 is NOT STARTED. No canonical promotion, Arelle validation, B5 change or existing accepted-baseline change is authorised by this specification.
