**English** | [日本語](README_ja.md)

# XBRL GL Next — Tavi proof of concept

This independent experimental environment uses the Tavi Public Working Draft to prototype Tavi taxonomies, instances, viewers and an Arelle OimTaxonomy extension. It does not share the formal HMD inputs or taxonomy generation pipeline used for the published three-representation `taxonomy/` packages. Four model-specific Tavi taxonomies are separately published under `taxonomy/tavi/`; the Simple, Full v3 and HMD-view PoC examples here are distinct. It is a project publication for collaborative technical review, not a declaration of formal standards endorsement or full Tavi conformance.

## Published XBRL GL Next Tavi taxonomy outputs (separate from the PoC)

| Model | Root | Published taxonomy |
| --- | --- | --- |
| COR | `cor:accountingEntries` | [Accounting Entries](../taxonomy/tavi/accounting-entries/taxonomy.json) |
| COR-JPN | `jpn:accountingEntries` | [Accounting Entries — Japan](../taxonomy/tavi/accounting-entries-jpn/taxonomy.json) |
| BTX | `btx:businessTransactions` | [Business Transactions](../taxonomy/tavi/business-transactions/taxonomy.json) |
| BTX-PINT | `pint:businessTransactions` | [Business Transactions — PINT](../taxonomy/tavi/business-transactions-pint/taxonomy.json) |

Each published model has its own formal 18-column HMD under `semantic-model/HMD/`. The [four-model HMD-to-Tavi generator](tools/hmd_to_tavi.py) creates a taxonomy from one formal HMD at a time, independently of the Simple and HMD-view PoC examples; it does not implement Specialisation, Graph Walk or instance generation. See the [four-model reproduction guide](README_REPRODUCE_4_MODELS.md) and [model summary](README_ADDENDUM_4_MODELS.md).

## Additional examples

| Example | Taxonomy | Report or view |
| --- | --- | --- |
| Simple Tavi | [Minimal taxonomy](taxonomy/tavi-tax.json) | [JSON metadata](instance/tavi-inst.json) + [CSV](instance/tavi-inst.csv) |
| Full Accounting Entries v3 | [Full v3 taxonomy](taxonomy/XBRL_GL_Next_Tavi_AccountingEntries_v3.json) | Taxonomy only; no corresponding published Full instance package is asserted |
| Single Account Date r2 HMD view | [View taxonomy](profiles/single-account-date-r2/taxonomy/Tavi_JournalEntries_SingleAccount_Date_r2_candidate.json) | [View metadata](instance/tavi-inst-hmd-view.json), [profile metadata](profiles/single-account-date-r2/instance/tavi-inst-nine-column-Date-r2-candidate.json), and the referenced CSV files |

Open the relevant JSON metadata in Arelle when inspecting an instance; a CSV file alone is not a complete xBRL-CSV report. The Simple, Full v3, HMD-view and four-model taxonomies have different scopes and are not interchangeable.

## Arelle and static viewers

The [Arelle patch application guide](arelle/APPLY_PATCH.md) and [environment guide](arelle/ENVIRONMENT.md) describe a separate Arelle checkout with the OimTaxonomy plug-in. The supported PoC includes taxonomy loading, native fact display, a transposed Structured Tidy Data view and label-language selection within the documented patch scope.

Static HTML demonstrations:

- [Simple Tavi viewer](https://pontsoleil.github.io/XBRL_GL_Next/tavi-inst.html)
- [HMD-view viewer](https://pontsoleil.github.io/XBRL_GL_Next/tavi-inst-hmd-view.html)

These are displays, not formal Tavi validators. The four-model acceptance concerns taxonomy generation and native DTS loading; general View-to-Tavi instance generation and four-model instance validation are not established by those results. Do not infer them from the static viewers.
