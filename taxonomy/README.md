# Generated taxonomy packages

The existing public XBRL 2.1 **Tuple** and **OIM** DTS trees are organised by independent roots:

- `accounting-entries/` (COR),
- `business-transactions/` (BTX), and
- `journal-entries/` (a separately scoped, purpose-specific model).

Each root has its own Tuple/OIM entry points. The namespace form is `https://www.xbrl.or.jp/taxonomy/xbrl-gl-next/{module}`; dates in physical filenames are not namespace dates. Do not merge independently generated DTS trees or assume that common names entail equivalent types.

The four-model Tavi acceptance set uses `taxonomy/tavi/{accounting-entries,accounting-entries-jpn,business-transactions,business-transactions-pint}/taxonomy.json` **in WORK**. It is a separate JSON PoC, not an OIM XSD entry point and not the older Simple/COR Full v3/HMD View files under `tavi-poc/taxonomy/`. [Reproduction instructions](../tavi-poc/README_REPRODUCE_4_MODELS.md).

Published manifests and provenance must be interpreted against their stated scope; historical package identities are not silently revised when new HMDs are accepted.
