# Source inventory

## Purpose and status

This project-authored document distinguishes material currently registered in
the Private GitHub repository from planned or held material in the WORK
environment. It is a human-readable registration summary, not a
machine-readable manifest and not evidence that an external asset is cleared
for redistribution.

The current Private repository contains historical 2025 exploration assets and
the initial rearchitecture documents. The new `source/`, `taxonomy/`,
`examples/`, `tools/semantic/`, and generated inventory structures described
in WORK are not treated as registered unless they actually exist in the target
Git tree.

## Currently registered source families

| Current GIT path | Role | Registration status |
| --- | --- | --- |
| `semantic-model/FSM/` | Historical 2025 FSM snapshots | Reference only; not the 14-column PoC contract |
| `semantic-model/BSM/` | Historical 2025 BSM snapshots | Reference only; not the 15-column PoC contract |
| `semantic-model/LHM/` | Historical 2025 LHM snapshots | Reference only; not the 17-column LHM/HMD contract |
| `scripts/` | Historical transformation and taxonomy scripts | Functional and licence review required before reuse |
| `xBRL-CSV_taxonomy/` | Historical xBRL-CSV taxonomy material | Reference only; provenance and namespace review required |
| `xBRL-CSV_instance/` | Historical examples and workbooks | Registration predates this plan; rights, privacy, and test status require review |
| `XBRL-GL-2016-PWD/` | Historical work-product-derived material | External terms apply; not a project-owned specification |
| `docs/` | Project documentation and design decisions | Working Draft |
| `TaxonomyFramework/` | Rearchitecture contracts and plans selected for the branch | Working Draft |

Existing files are not automatically accepted as the conformance baseline or
as regression expected values. Their provenance, licence, data sensitivity,
and relationship to the new 14/15/17-column contracts are reviewed
independently.

## Planned, not yet registered

| Planned WORK family | Intended use | Current decision |
| --- | --- | --- |
| `contracts/` | Consumer migration contracts | This candidate contains only the README and empty mapping template |
| `source/models/core/` | Candidate semantic-model inputs | Not yet registered |
| `source/models/business-transactions/` | Candidate transaction-document models | Not yet registered |
| `source/unece/` | CCL-derived analysis input | Registration hold pending source-specific rights |
| `taxonomy/tuple/` | Tuple comparison baseline | Not yet registered under the new structure |
| `taxonomy/oim/prototype/` | OIM/Palette technical prototype | Registration hold pending provenance, namespace, and licence review |
| `taxonomy/experiments/` | Party, Document, and code-list experiments | Not yet registered |
| `examples/vendor-invoice/` | End-to-end xBRL-CSV candidate | Not yet registered; data and rights review required |
| `tools/semantic/` | Target Specialization and Graph Walk candidates | Not yet registered; program/fixture/test set must be approved together |
| `tools/taxonomy/` | Target syntax-binding generator candidate | Deferred until the semantic baseline is reproducible |
| `TaxonomyFramework/inventory/` | Machine-readable Phase 0 evidence | Generated evidence; not part of this candidate |

## External reference baselines

| Work product | Status | Release date | Recorded official package SHA-256 |
| --- | --- | --- | --- |
| XBRL Global Ledger 2015 | Recommendation | 2015-03-25 | `AFCAEE16683E1D1348E0BBE91D1928EC5EF2265BEA8590238F86D52E9F12B931` |
| XBRL Global Ledger 2017 | Public Working Draft | 2016-12-01 | `0C48AA0EA8F6963CA5A3625AD32ADA6AEE5B3A164438A155A0C9937CCFFECE67` |

Official packages are referenced by source, version, and checksum. They are not
copied merely to satisfy a repository link. Project prototypes and historical
extracts are not official XBRL International releases.

## Excluded or held

- external ZIP archives and standards documents whose redistribution is not
  expressly confirmed;
- UN/CEFACT-derived BIE, code-list, or taxonomy material without a verified
  download/redistribution basis;
- modified XBRL-derived taxonomies using an external owner's namespace;
- generated logs, caches, bytecode, temporary files, and reproducible
  intermediate output;
- real transactions, personal information, credentials, confidential
  configuration, and consumer working-tree content;
- duplicate or date-stamped working copies whose provenance is unclear.

## Registration controls

1. Record source, version, checksum, rights status, intended use, and
   project/external ownership before registration.
2. Apply MIT or CC BY 4.0 only to identified project-authored material.
3. Apply each external owner's terms to external originals and derivatives.
4. Do not register unresolved-rights material in the Private repository.
5. Do not infer approval by XBRL Japan, XBRL Europe, XBRL International,
   UN/CEFACT, or any other organization.
6. Recheck the target branch and actual paths immediately before copying.

See [`../THIRD_PARTY_NOTICES.md`](../THIRD_PARTY_NOTICES.md) for the licensing
boundary and
[`../TaxonomyFramework/OPEN_ISSUES.md`](../TaxonomyFramework/OPEN_ISSUES.md)
for unresolved registration issues. ADR-0003, ADR-0004, and the detailed Phase
0 inventory/dependency reports are under reevaluation and are not registered
by this candidate.
