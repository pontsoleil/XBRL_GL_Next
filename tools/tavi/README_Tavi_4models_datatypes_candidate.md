**English** | [日本語](README_Tavi_4models_datatypes_candidate_ja.md)

# HMD-to-Tavi taxonomy generator: four models

The current [`hmd_to_tavi.py`](../../tavi-poc/tools/hmd_to_tavi.py) generates one Tavi taxonomy JSON file from one accepted, 18-column HMD CSV. It uses Python 3.10 or later and the standard library. It does not generate instances, table templates or viewers, nor does it perform Specialisation or Graph Walk.


This describes the HMD-to-Tavi generator used for the `taxonomy/tavi/` four-model output collection, not the independent Simple or HMD-view taxonomy and instance experiments in `tavi-poc/`. The common View-to-three-instance workflow is planned, not implemented here.

## Published models

| Model | HMD root | HMD input | Taxonomy JSON |
| --- | --- | --- | --- |
| COR | `cor:accountingEntries` | [`accounting-entries`](../../semantic-model/HMD/accounting-entries/XBRL_GL_Next_HMD_AccountingEntries_for_taxonomy.csv) | [`taxonomy.json`](../../taxonomy/tavi/accounting-entries/taxonomy.json) |
| COR-JPN | `jpn:accountingEntries` | [`accounting-entries-jpn`](../../semantic-model/HMD/accounting-entries-jpn/XBRL_GL_Next_HMD_AccountingEntries_for_taxonomy.csv) | [`taxonomy.json`](../../taxonomy/tavi/accounting-entries-jpn/taxonomy.json) |
| BTX | `btx:businessTransactions` | [`business-transactions`](../../semantic-model/HMD/business-transactions/XBRL_GL_Next_HMD_BusinessTransactions_for_taxonomy.csv) | [`taxonomy.json`](../../taxonomy/tavi/business-transactions/taxonomy.json) |
| BTX-PINT | `pint:businessTransactions` | [`business-transactions-pint`](../../semantic-model/HMD/business-transactions-pint/XBRL_GL_Next_HMD_BusinessTransactions_for_taxonomy.csv) | [`taxonomy.json`](../../taxonomy/tavi/business-transactions-pint/taxonomy.json) |

Each model is generated independently. Do not assume identical structure or types across roots. The input must be a formal HMD with the accepted 18 columns, including `value_domain`; a Reviewed LHM is not an alternative input.

## Interface and types

The command accepts `--hmd PATH`, `--output PATH`, `--version TEXT`, `--include-documentation` and optional `--documentation-target QName`. Specify a new output file: existing output files are not overwritten. The generator preserves HMD semantic paths, module identities, row order and available labels and documentation, and rejects unsupported datatypes or invalid roots.

The Tavi base-type mapping includes `Identifier` → `xs:string`, `Code` → `xs:token`, `Text` → `xs:string`, and `Amount` → `xbrli:monetary`, alongside the generator's other supported datatype mappings. Module namespaces follow `https://www.xbrl.or.jp/taxonomy/xbrl-gl-next/{module}`.

For exact commands, input identities, validation scope and environment requirements, consult the [four-model reproduction guide](../../tavi-poc/README_REPRODUCE_4_MODELS.md). Its dated execution evidence must not be mistaken for a fresh-clone verification.
