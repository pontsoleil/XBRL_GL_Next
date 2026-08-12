# XBRL GL Next sample instances — v0

Date: 2026-08-11

The examples use the test-generated XBRL GL Next taxonomy.

## Tuple

Tuple instances remain XML files:

- `tuple/accountingEntries-journalEntry.xml`
- `tuple/businessTransactions-vendorInvoice.xml`

## OIM / xBRL-CSV

Each OIM instance is represented by exactly two files directly under `ids/oim/`:

- one JSON metadata file, which is the Arelle entry point;
- one Structured CSV data file.

The JSON and CSV use the same basename.

```text
ids/
└─ oim/
   ├─ accountingEntries-journalEntry.json
   ├─ accountingEntries-journalEntry.csv
   ├─ businessTransactions-vendorInvoice.json
   └─ businessTransactions-vendorInvoice.csv
```

There is no HMD-specific subdirectory under `ids/oim/`.

For Arelle, open the `.json` file, not the `.csv` file.

Examples:

- `accountingEntries-journalEntry.json`
- `businessTransactions-vendorInvoice.json`

Each CSV is one Structured CSV. It is not split into normalized Class tables.
Occurrence-key dimension columns retain the HMD hierarchy.
