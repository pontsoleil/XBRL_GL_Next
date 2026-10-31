**English** | [日本語](README_ja.md)

# Published taxonomy packages

The `taxonomy/` directory contains the independent Tuple and OIM packages derived from formal model-specific HMDs. The Journal Entry Tavi discussion draft is separately scoped under `tavi-poc/`. The common View-to-three-instance workflow remains a future development stage.



This directory contains published Tuple and OIM taxonomy packages.

## Tuple and OIM

- [`accounting-entries/`](accounting-entries/) — Accounting Entries (COR).
- [`business-transactions/`](business-transactions/) — Business Transactions (BTX).
- [`journal-entries/`](journal-entries/) — independently scoped journal-entry models.

Select the entry point for the intended model and binding. Do not combine independently generated DTS trees merely because they use similarly named concepts. Module namespaces use `https://www.xbrl.or.jp/taxonomy/xbrl-gl-next/{module}`; dates in filenames do not form part of these namespace URIs.

## Tavi JSON

Experimental discussion draft based on Tavi PWD 2026-09-01; formal conformance has not been established. The sole Tavi taxonomy is the [Journal Entry JSON](../tavi-poc/taxonomy/Tavi_JournalEntries_SingleAccount_Date_r2_candidate.json), with an embedded Table Template. Its [static viewer](https://pontsoleil.github.io/XBRL_GL_Next/tavi-inst-hmd-view.html) is not a conformance validator.

For provenance and publication conditions, consult the [project notices](../THIRD_PARTY_NOTICES.md).
