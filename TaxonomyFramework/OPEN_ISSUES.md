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
| P0-07 | Resolved | Legacy `FSM_btx` has 640 blank `module` values | The reviewed `FSM.xlsx` input uses an explicit 77-row `FSM_btx` sheet with no blank module values; the unselected legacy rows remain historical evidence and are not inferred from names | Keep the reviewed input and its full-pipeline regression fixture together; any later legacy-row migration still requires an explicit mapping | Phase 3 |
| P0-08 | High | Generator cannot deterministically reproduce the valid baseline | Baseline is a completed example with manual edits | Use ADR-0003 assembly as a generator acceptance test after reevaluation | Phase 1–5 |
| P0-09 | High | No concept-level comparison of 2015 and 2017 Tuple models | Official packages and checksums are fixed | Generate concept, type, tuple-path, role, and linkbase comparisons | Phase 2 |
| P0-10 | Medium | `tools/semantic/bie_to_fsm.py` has no explicit licence | Private WORK analysis only | Record author, copyright, and licence | Phase 1 |
| P0-11 | Medium | Publication authority for Framework DOCX | User-supplied starting point | Repository owner confirms authorship and publication authority | Publication gate |
| P0-12 | Medium | DOCX/XLSX binary metadata review | Text secret scan passed | Inspect author properties, hidden sheets, comments, and embedded objects before release | Phase 7 |
| P0-13 | Medium | End-to-end OIM example validation | Only taxonomy-root validity has been checked | Validate vendor-invoice metadata, CSV, facts, and round trip | Phase 5–6 |
| P0-14 | Medium | Shared/Aligned heuristic | Not a governance approval | Create a review registry based on provenance and scope of use | Phase 3/7 |
| P0-15 | Resolved | LHM and HMD terminology | Graph Walk from a declared root set or multiple explicit roots produces a combined 17-column LHM. Exactly one explicit root QName produces a 17-column HMD directly from the BSM; prior LHM generation is not required | Keep producer and consumer tests aligned with ADR-0007 | Phase 1 |
| P0-16 | Medium | Consumer migration | Only baseline checksums are frozen | Complete crosswalk, shadow generation, and rollback gates | Phase 6 |
| P0-18 | Resolved | Semantic pipeline integration | FSM 15, BSM 16, and LHM/HMD 17 columns are implemented and tested; the reviewed 500-row FSM plus 77-row FSM_btx generates a 713-row BSM, a 498-row combined LHM, and both root-specific HMDs | Maintain the full-data regression; downstream consumer migration remains separately tracked by P0-16 and P0-29 | Phase 1 |
| P0-19 | Resolved | DNM `-o` remains implemented | DNM is not supported and the option, branches, output, help, examples, and DNM-only tests are absent from the current Graph Walk | Prevent reintroduction through CLI regression tests | Phase 1 |
| P0-20 | High | Additional fields in the WORK 18-column output | Five responsibility-specific sidecar/manifest categories are proposed | Test ID collisions, missing joins, join multiplicity, and consumer impact on existing FSM data | Phase 1 |
| P0-21 | Resolved | Duplicate Association identity keys | Identity is `(association_role, associated_module, associated_class)` and excludes `property_term`; duplicates are reported without stopping unaffected Classes | Keep super/child matching, ambiguity isolation, continuation, and diagnostics under regression test | Phase 1 |
| P0-22 | Resolved | Semantic-tool generation integration | The reviewed current implementation and corresponding tests are authoritative; older WORK, 4-test, and 28-test generations remain comparison records only | Do not merge legacy-incompatible behaviour back into the reviewed implementation | Phase 1 |
| P0-23 | Medium | Duplication between `xBRL-GL2.0_btx` and `taxonomy/oim/prototype` | All 46 taxonomy files match by relative path and SHA-256 | Approve responsibility-based placement for DTS, samples, tools, generated files, and provenance | Phase 1 |
| P0-24 | Resolved | `element` generation from `semantic_path` | `semantic_path` is the semantic identity; Graph Walk generates module-unique lowerCamelCase NCNames after path construction. C/A/REF require an element; R depends on maximum multiplicity | Keep uniqueness and reproducibility fixtures; generator/consumer work follows separately | Phase 1 |
| P0-25 | High | Status of a PoC BSM containing errors | Keep status outside the 16-column BSM core; manifest and diagnostics are authoritative | Define schema for processing status, counts, report path/hash, property-status sidecar, and consumer rejection | Phase 1 |
| P0-26 | Blocker | Migration of existing models without `associated_module` | ADR-0006 defines Class and referenced-Class identities | Approve explicit mapping, review, migration diagnostics, and rollback for every reference; inference is forbidden | Phase 1 |
| P0-27 | Resolved | Isolation when a Specialization superclass cannot be resolved | Exclude the child from the normal BSM and record child-only properties in diagnostics | Apply to implementation and tests | Phase 1 |
| P0-28 | Resolved | Module registry and syntax-binding table | A seven-column binding table and management responsibility are defined; `taxonomy_entry_point` belongs in the release manifest | Confirm the final registry location and implement manifest/binding validation later | Phase 1 |
| P0-29 | High | Distinguishing legacy and new LHM contracts | The 17-column LHM contract applies from taxonomy version `2026-12-31`; manifest contract name/version are mandatory | Approve schema and consumer rejection rules before binding implementation | Phase 1 |
| P0-30 | Resolved | Author and reviewer of existing-FSM migration | The PoC operator prepares and reviews an auditable explicit mapping | Validate required migration records during implementation | Phase 1 |
| P0-31 | High | QName-form values in the semantic model | Automatic split, module inference, and warning-only acceptance are prohibited | Confirm diagnostic schema and approval procedure for legacy-QName mappings | Phase 1 |
| P0-32 | High | Same-named Classes from different modules in one HMD | FSM/BSM may retain candidates; an HMD explicitly selects one `(selected_module, class_term)` and prohibits mixing | Test selection, conflict, Aligned specialization, and `semantic_path` uniqueness before profile implementation | Phase 1 |
| P0-33 | High | `LICENSE.md` can be read as applying CC BY 4.0 to all generated artifacts | Do not change the existing licence file without owner approval; narrower README and notice text applies only to identified project-authored material | Obtain a file-level licensing decision and then align `LICENSE.md` without relicensing external originals, derivatives, or consumer data | Publication gate |
| P0-34 | Resolved | Full Accounting Entries and Business Transactions LHM element collision | The redundant inherited `cor:Entity_ Party / Business Description` declaration was removed from the reviewed FSM while `cor:Party / Party Business Description` remains and is inherited. Full combined Graph Walk completes with no same-module, different-ID element collision | Preserve the reviewed FSM fixture and the full multiple-root regression test | Phase 1 |

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
