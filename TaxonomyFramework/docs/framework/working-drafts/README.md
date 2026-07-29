# XBRL GL Next taxonomy framework working drafts

These project-authored documents are working drafts for private collaborative review. They are not approved specifications or official positions of XBRL Japan, XBRL Europe, XBRL International, or any other organisation.

## Current PoC baseline

- FSM has 15 columns, with `property_term` and `association_role` as separate columns.
- BSM has 16 columns; the sixteenth column is `id`, and BSM has no `element` column.
- LHM has 17 columns.
- BSM IDs use `XXnn` for Classes and `XXnn-pp` for properties. Property sequence width expands when more than 99 properties must be represented.
- HMD is not a fourth semantic model. For one explicit root Class QName, Graph Walk generates the 17-column root-specific HMD directly from BSM; a prior LHM is not required.
- The semantic-binding and syntax-binding sheets are provisional proposals, not final contracts.

## Current semantic input

| Artifact | SHA-256 | Review status |
|---|---|---|
| [FSM.xlsx](FSM.xlsx) | `A22F37E69168341F38F77987FD4B0D38BF732527C418A700CE766D45D991F3E2` | Reviewed 15-column FSM/FSM_btx input; `for-review`; `license-hold`; redundant `cor:Entity_ Party / Business Description` removed and sequence values normalised |

Review and reproducibility CSV derivatives are registered under
[`generated/`](generated/README.md). `FSM.csv` (500 rows) and `FSM_btx.csv`
(77 rows) use the 15-column FSM contract, `BSM.csv` (713 rows) uses the
16-column BSM contract, and the full combined `LHM.csv` (498 rows) uses the
17-column LHM/HMD contract for Accounting Entries and Business Transactions.
The authoritative source remains `FSM.xlsx`; all CSV derivatives are
`for-review`, `license-hold`, and must not be edited manually.

## Document register

All documents have status `for-review`. Most documents are collaborative-review revisions dated 2026-07-27. Part 1 was revised on 2026-07-29 and is provided in both DOCX and PDF formats. The taxonomy target version discussed by the project is 2026-12-31.

| Document | Author | SHA-256 | Review status |
|---|---|---|---|
| [Requirements Specification](XBRL_GL_Next_Requirements_Specification_revised_collaborative-review_2026-07-27.docx) | Nobuyuki SAMBUICHI | `816DA0514EE791C6EDF6D197ACDC8D08DDCF6AF4FC6DE73BC22F1D74828248D0` | Consistency and structural checks completed; stakeholder review pending |
| [How to extend the taxonomy](XBRL_GL_Next_Taxonomy_Framework_How_to_extend_the_taxonomy_revised_collaborative-review_2026-07-27.docx) | Nobuyuki SAMBUICHI | `6FAE2D6D05DCCFD82AAF9BA7B21A4DBA773FEDE5CFC75115D087EF5C01BC3952` | Consistency and structural checks completed; stakeholder review pending |
| [Part 1: General rules (DOCX)](XBRL_GL_Next_Taxonomy_Framework_Part_1_General_rules_revised_collaborative-review_2026-07-29.docx) | Nobuyuki SAMBUICHI | `79A953D002DB18709F423CBA60B70387BA2DC5874C26D9AFB2A35A98D94F7BEC` | Same Part 1 document, final reviewed DOCX distribution; `for-review`; `license-hold`; stakeholder review pending |
| [Part 1: General rules (PDF)](XBRL_GL_Next_Taxonomy_Framework_Part_1_General_rules_revised_collaborative-review_2026-07-29.pdf) | Nobuyuki SAMBUICHI | `421CE93B30B873FABACA860BAA55AEF4B4518CC6FE2DFE91A648512118617D52` | Same Part 1 document, 54-page Word-generated PDF distribution corresponding to the final reviewed DOCX; `for-review`; `license-hold`; stakeholder review pending |
| [Part 2: XBRL 2.1 palette taxonomy](XBRL_GL_Next_Taxonomy_Framework_Part_2_XBRL_2_1_palette_taxonomy_revised_collaborative-review_2026-07-27.docx) | Nobuyuki SAMBUICHI | `28EE0E920C9960DA87E770CF947093B35293B6EE98E0FF555CE69D09066276D0` | Consistency and structural checks completed; stakeholder review pending |
| [Part 3: xBRL-CSV palette taxonomy](XBRL_GL_Next_Taxonomy_Framework_Part_3_xBRL_CSV_palette_taxonomy_revised_collaborative-review_2026-07-27.docx) | Nobuyuki SAMBUICHI | `F7A73FF9A6ACA81DC291A6BFDE2DB52FC0E12826BE17D7222BA6765EE216D1A7` | Consistency and structural checks completed; stakeholder review pending |
| [Part 4: Aligned pool for extension](XBRL_GL_Next_Taxonomy_Framework_Part_4_Aligned_pool_for_extension_revised_collaborative-review_2026-07-27.docx) | Nobuyuki SAMBUICHI | `0BFB3A87510652FDDBA4F21A25EF6E576A7B372D5F2AEEE491CF3D75D3CE5D3E` | Consistency and structural checks completed; stakeholder review pending |

## Licence and distribution restrictions

Copyright and licensing terms for these drafts remain under review. Do not assume that repository-level MIT or CC BY 4.0 notices apply to these document files. Third-party specifications, excerpts, trademarks, and referenced material remain subject to the terms of their respective rights holders.

The files are restricted to the private project repository and invited review participants. They must not be redistributed publicly until the applicable rights, attribution, organisational approval, and publication procedure have been confirmed.

The sharing and redistribution status of Part 1 remains `license-hold`.

## Git registration status

This directory contains six logical working-draft documents in seven distribution files: six DOCX files and one PDF. The Part 1 DOCX and PDF are two distribution formats of the same logical document. Together with the reviewed `FSM.xlsx` semantic input, `README.md`, `COPY_REPORT.md`, the five review artifacts in `generated/`, and its `.gitattributes` byte-preservation rule, all sixteen files in this directory tree are tracked in Git.

## Verification note

The final DOCX package, XML parts, text, tables, metadata, links, comments, tracked changes, macros, embedded objects, absolute paths, email addresses, and credential-like strings were inspected. The corresponding Word-generated PDF contains 54 pages, and all 54 pages were visually reviewed after the 2026-07-29 cross-cutting contract revision. See [COPY_REPORT.md](COPY_REPORT.md) for the earlier registration audit record.
