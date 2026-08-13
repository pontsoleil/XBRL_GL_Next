**English** | [日本語](README_ja.md)

# XBRL GL Next sample instances

This directory contains small sample instances for the two XBRL GL Next sample HMDs:

- `cor_accountingEntries`
- `btx_businessTransactions`

The samples demonstrate how the same reviewed semantic model can be reported through the Tuple and OIM bindings. They are informative examples and do not define additional Framework requirements.

## Contents

```text
ids/
├─ README.md
├─ README_ja.md
├─ VALIDATION_REPORT.md
├─ tuple/
│  ├─ accountingEntries-journalEntry.xml
│  └─ businessTransactions-vendorInvoice.xml
└─ oim/
   ├─ accountingEntries-journalEntry.json
   ├─ accountingEntries-journalEntry.csv
   ├─ businessTransactions-vendorInvoice.json
   └─ businessTransactions-vendorInvoice.csv
```

## Tuple samples

The Tuple samples are XBRL 2.1 XML instances:

- `tuple/accountingEntries-journalEntry.xml`
- `tuple/businessTransactions-vendorInvoice.xml`

Open the XML file as the instance document. The instance discovers the corresponding Tuple taxonomy entry point under `../taxonomy/tuple/`.

These examples illustrate the physical Tuple hierarchy generated from the formal HMD.

## OIM / xBRL-CSV samples

Each OIM example consists of exactly two files with the same basename:

- a JSON metadata file;
- one Structured CSV data file.

For example:

```text
oim/accountingEntries-journalEntry.json
oim/accountingEntries-journalEntry.csv
```

The **JSON file is the report entry point**. When opening an xBRL-CSV sample in Arelle, open the `.json` file, not the `.csv` file.

The CSV remains one rectangular Structured CSV table. Class occurrences are identified by occurrence-key columns bound to typed dimensions; the CSV is not split into separate normalized Class tables.

## How to use the samples

Open the sample instance from this directory.

1. For Tuple, open the corresponding XML instance under `tuple/`.
2. For OIM/xBRL-CSV, open the corresponding JSON metadata file under `oim/`. The JSON file is the report entry point; the associated CSV file is read through that metadata.
3. The instance or OIM metadata references the corresponding taxonomy entry point under `../taxonomy/`, which is discovered by the XBRL processor.
4. Inspect the reported facts together with the taxonomy presentation and, for OIM, the dimensional network.
5. Use these samples as informative examples of the bindings defined in Taxonomy Framework Parts 2 and 3.

## Validation

See [`VALIDATION_REPORT.md`](VALIDATION_REPORT.md) for the instance-validation record.

The accepted 2026-08-12 baseline was validated with Arelle 2.44.1:

- Tuple instances: 2/2, error 0 / warning 0
- OIM instances: 2/2, error 0 / warning 0

## Editing policy

These are sample instances associated with the checked-in sample taxonomy. If the formal taxonomy changes, update the samples deliberately and rerun validation. Do not change an instance merely to hide a taxonomy or semantic-model error.
