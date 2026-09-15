# XBRL GL Next instance validation — v4

## OIM layout

OIM instances are flat pairs directly under `ids/oim/`.
The JSON and Structured CSV use the same basename.

- `accountingEntries-journalEntry`: PASS
- `businessTransactions-vendorInvoice`: PASS

Checks performed:
- exactly one JSON + one CSV per OIM instance;
- JSON/CSV basename equality;
- exactly one xBRL-CSV table per metadata file;
- table URL resolves to the same-basename CSV;
- flattened taxonomy relative path resolves;
- CSV header order equals metadata column order;
- obsolete OIM subdirectories do not remain.

Arelle entry points:
- `ids/oim/accountingEntries-journalEntry.json`
- `ids/oim/businessTransactions-vendorInvoice.json`
