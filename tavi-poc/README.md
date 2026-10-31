**English** | [日本語](README_ja.md)

# XBRL GL Next — Tavi proof of concept

Experimental discussion draft based on Tavi PWD 2026-09-01; formal conformance has not been established.

## Published scope

- [Journal Entry JSON](taxonomy/Tavi_JournalEntries_SingleAccount_Date_r2_candidate.json): the sole Tavi taxonomy, including its Table Template in `xbrlModel.tableTemplates`.
- [Journal Entry viewer](https://pontsoleil.github.io/XBRL_GL_Next/tavi-inst-hmd-view.html): the existing UI, tabs and nine-column CSV transpose, with the discussion-candidate sources in its source tabs.

The Simple, Full v3 and four-model taxonomies, Arelle patches and old-specification report metadata are withdrawn. Originals and historical evidence remain in WORK. Shared CSV data is retained; a standalone CSV is neither a complete xBRL-CSV report nor a verified PWD instance.

## Validation scope

The viewer is a static display, not a formal Tavi validator. JSON syntax, static display and earlier Arelle results do not establish PWD conformance. Part 5, the HMD and the source semantic model remain unchanged.
