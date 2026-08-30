# XBRL GL Next split taxonomy

XBRL GL Next publishes Accounting Entries and Business Transactions as separate DTSs. Their canonical generated roots are:

- `taxonomy/accounting-entries/` — 58 accepted generated files
- `taxonomy/business-transactions/` — 67 accepted generated files

The experimental namespace family is:

```text
https://www.xbrl.or.jp/taxonomy/xbrl-gl-next/experimental/{module}/2026-12-31
```

The namespace is an experimental project namespace. It does not by itself establish external publication authority.

Canonical semantic-model artefacts are maintained under `semantic-model/FSM/`, `semantic-model/BSM/`, `semantic-model/LHM/`, and `semantic-model/HMD/`. LHM and HMD artefacts use DTS-specific `accounting-entries/` and `business-transactions/` subdirectories where their accepted bytes differ.

Taxonomy-generation datatype inputs are maintained under `definitions/taxonomy/`, and the accepted static `gl-gen` seed is maintained under `tools/taxonomy/gen/`. Per-DTS publication provenance is maintained under `taxonomy/provenance/` outside the generated DTS roots.

Files under `ids/**` are not part of Phase 1. Instance regeneration is handled later through the existing UADC-PoC transformation routes.

Legacy single-tree taxonomy cleanup is deferred. Files under `docs/**` are working evidence and are not publication content.
