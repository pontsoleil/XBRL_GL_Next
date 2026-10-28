**English** | [日本語](README_ja.md)

# Published taxonomy packages

The `taxonomy/` directory publishes XBRL GL Next taxonomies in three representations—XBRL 2.1 Tuple, OIM and Tavi—based on the formal model-specific HMDs in `semantic-model/HMD/`. For each applicable model, the three taxonomy representations use its formal HMD as their common semantic input. This describes the taxonomy architecture; it does not assert that every generation run used an identical historical file edition. The common View-worksheet-to-3-instance workflow (Tuple XML, OIM CSV with JSON metadata and Tavi CSV with JSON metadata) is the next development stage, not a completed three-format result.

The separate `tavi-poc/` directory is an independent Tavi taxonomy and instance prototyping environment. Its experimental taxonomy and instance inputs are **not** the shared HMDs or generator pipeline used for `taxonomy/`. Its Simple, Full v3 and HMD-view examples are not alternate names for the published four-model `taxonomy/tavi/` taxonomies.

This directory contains published Tuple, OIM and Tavi taxonomy packages.

## Tuple and OIM

- [`accounting-entries/`](accounting-entries/) — Accounting Entries (COR).
- [`business-transactions/`](business-transactions/) — Business Transactions (BTX).
- [`journal-entries/`](journal-entries/) — independently scoped journal-entry models.

Select the entry point for the intended model and binding. Do not combine independently generated DTS trees merely because they use similarly named concepts. Module namespaces use `https://www.xbrl.or.jp/taxonomy/xbrl-gl-next/{module}`; dates in filenames do not form part of these namespace URIs.

## Tavi JSON

The following independent model taxonomies are published under [`tavi/`](tavi/):

- [COR](tavi/accounting-entries/taxonomy.json)
- [COR-JPN](tavi/accounting-entries-jpn/taxonomy.json)
- [BTX](tavi/business-transactions/taxonomy.json)
- [BTX-PINT](tavi/business-transactions-pint/taxonomy.json)

Tavi JSON taxonomies are not XBRL 2.1 XSD entry points or instance documents. For the generator and its inputs, see the [Tavi generator overview](../tools/tavi/README_Tavi_4models_datatypes_candidate.md) and [reproduction guide](../tavi-poc/README_REPRODUCE_4_MODELS.md).

For provenance and publication conditions, consult the [project notices](../THIRD_PARTY_NOTICES.md).
