# ADR-0004: Disposition of the ChatGPT generator and model review

- Status: Accepted
- Date: 2026-07-25

## Terminology amendment (2026-07-28)

This ADR preserves the original review wording as historical evidence. For the
current architecture, Graph Walk produces LHM only. HMD is a message-level
subset selected from LHM during binding. References below to `LHM/HMD` do not
define a combined Graph Walk output contract and are superseded for terminology
by ADR-0006.

## Context

The following review artifacts were evaluated:

- `docs/ChatGPT/XBRL_GL2.0定義改訂時の考慮事項.md`
- `docs/ChatGPT/XBRL_GL_Next_タクソノミ生成スクリプト改良点.md`
- `docs/ChatGPT/xBRLGL_TaxonomyGenerator.py`
- `docs/ChatGPT/xBRL_GL2.0_text2025-12-26.xlsx`
- `docs/ChatGPT/xBRL_GL2.0_text2025-12-26_改訂版.xlsx`

The reviewed script is byte-identical to
`tools/taxonomy/xBRLGL_TaxonomyGenerator.py`. The revised workbook contains
FSM, BSM and LHM sheets plus review, issue and architecture sheets.

The review was judged against the validated dual-support taxonomy fixed by
ADR-0003 and against the current Shared, Aligned and Distinct governance
definitions.

## Confirmed workbook improvements

The revised LHM contains 28 effective rows. Inspection confirmed:

- zero attribute rows with a missing datatype;
- zero duplicate semantic paths;
- zero duplicate abbreviation paths;
- zero semantic paths outside the adopted namespace-neutral lower-camel path
  syntax;
- zero missing `lhm_level` values; and
- zero unexpected `instance` values.

These improvements are accepted as input-quality work. They do not make the
revised workbook the authoritative source. The authoritative pipeline remains
FSM to BSM to LHM/HMD, and derived LHM fields must be reproducible from the
upstream model and profile rules.

## Issue disposition

| Issue | Disposition | Decision |
| --- | --- | --- |
| ISS-001 namespace and version | Partially accepted | Pass namespace and version separately and validate the version date. The alleged extra quote in the current default namespace was not reproduced. Do not derive the version only from the last ten characters. |
| ISS-002 content schema assembly | Accepted | Make the generator reproduce the validated pattern: same-namespace module schema by `include`, dependent content schemas by `import`, with no duplicate effective declaration. |
| ISS-003 palette imports | Accepted with correction | Require complete DTS reachability. The palette may import a root content schema that closes the dependency graph; it need not directly import every content schema. |
| ISS-004 presentation reachability | Accepted with correction | Test that presentation networks are reachable from the entry point. Do not add duplicate direct palette references when imported module schemas already reference their presentation linkbases. |
| ISS-005 XML output safety | Accepted | Replace unescaped string concatenation with namespace-aware XML construction or a complete escaping layer. Test ampersands, angle brackets, quotes and line breaks. |
| ISS-006 language codes | Accepted | The local standard-label resource must use the configured language, such as `ja`, rather than the hard-coded `en`. |
| ISS-007 duplicate `xlink:label` | Not accepted as a validity defect | Reusing an XLink label for resources with different label roles can be valid and is present in the validated taxonomy. Separate resource labels may be adopted for generator clarity, but are not a conformance requirement. |
| ISS-008 Reference Association | Accepted | Do not discard `R` rows. First define reference semantics, identity and target resolution, then bind them through the `lnk` module, XBRL facts, footnotes or explicit custom arcroles as appropriate. |
| ISS-009 LHM columns | Confirmed | Keep `lhm_level` and `instance` in the generated LHM/HMD contract. Do not hand-maintain derived values independently of FSM/BSM transformation. |
| ISS-010 LHM datatype | Confirmed | Preserve the completed datatypes and validate every effective attribute against GEN and XBRL item types. |
| ISS-011 abbreviation path | Confirmed | Require profile-local uniqueness and fail on collisions. |
| ISS-012 semantic path | Superseded by ADR-0005 | Keep semantic paths namespace-neutral and syntax-independent. Generate `element` after Graph Walk; remove `xpath` from LHM/HMD and manage XML placement in the syntax binding. |
| ISS-013 underscore naming | Accepted | Do not encode inheritance in display names. Record superclass and specialization explicitly in FSM. Apply the inherited-property matching and multiplicity-zero deletion rules defined by the framework. |
| ISS-014 dimension design | Conditionally accepted | The validated typed-dimension design remains the baseline. Change a class to an explicit dimension, row identifier or other mechanism only when fact identity and drill relationships are demonstrated by profile tests. |
| ISS-015 period type | Deferred | The validated baseline uses `instant`. Do not change concepts to `duration` by inference. Add concept/profile period rules only with a documented semantic basis and migration tests. |
| ISS-016 amount unit | Accepted | Generate units from datatype and an explicit unit rule, not solely from an `Amount` name suffix. Test multiple transaction and reporting currencies. |
| ISS-017 metadata parameters | Accepted | Externalize entity, period, currency, decimals and other report parameters from taxonomy generation. |
| ISS-018 suffix lookup | Accepted | Replace suffix fallback with a stable full semantic ID and an explicit alias or migration table. Ambiguous matches are errors. |
| ISS-019 validation reporting | Accepted | Collect input errors and warnings into a deterministic report instead of terminating at the first independently detectable error. |
| ISS-020 post-generation validation | Accepted | Automate XML parsing, local-reference checks and Arelle validation. Keep XMLSpy as an independent validation check for release candidates. |
| ISS-021 PK multiplicity | Deferred | Do not force `0..1` to `1..1` without deciding whether the key is a business key or a technical row identifier. Define fact identity for every repeated class first. |
| ISS-022 SRCD migration | Accepted | Preserve the official 2017 QName as provenance and maintain an explicit mapping to the Next semantic ID, QName and presentation/definition parentage. |

## Corrections to the semantic review

The Shared, Aligned and Distinct examples in the review are not accepted
unchanged.

### Shared

Shared defines concepts and structures that can be used globally across
countries, regimes, industries and implementations. A concept from an
international public standard is not made Aligned merely because it originated
in CCL, UBL, CII or XBRL GL.

Globally reusable Party, Address, Contact, Period, Amount, Quantity, Document,
Reference, Tax and accounting-event structures are Shared candidates.
International-standard mappings and compatibility metadata may accompany the
Shared definitions.

### Aligned

Aligned maintains consistency with a regional or national standard, law,
regulation, or published industry standard that is not an international
standard. Japanese consumption-tax rules are therefore Aligned, not Distinct.
The applicable legal categories, rates, effective periods and rounding rules
belong in an Aligned package over the Shared Tax structure.

### Distinct

Distinct is limited to definitions specific to an enterprise, enterprise
group, product, bilateral trading relationship or closed user community.
XBRL GL Entry Header and Journal Entry concepts must not be classified as
Distinct merely because they are XBRL GL concepts.

## Summary Amount and lineage

The review's proposed Shared Summary Amount mixes amount meaning with
fact-level lineage. `Source Fact Set Reference` is not part of the effective
Summary Amount value structure. Put fact, source-document, calculation and
evidence relationships in the `lnk` module.

The Shared Summary Amount structure may contain globally reusable amount,
scope and calculation semantics. Accounting, invoice, payment, tax and
settlement code values are placed in the appropriate Shared international
profile or Aligned package according to their governing standard. Enterprise
codes remain Distinct.

## Consequences

- The revised workbook is retained as a reviewed design input, not promoted
  directly to authoritative LHM.
- The current generator remains a PoC until it reproduces the validated
  taxonomy graph and passes automated comparison and validation.
- Technical validity regressions are blocked by ADR-0003 tests.
- Semantic changes are made in FSM and profile extensions, then regenerated
  through BSM and LHM/HMD.
- Review issue status should be maintained against the corrected dispositions
  above rather than copied verbatim from the workbook.
