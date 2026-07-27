**English** | [日本語](COPY_PLAN_ja.md)

# Copy and GitHub registration plan

## 1. Principles

- Treat the UADA source as a read-only investigation source.
- Never copy a directory tree without an explicit file list.
- Track each adopted file by source path, destination path, size, timestamp,
  and SHA-256.
- Inspect differences and adoption reasons before overwriting a same-named
  file.
- Do not register archives, logs, caches, real data, or external originals
  whose rights are unresolved.
- The target now has an `origin` remote and a dedicated branch. Registration
  scope, publication authority, and each push still require user approval.

## 2. Copies completed in WORK

These entries describe WORK imports; they do not mean that the same assets are
approved for Private GitHub registration.

| Source | WORK destination | Disposition | Collision | Verification |
| --- | --- | --- | --- | --- |
| UADA XBRL GL tree | `taxonomy/tuple/gl` | Adopted for analysis | None | 52/52 SHA-256 matched at import |
| Core FSM/BSM/LHM | `source/models/core` | Adopted for analysis | None | 3/3 matched |
| Business-transaction FSM/BSM/LHM | `source/models/business-transactions` | Adopted; blank CSV records removed in WORK FSM | Existing source retained | 2/3 matched; one intentional FSM difference |
| Selected UNECE CSV | `source/unece` | Private analysis only | None | 9/9 matched |
| Document experiment | `taxonomy/experiments/document` | Private experiment | None | 7/7 matched |
| Selected party pool | `taxonomy/experiments/party` | 11 adopted; 17 excluded | None | 11 adopted files matched |
| Selected code lists | `taxonomy/experiments/codelists` | 8 adopted; 111 excluded | None | 8 adopted files matched |
| Semantic/taxonomy tools | `tools` | Four adopted for comparison | WORK specialization revised | 3/4 matched at the recorded stage |
| Vendor invoice CSV/JSON | `examples/vendor-invoice` | Two adopted for analysis | None | 2/2 matched at import |
| Historical OIM/Palette bundle | `xBRL-GL2.0_btx` | 57 source files imported and date-normalized; one WORK provenance file added | Managed separately from the project tree | 57 source payload files plus one provenance file |

The file-level import evidence is a WORK-generated inventory. It is not
registered by this documentation unit and must not be copied solely to satisfy
a link.

## 3. Phase 0 artifacts prepared in WORK

| Source activity | WORK artifact | Purpose | Verification |
| --- | --- | --- | --- |
| Read-only repository, UADA, and official-package scan | Phase 0 inventory and machine-readable evidence | Fix provenance and disposition | Manifest summary and hash recalculation |
| XSD/XML dependency scan | Dependency report | Fix DTS graph and missing references | XML parse error count |
| Phase classification | `OPEN_ISSUES.md` | Identify blockers, owners, and next phase | Stable issue IDs and review |
| Copy review | This plan and source comparison | Record disposition, collisions, and checks | 99 imported files: 97 unchanged, two intentional WORK revisions |
| Manifest generator | WORK inventory tool | Reproducible inventory | Python compile and regeneration comparison |

Only project-authored documents explicitly listed in the current registration
unit are candidates. Generated evidence, tools, taxonomies, and external-source
material remain separate decisions.

## 4. Proposed placement of `xBRL-GL2.0_btx` and the OIM prototype

This section is a proposal made before any move or deletion. No file is moved,
renamed, deleted, overwritten, or copied to the formal repository without
approval.

### 4.1 Findings

| Item | `xBRL-GL2.0_btx/` | `taxonomy/oim/prototype/` |
| --- | ---: | ---: |
| All files | 58 | 46 |
| XSD | 19 | 19 |
| XML | 28 | 27 |
| Other | 11 | 0 |
| Zero-byte files | 0 | 0 |

The source bundle contained 57 files. WORK contains 58 because
`PROVENANCE.md` was added after import. The 46 taxonomy files in
`taxonomy/oim/prototype/` match the corresponding bundle files by relative path
and SHA-256. Maintaining both as taxonomy authorities is unnecessary.

The matching set includes two comparison files,
`plt/plt-def-2026-12-31_02-20_A.xml` and
`plt/plt-def-2026-12-31_02-20_B.xml`, that are not named by the entry point.
Whether they belong in a comparison fixture or are excluded remains open.

### 4.2 Twelve files found only in `xBRL-GL2.0_btx/`

| Category | Files | Proposed placement | Current disposition |
| --- | --- | --- | --- |
| Provenance | `PROVENANCE.md` | `docs/provenance/` or a source manifest | Retain in WORK |
| Comparison copy | `vendor_invoices copy.json` | Exclude or move to a comparison fixture | Hold |
| Candidate sample source | `vendor_invoices.csv` | `examples/vendor-invoice/` or an instance fixture | Compare with existing example |
| Candidate generated samples | `vendor_invoices.json`, `xbrl-gl.json` | `examples/` or generated output | Hold |
| Candidate binary output | `vendor_invoices.xlsx`, `xbrl-gl_skeleton.xlsx` | Exclude if reproducible | Hold |
| Candidate metadata source | `xbrl-gl_skeleton.csv` | Metadata fixture | Hold |
| Candidate validation tools | Three `verify_tax_subtotals*.py` files | `tests/` or `tools/validation/` after functional integration | Hold |
| Comparison instance | `ids/Vendor_Invoices_revised.xml` | Legacy-instance fixture or reference only | Hold |

Same-named CSV/JSON files under `examples/vendor-invoice/` have different
SHA-256 values. They are never overwritten without fact, metadata, taxonomy
URI, provenance, and expected-result comparison.

### 4.3 Proposed future placement

| Asset | Candidate authority | Future treatment of duplicate | Gate |
| --- | --- | --- | --- |
| OIM/Palette taxonomy | `taxonomy/oim/prototype/` | Remove duplicate bundle copies only after manifest review | XML Schema, DTS, XMLSpy, Arelle, and hash checks |
| Definition comparisons A/B | Taxonomy-comparison fixture or exclusion | Separate from taxonomy authority | Documented purpose and expected differences |
| Sample instance/metadata | `examples/` or fixtures | Separate from source bundle | Rights, anonymization, provenance, expected results |
| Reproducible JSON/XLSX | Generated output or Git exclusion | Separate from source bundle | Reproduction command and stable hash |
| Validation scripts | `tests/` or `tools/validation/` | Integrate functions after comparison | Unit tests, CLI, dependencies |
| Import provenance | `docs/provenance/` and manifest | Retain old bundle path as history only | Source, transformation, date, and SHA |

### 4.4 Zero-byte files

Neither inspected directory currently contains a zero-byte file. A future
finding is classified without immediate deletion:

1. intentional placeholder, documented as such;
2. abnormal generator output, quarantined and excluded;
3. missing content, requiring source-hash review and reacquisition or
   regeneration.

## 5. Material not copied in the next registration unit

| Target | Decision | Reason |
| --- | --- | --- |
| Official XBRL GL 2015/2017 ZIP files | Do not copy | Reacquire by official URL, version, and checksum |
| UADA archives, dated work folders, and duplicate workbooks | Do not copy | They obscure provenance and duplicate reproducible CSV |
| Logs, `__pycache__`, and bytecode | Do not copy | Temporary or generated |
| UN/CEFACT originals and bulk code lists | Hold | Redistribution and derivative-publication conditions unresolved |
| Consumer LHM or real consumer data | Do not copy | Provider retains only approved checksums and crosswalk metadata |
| Original ChatGPT review workbooks | Do not copy | Review evidence, not a distribution artifact |

## 6. GitHub registration candidates

### Candidate for tracking

- approved project-authored README, governance, architecture, contracts, and
  ADR documents;
- approved project-authored tests and tools with confirmed licence;
- approved machine-readable contracts that contain no real or confidential
  data.

### Private-only after separate approval

- draft FSM/BSM/LHM/HMD and test fixtures;
- technical taxonomy prototypes and experiments;
- examples whose rights, privacy, and expected results are confirmed.

Private placement is not a substitute for redistribution permission.
`xBRL-GL2.0_btx/` is not registered as one directory. Taxonomy, sample, tool,
generated output, and provenance are reviewed separately.

### Excluded from public push

- modified XBRL-derived taxonomies using an official external namespace;
- UN/CEFACT-derived material without permission;
- tools without confirmed authorship and licence;
- binaries, review evidence, archives, caches, logs, real data, and secrets.

## 7. Verification after an approved copy

The following commands are examples for the WORK inventory environment. Roles
are passed through environment variables rather than personal absolute paths.

```powershell
python .\tools\inventory\generate_phase0_manifests.py `
  --repo . `
  --source $env:XBRL_GL_NEXT_UADA_SOURCE `
  --official-dir $env:XBRL_GL_OFFICIAL_PACKAGE_DIR `
  --work-root $env:XBRL_GL_NEXT_WORKSPACE `
  --output-dir .\TaxonomyFramework\inventory

python .\tests\check_repository.py
python -m py_compile .\tools\inventory\generate_phase0_manifests.py
git diff --check
```

Taxonomy changes additionally require entry-point validation with Arelle and
XMLSpy. The former `bie_specialization.py` was later revised in WORK and
renamed `specialization.py`; it is not part of this documentation registration
unit.

## 8. Decisions before semantic-tool integration

### 8.1 Canonical core

- FSM has 14 columns; BSM has those 14 plus terminal `id`, and no `element`.
- LHM/HMD share a 17-column contract. They retain `semantic_path`,
  `associated_module`, and HMD identity `class_term`; they exclude `path`,
  `associated_class`, `abbreviation_path`, and `xpath`.
- XML placement such as `xpath` belongs to syntax binding.
- Graph Walk generates a prefix-free lowerCamelCase NCName after fixing
  `semantic_path`, prepending non-repeating ancestor terms until module-unique.
  It does not use sequence, input order, or hash. C/A/REF require `element`;
  R leaves it blank for maximum multiplicity one and requires a dimension
  element when the maximum exceeds one or is unbounded.
- FSM/BSM may retain same-named Class candidates from different modules. One
  HMD explicitly selects only one module for a `class_term` and prohibits
  mixing.

### 8.2 DNM

DNM and `graphwalk.py -o` are not supported by the target. A later
implementation task removes the option, branches, outputs, examples, help, and
DNM-only tests. This documentation task does not modify programs.

### 8.3 Additional fields in the WORK 18-column generation

`fsmid`, `inherited`, `UNID`, `TDED`, `context`, and `short_name` are not added
to the canonical core. They belong in responsibility-specific provenance,
inheritance-trace, external-reference, semantic-context, and
label/presentation sidecars. Their contracts remain a separate design and
implementation gate.

### 8.4 Association

An empty role remains empty and is not inferred. Duplicate
`(property_term, associated_module, associated_class)` values within one Class
are input errors regardless of property type, multiplicity, ID, or sequence.
During the PoC, unaffected Classes and unambiguous properties continue into the
BSM; ambiguous properties are omitted and diagnosed. The implementation never
chooses by ID/order, silently merges, rewrites a role, or appends a sequence.
Result status belongs in the manifest, not the 15-column core.

## 9. Phase 0 exit decision

The project has classified copy candidates, exclusions, reference-only
material, Private-only candidates, and publication holds. Inventory and scope
definition are complete. Public release remains gated by the blockers in
[`OPEN_ISSUES.md`](OPEN_ISSUES.md) and explicit approval of visibility,
publication authority, and each registration set.

## 10. FSM-to-BSM-to-LHM/HMD baseline registration

The detailed baseline plan is already present in the target as a Japanese-only
working document. It is not an English canonical specification and is held
from further promotion until an English canonical version and aligned Japanese
version are prepared. Current WORK, 4-test, and 28-test generations are
comparison sources, not automatically adopted versions. Programs, combined
fixtures, expected results, and tests must implement and verify the new
14/15/17-column contracts as one matched set before registration. No copy,
branch operation, commit, or push is performed without user approval.
