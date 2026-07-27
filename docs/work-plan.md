**English** | [日本語](work-plan_ja.md)

# Recommended work plan

## Phase 0 — Repository and provenance baseline

- Status: completed 2026-07-25.
- The target Git repository now has an `origin` remote on the dedicated
  rearchitecture branch. Repository ownership, visibility, publication
  authority, and each push remain explicit governance gates rather than
  inferred permission.
- Consumer LHM checksums for UADC_PoC and LedgerExplorer are frozen in
  `TaxonomyFramework/inventory/consumer-lhm-baseline.csv`.
- Exact XBRL GL 2015/2017 package URLs, file counts, checksums and licence
  statements are recorded.
- UN/CEFACT inputs are classified as private analysis material until an
  official package checksum or redistribution permission is recorded.
- Open issues have stable IDs, ADRs are in `docs/decisions`, and public release
  blockers are separated from later design work.
- All current taxonomy files remain `prototype`.

Exit condition met: each imported artifact has a recorded source or source
classification, version where known, rights status and GitHub disposition.
Unknown authority does not become an implicit permission; the artifact is
placed on publication hold.

## Phase 1 — Requirements and conformance matrix

- Turn each `GL-REQ-*` requirement into a machine-readable requirement record.
- Map requirements to Framework sections, implementation artifacts and tests.
- Resolve open vocabulary: `LHM` versus `HMD`, `Shared` versus `Aligned`, and
  profile/palette terminology.
- Define initial profiles: ledger, invoice/business transaction and statistical
  observation.

Exit condition: every prototype feature traces to an approved requirement and
profile.

## Phase 2 — 2015/2017 reverse engineering

- Inventory entry points, modules, tuples, types, substitution groups and
  linkbases.
- Build canonical tuple paths and stable source identifiers.
- Identify semantic duplicates and module coupling.
- Create `mapping/tuple-to-semantic.csv`.

Exit condition: each retained 2015/2017 concept has an explicit semantic
disposition.

## Phase 3 — Foundational Semantic Model

- Normalize names, definitions, representation terms, cardinalities and
  associations.
- Separate Shared, Aligned and Distinct governance status from algorithmic
  similarity scores.
- Attach UN/CEFACT Dictionary Entry Name, unique ID, release and business
  context to Shared candidates and retain the corresponding provenance when an
  Aligned specialization is created.
- Assign stable concept IDs and semantic paths independent of XML QName.
- Define deterministic superclass specialization using
  `(property_term, associated_module, associated_class)` as the Association
  property identity key.
- Identify Classes by `(module, class_term)` and referenced Classes by
  `(associated_module, associated_class)`. Require both reference fields even
  within one module. Apply XML Schema `token`-equivalent whitespace collapse
  to managed strings; preserve free-text definitions. Lowercase ASCII in
  module identifiers only. Reject QName-form semantic values rather than
  splitting them, and defer QName construction to syntax binding.
  Keep an empty role empty. Report a
  duplicate identity key within the same class before specialization,
  regardless of association kind, multiplicity, property ID or sequence.
- During the PoC, continue unaffected classes and unambiguous properties after
  model errors. Do not select or merge an ambiguous Association; mark it
  unresolved or requiring review and emit a diagnostic report with the BSM.
- Permit child classes to remove, modify and add inherited properties.
  Association kind and multiplicity are modifiable and are not part of the
  identity key.
- Establish module ownership rules for `cor`, `bus`, `btx`, `sta`, `lnk` and
  supporting modules.

Exit condition for the PoC: FSM validation identifies every unresolved class,
duplicate stable ID and ambiguous Association; unaffected content is emitted
deterministically; every omission is linked to the diagnostic report. A clean
release still requires zero unresolved model errors.

## Phase 4 — Profiles, BSM and graph walk

- Define a declarative profile manifest.
- Specialize FSM into BSM without editing Shared definitions by applying child
  property removals, modifications and additions.
- Treat multiplicity `0` as a removal directive. Do not emit the matching
  inherited property or the directive row to the effective BSM. A new
  Association with no matching superclass property and multiplicity `0` or
  `0..0` is also not effective and is not emitted.
- Generate LHM/HMD deterministically by declared roots and association choices.
- For Reference Associations, emit R and target-PK-derived REF rows, inherit
  the target module from R to REF, and stop traversal without parsing names.
- Read the 14-column FSM, emit the 15-column BSM semantic core and emit the
  17-column LHM/HMD semantic core. Omit BSM `element`; omit LHM/HMD `path`,
  `abbreviation_path`, `xpath` and `associated_class`; retain
  `semantic_path`, `associated_module` and HMD identity `class_term`,
  and generate the LHM/HMD `element` from the finalized semantic path.
- Generate a model-wide unique LC3 element name by prepending non-repeating
  parent or ancestor words. Report an error instead of adding an automatic
  number when ancestry cannot make the name unique.
- Remove DNM and Graph Walk `-o` from the target CLI and test plan.
- Produce a change report for each transformation.
- Record PoC result status in the manifest rather than the 15-column core.
  Use `processing_status=poc-with-errors`, counts and a diagnostic-report
  reference when model errors remain.
- Make all three transformation tools usable from the command line and test
  them with fixed fixtures.
- Apply the new contracts from taxonomy version `2026-12-31` and identify
  legacy/new artifacts by manifest contract name and version.

Exit condition: a clean checkout regenerates identical BSM and LHM outputs,
and a property removed with multiplicity `0` is absent from the BSM, LHM/HMD
and generated taxonomy.

## Phase 5 — Dual syntax binding

- Generate the Tuple binding as a compatibility reference.
- Define the OIM cube pattern for repeated classes and parent-child levels.
- Define primary items, dimensions, domains, defaults, closed/open behavior and
  target roles.
- Generate JSON metadata and CSV templates from the same profile manifest.
- Add deterministic tuple-path ↔ semantic-path ↔ OIM-aspect mapping.

Exit condition: equivalent Tuple and xBRL-CSV examples map to the same semantic
records without manual interpretation.

## Phase 6 — Domain pilots

Implement small vertical slices before broad CCL import:

1. UADC_PoC EN 16931 vendor invoice;
2. LedgerExplorer purchase order to invoice to ledger linkage;
3. statistical observation linked to source transactions.

Each pilot includes source message mapping, profile manifest, generated
taxonomy, examples, validation rules and round-trip comparison.

Exit condition: all three pilots pass semantic, XBRL and OIM validation.

Consumer cutover follows `docs/workspace-integration.md`; the provider never
overwrites a consumer LHM without a completed crosswalk and shadow comparison.

## Phase 7 — Governance and publication

- Establish the Shared core change process and Aligned registry review.
- Define namespace/version/deprecation policy.
- Publish package manifests and catalog resolution.
- Add CI for XML Schema, linkbase, OIM metadata, CSV, mapping and reproducible
  generation.
- Publish Working Draft releases only after rights and conformance review.

Exit condition: a tagged package is reproducible, traceable and independently
validated.
