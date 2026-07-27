**English** | [日本語](OPEN_ISSUES_ja.md)

# Open issues

Phase 0 fixed the location, impact, disposition, and implementation phase for
each issue. An unresolved issue never justifies ambiguous provenance or
publication scope; the affected artifact remains on registration or
publication hold.

| ID | Priority | Issue | Current decision | Next action | Phase |
| --- | --- | --- | --- | --- | --- |
| P0-01 | Blocker | GitHub owner, visibility, publication authority, and push approval | The target now has an `origin` remote and a dedicated branch; this does not itself authorize publication or each push | Repository owner confirms visibility and publication authority and approves each registration set | Publication gate |
| P0-02 | Blocker | XBRL-derived prototypes use an `xbrl.org` namespace | Retain for technical analysis; do not represent them as official taxonomies | Import an official taxonomy or migrate independently governed concepts to a project-owned namespace while preserving attribution | Phase 1–3 |
| P0-03 | Blocker | XBRL GL licence restricts modification of taxonomy content | Current Tuple/OIM trees remain on publication hold | Obtain legal review of the XBRL International-compliant extension/reimplementation boundary | Publication gate |
| P0-04 | Blocker | Redistribution rights for UN/CEFACT D25A-derived CSV | Free-of-charge use is not treated as redistribution or derivative-publication permission | Replace copied data with an official download recipe or obtain written permission | Publication gate |
| P0-05 | High | Original CCL D25A URL and checksum cannot be reconstructed | Only the release identifier is confirmed | Add row unique ID, official package, acquisition date, and checksum to the provenance table | Phase 3 |
| P0-06 | High | Tuple experiment has five local missing dependencies | Excluded from formal entry points | Rebuild as a self-contained fixture or profile resolver | Phase 1 |
| P0-07 | High | `FSM_btx` has 640 blank `module` values | Canonical `(module, class_term)` identity cannot be created | Review an explicit source-based mapping or source correction; record unresolved rows in the exclusion report and do not infer from names | Phase 3 |
| P0-08 | High | Generator cannot deterministically reproduce the valid baseline | Baseline is a completed example with manual edits | Use ADR-0003 assembly as a generator acceptance test after reevaluation | Phase 1–5 |
| P0-09 | High | No concept-level comparison of 2015 and 2017 Tuple models | Official packages and checksums are fixed | Generate concept, type, tuple-path, role, and linkbase comparisons | Phase 2 |
| P0-10 | Medium | `tools/semantic/bie_to_fsm.py` has no explicit licence | Private WORK analysis only | Record author, copyright, and licence | Phase 1 |
| P0-11 | Medium | Publication authority for Framework DOCX | User-supplied starting point | Repository owner confirms authorship and publication authority | Publication gate |
| P0-12 | Medium | DOCX/XLSX binary metadata review | Text secret scan passed | Inspect author properties, hidden sheets, comments, and embedded objects before release | Phase 7 |
| P0-13 | Medium | End-to-end OIM example validation | Only taxonomy-root validity has been checked | Validate vendor-invoice metadata, CSV, facts, and round trip | Phase 5–6 |
| P0-14 | Medium | Shared/Aligned heuristic | Not a governance approval | Create a review registry based on provenance and scope of use | Phase 3/7 |
| P0-15 | Resolved | LHM/HMD terminology | LHM is the whole table; HMD identifies or extracts one root Class; both use the common 17-column contract and `(module, class_term)` identity | Apply to implementation and fixtures | Phase 1 |
| P0-16 | Medium | Consumer migration | Only baseline checksums are frozen | Complete crosswalk, shadow generation, and rollback gates | Phase 6 |
| P0-18 | Blocker | WORK specialization 18-column output conflicts with old 15-column Graph Walk input | FSM 14, BSM 15, and LHM/HMD 17 columns are the PoC implementation baseline; current programs do not yet implement it | Register the specification, programs, fixtures, expected results, and tests as a matched candidate set after approval | Phase 1 |
| P0-19 | High | DNM `-o` remains implemented | DNM is not supported | Remove option, branches, output, help, examples, and DNM-only tests in the later implementation task | Phase 1 |
| P0-20 | High | Additional fields in the WORK 18-column output | Five responsibility-specific sidecar/manifest categories are proposed | Test ID collisions, missing joins, join multiplicity, and consumer impact on existing FSM data | Phase 1 |
| P0-21 | High | Duplicate Association identity keys | Report as input errors, but do not stop the entire PoC model | Implement and test super/child comparison, omission of ambiguous properties, continuation of other Classes, and diagnostics | Phase 1 |
| P0-22 | High | Semantic-tool generation integration | Independent features are distributed across WORK, 4-test, and 28-test generations | Prohibit whole-version overwrite and approve a feature-level integration plan | Phase 1 |
| P0-23 | Medium | Duplication between `xBRL-GL2.0_btx` and `taxonomy/oim/prototype` | All 46 taxonomy files match by relative path and SHA-256 | Approve responsibility-based placement for DTS, samples, tools, generated files, and provenance | Phase 1 |
| P0-24 | High | `element` generation from `semantic_path` | `semantic_path` is the semantic identity; generate a module-unique lowerCamelCase NCName from the shortest unique suffix. C/A/REF require it; R depends on maximum multiplicity. Programs are not updated | Convert AT-074–AT-094 into fixtures and verify Graph Walk reproducibility; generator/consumer work follows later | Phase 1 |
| P0-25 | High | Status of a PoC BSM containing errors | Keep status outside the 15-column core; manifest is authoritative | Define schema for processing status, counts, report path/hash, property-status sidecar, and consumer rejection | Phase 1 |
| P0-26 | Blocker | Migration of existing models without `associated_module` | ADR-0006 defines Class and referenced-Class identities | Approve explicit mapping, review, migration diagnostics, and rollback for every reference; inference is forbidden | Phase 1 |
| P0-27 | Resolved | Isolation when a Specialization superclass cannot be resolved | Exclude the child from the normal BSM and record child-only properties in diagnostics | Apply to implementation and tests | Phase 1 |
| P0-28 | Resolved | Module registry and syntax-binding table | A seven-column binding table and management responsibility are defined; `taxonomy_entry_point` belongs in the release manifest | Confirm the final registry location and implement manifest/binding validation later | Phase 1 |
| P0-29 | High | Distinguishing legacy and new LHM/HMD contracts | The 17-column contract applies from taxonomy version `2026-12-31`; manifest contract name/version are mandatory | Approve schema and consumer rejection rules before implementation | Phase 1 |
| P0-30 | Resolved | Author and reviewer of existing-FSM migration | The PoC operator prepares and reviews an auditable explicit mapping | Validate required migration records during implementation | Phase 1 |
| P0-31 | High | QName-form values in the semantic model | Automatic split, module inference, and warning-only acceptance are prohibited | Confirm diagnostic schema and approval procedure for legacy-QName mappings | Phase 1 |
| P0-32 | High | Same-named Classes from different modules in one HMD | FSM/BSM may retain candidates; an HMD explicitly selects one `(selected_module, class_term)` and prohibits mixing | Test selection, conflict, Aligned specialization, and `semantic_path` uniqueness before profile implementation | Phase 1 |
| P0-33 | High | `LICENSE.md` can be read as applying CC BY 4.0 to all generated artifacts | Do not change the existing licence file without owner approval; narrower README and notice text applies only to identified project-authored material | Obtain a file-level licensing decision and then align `LICENSE.md` without relicensing external originals, derivatives, or consumer data | Publication gate |

## Items resolved in Phase 0

- Identified the 2015 official package as Recommendation `2015-03-25`.
- Identified the 2017 work product as PWD `2016-12-01`.
- Fixed official ZIP URLs, sizes, file counts, and SHA-256 values.
- Verified all 99 selected UADA copies at import time; 97 remain identical and
  two intentional WORK revisions are tracked as different.
- Distinguished the UADA and WORK Git roots.
- Identified 478 DTS dependency edges and five local missing references.
- Froze checksums for eight consumer LHM baselines.
- Separated GitHub candidates, Private-only material, publication holds, and
  excluded material.
- Confirmed zero findings in the high-confidence secret scan.
- Found one pre-existing prototype syntax error in the full tools compile and
  recorded it as P0-17.
- Revised WORK `specialization.py` for P0-17 and fixed property identity,
  modification, addition, multiplicity-`0` deletion, cycle detection, and CLI
  behavior in unit tests.
