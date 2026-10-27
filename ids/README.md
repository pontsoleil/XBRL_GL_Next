**English** | [日本語](README_ja.md)
# XBRL GL Next sample Instance Documents (`ids`)

**`ids` means XBRL Instance Documents.** These are instance examples that use generated taxonomies, not a directory of identifier definitions.

- `tuple/`: XBRL 2.1 XML instance documents for Accounting Entries, Business Transactions and other scoped examples. Open the XML as the instance entry point.
- `oim/`: xBRL-CSV sample reports, each composed of **one JSON metadata file and the corresponding CSV data file**. Open the JSON metadata as the report entry point. Keep the pair together, including relative references.

These samples relate to the relevant independent taxonomy roots under [`taxonomy/`](../taxonomy/). The number of sample instances differs from the number of taxonomy entry points. Historical validation results do not constitute a fresh run of these examples.

The separate [`tavi-poc/instance/`](../tavi-poc/instance/) contains experimental Tavi resources. It is not a fourth set of validated full Tavi instances: automatic generation from View definitions must be investigated and accepted separately.
