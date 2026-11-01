**English** | [日本語](README_ja.md)

# XBRL GL Next — Tavi proof of concept

Experimental discussion draft based on Tavi PWD 2026-09-01; formal conformance has not been established.

## Published scope

This three-cube Journal Entry PoC precedes any formal semantic-model revision. The reused filename `tavi-tax.json` identifies this new PoC, not the withdrawn Simple taxonomy.

- [Journal Entry JSON](taxonomy/tavi-tax.json): the sole Tavi taxonomy, including its Table Template in `xbrlModel.tableTemplates`.
- [Structured Tidy Data CSV](instance/tavi-ins.csv): 18 columns and seven occurrence records.
- [Journal Entry viewer](https://pontsoleil.github.io/XBRL_GL_Next/tavi-inst-hmd-view.html): the existing UI, tabs and 18-column, seven-record CSV transpose, with the discussion-candidate sources in its source tabs.

The Simple, Full v3 and four-model taxonomies, Arelle patches and old-specification report metadata are withdrawn. Originals and historical evidence remain in WORK. Shared CSV data is retained; a standalone CSV is neither a complete xBRL-CSV report nor a verified PWD instance.

## Validation scope

The viewer is a static display, not a formal Tavi validator. JSON syntax, static display and earlier Arelle results do not establish PWD conformance. Part 5, the HMD and the source semantic model remain unchanged.
