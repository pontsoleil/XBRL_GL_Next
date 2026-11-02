**English** | [日本語](README_ja.md)

# XBRL GL Next — Tavi proof of concept

Experimental discussion draft based on Tavi PWD 2026-09-01. Formal Tavi conformance has not been established.

## Journal Entry PoC — current review files

The review set provides a three-cube Journal Entry example with two occurrence-key variants. These are discussion candidates and do not change the formal semantic model, HMD, or Part 5.

| Variant | Tavi taxonomy | Instance module | Structured Tidy Data CSV |
| --- | --- | --- | --- |
| Integer occurrence keys | [`tavi-tax.json`](taxonomy/tavi-tax.json) | [`tavi-ins.json`](instance/tavi-ins.json) | [`tavi-ins.csv`](instance/tavi-ins.csv) |
| UUIDv7 occurrence keys | [`tavi-uuid-tax.json`](taxonomy/tavi-uuid-tax.json) | [`tavi-uuid-ins.json`](instance/tavi-uuid-ins.json) | [`tavi-uuid-ins.csv`](instance/tavi-uuid-ins.csv) |

Each taxonomy includes its 18-column Table Template in `xbrlModel.tableTemplates`. Each corresponding CSV has 18 columns and seven occurrence records.

The Instance modules specify the taxonomy and CSV through `documentInfo.importMapping`, `xbrlModel.importedTaxonomies`, `factMaps`, `factSources`, and `documentInfo.sourceMappings`. Structural consistency of local references was checked, but native Tavi import resolution and fact reconstruction have **not** been verified. The review modules must not be described as formally conformant Tavi instances.

The independent [`tavi-schema.json`](taxonomy/tavi-schema.json) is a review-time structural validation resource. It is assigned externally to Tavi JSON documents; it is not embedded in them through validation-only `$schema` or `$ref` properties. Its status as an official XBRL International schema has not been established.

## Tavi Viewer

**[Open the common Tavi Viewer](https://pontsoleil.github.io/XBRL_GL_Next/viewer/tavi-viewer.html)**

[HTML source](viewer/tavi-viewer.html) · [JavaScript source](viewer/tavi-viewer.js)

The common viewer supports both listed review variants. Select an Instance JSON to display the corresponding Table Template, Tavi taxonomy and JSON Schema in the left-hand **Properties** tabs, and the **transposed Structured Tidy Data CSV** in the right-hand pane.

The viewer uses an explicit, hard-coded list of supported Instance–Taxonomy–CSV pairings in `tavi-viewer.js`. Although it loads the selected Instance JSON, it does **not** yet derive the file pairing from its `importMapping` and `sourceMappings`. GitHub repository discovery may list additional JSON files without establishing a supported pairing.

### Viewing locally

Serve the `tavi-poc/` directory over HTTP; do not rely on opening the HTML as a `file://` document. For example, from the directory's parent:

```shell
python -m http.server 8765 --bind 127.0.0.1
```

Open `http://127.0.0.1:8765/tavi-poc/viewer/tavi-viewer.html`. Keep `tavi-viewer.html` and `tavi-viewer.js` together, with `taxonomy/` and `instance/` at their repository-relative locations.

The viewer is for static source inspection and CSV presentation. It is not a JSON Schema validation engine, a native Tavi processor, or a semantic conformance validator.

## Historical scope and validation limits

The Simple, Full v3 and four-model taxonomies, Arelle patches and older report-metadata paths were withdrawn from the current published PoC. Originals and historical evidence remain in WORK. Historical materials or residual files must not be presented as currently supported instance formats.

The November 2, 2026 review publication completed Canonical registration, Official Git publication and push for the nine-file review set (seven additions and two existing files retained). JSON syntax, external Draft-07 structural validation, CSV/Table Template alignment, local references and Windows Chrome viewer display were checked for this review set. These checks do not establish Tavi PWD conformance, native import semantics, parent-occurrence constraints or fact reconstruction.
