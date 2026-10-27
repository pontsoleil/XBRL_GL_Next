**English** | [日本語](README_ja.md)

# XBRL GL Next Tavi PoC — Full and HMD-view taxonomies

## Current HMD View screen acceptance — 13 October 2026

**Single Account Date r2 HMD View: HMD View screen display: PASS (User-confirmed, 2026-10-13).** The user confirmed the Arelle Structured Tidy Data screen display. This updates the previous NOT VERIFIED state for `instance/tavi-inst-hmd-view.json` with the Single Account Date r2 taxonomy and `instance/tavi-inst.csv` identified below.

CSV instance loading and 24 facts correspondence remain **PASS (existing evidence)** for the original fixed input set; the named metadata entry point has the previously approved taxonomy-reference-only change. Formal Arelle validation is **OUT OF SCOPE**; B5 remains a **SEPARATE ISSUE**. No Arelle run, validation, new execution log or screenshot was produced for this update. Taxonomy, CSV, metadata and HTML bytes are unchanged.

The confirmation identifies this registered HMD View set. No contemporaneous GUI input-path/SHA capture was supplied; the recorded SHA-256 values identify the registered files, not an independently captured GUI runtime. The earlier screenshot belongs to the legacy minimal example and is not reused as HMD View display evidence. This PASS does not apply to a different metadata/taxonomy/CSV combination.

The registration-time NOT VERIFIED statements below are retained as history. This section supersedes them only for the named HMD View entry point; the original profile metadata and Full cases retain their separate evidence boundaries.

This package distinguishes a small Single Account learning example (A) from the Full Accounting Entries HMD example (B). These are documentation cases, not runtime Profile settings. Canonical registration and Arelle load/display acceptance are recorded separately. Formal XBRL/OIM validation is outside the load/display acceptance scope.

## Canonical instance entry points

Both entry documents use the shared `instance/tavi-inst.csv` (279 bytes, SHA-256 `63c6103e07f0f0d5ae57a6c7bec5325d83b7ad837b0bd9f69da7b63b7f8cbcec`). Open the corresponding JSON in Arelle.

| Metadata | Selected Canonical taxonomy | Purpose |
|---|---|---|
| [instance/tavi-inst.json](instance/tavi-inst.json) | [taxonomy/tavi-tax.json](taxonomy/tavi-tax.json) | Simple Tavi definition; preserved unchanged |
| [instance/tavi-inst-hmd-view.json](instance/tavi-inst-hmd-view.json) | [Single Account Date r2 view taxonomy](profiles/single-account-date-r2/taxonomy/Tavi_JournalEntries_SingleAccount_Date_r2_candidate.json) | HMD-view-derived definition |

The HMD-view metadata is 1934 bytes, SHA-256 `00813144dea865de953de9bdfe0e2fe40072a431d287605fa91a3397eead6bd9`. It is derived from the previously registered 1902-byte metadata with SHA-256 `849ff63ebf4b113f76cb0cdc5a3dbf87863d2ea97db9301a12027f776cbb30f6`. The sole content change is `/documentInfo/taxonomy/0`: `../taxonomy/Tavi_JournalEntries_SingleAccount_Date_r2_candidate.json` becomes `../profiles/single-account-date-r2/taxonomy/Tavi_JournalEntries_SingleAccount_Date_r2_candidate.json` so the new entry point resolves to the existing Canonical view taxonomy. Its CSV URL remains `tavi-inst.csv`; all namespaces, mappings, occurrence dimensions, entity, period, unit and decimals remain unchanged. The source metadata and profile file set are preserved. Source and revised SHA differ; the revised working candidate and Canonical copy have matching SHA.

This registers a named entry point for the same view, not a new taxonomy or runtime Profile setting. The original input set has saved load/24-fact correspondence PASS. No Arelle execution was repeated for the new entry point; only the unchanged semantic fields, taxonomy/CSV SHA and Canonical relative references were checked. View-specific screen display remains NOT VERIFIED. Full v3 is a third, separate preserved taxonomy; neither entry document references it. Full-taxonomy Table Templates remain excluded.

## Current scope

The full taxonomy is defined from the complete HMD. The view taxonomy is defined from a selected HMD view; the CSV example belongs to that view and its own JSON metadata. These are distinct semantic models. The user's latest instruction excludes Table Templates corresponding to Full taxonomies from Canonical registration. No Full-template CSV or JSON is copied, generated or repaired.

| Case | Purpose | Current Canonical state |
|---|---|---|
| Single Account Date r2 HMD view | Explain the selected journal/Detail/account structure and interpret the example CSV | REGISTERED: unchanged view taxonomy + dedicated metadata + CSV |
| Full Accounting Entries v3 | Preserve the HMD-derived GL Next taxonomy | Taxonomy REGISTERED and unchanged; corresponding Table Template/instance scaffold EXCLUDED |
| Full Accounting Entries Date r2 | Preserve the later Date-definition Candidate as a distinct version | WORK Candidate NOT REGISTERED; Full Table Template registration EXCLUDED |

Full v3 already has a separate `accountingEntriesV3` Table Template and CSV scaffold in WORK. In the accepted corrected package, `tavi-inst-v3.json` references Full v3 directly and its matching `tavi-inst-v3.csv`. It has 764 columns and zero data rows. That **Table Template r2** revision is not the later **Full Accounting Entries Date r2** taxonomy. The pair is preserved as evidence, not registered or used as the view's populated CSV. The excluded scaffold is preserved as historical WORK evidence, not as a runtime input of this registered package. Its saved empty-instance load succeeds; screen display remains NOT VERIFIED.

The previous proposal to prepare a Full Date r2 metadata/CSV set is superseded by the exclusion decision. The historical missing-metadata HOLD is retained in earlier WORK reports. It is not an instruction to generate or register a Full Table Template.

## View registration and Full Date r2 history

| Item | A. Single Account Date r2 | B. Full Accounting Entries Date r2 |
|---|---|---|
| Purpose | Explain CSV interpretation with a small standalone Tavi taxonomy | Represent the Accounting Entries HMD in Tavi |
| Version | 2026-10-12-single-account-Date-r2-candidate | 2026-10-12-header-entry-date-Date-r2-candidate |
| Canonical registration | REGISTERED as a three-file example | NOT REGISTERED; Full Table Templates EXCLUDED by latest instruction |
| Instance load | PASS, saved 12 October evidence reused | NOT YET VERIFIED; Phase A tested the taxonomy only |
| Screen display for the exact Date r2 set | NOT YET VERIFIED | NOT YET VERIFIED |
| Combined load/display acceptance | NOT YET VERIFIED | NOT YET VERIFIED |
| Formal Arelle validation | OUT OF SCOPE | OUT OF SCOPE |
| B5 | SEPARATE ISSUE for the saved A execution | No failure or PASS transferred from A |

### A — registered file set

Open [A's OIM JSON metadata](profiles/single-account-date-r2/instance/tavi-inst-nine-column-Date-r2-candidate.json) in Arelle. It references the paired CSV and standalone taxonomy through unchanged relative paths.

| Role | Path relative to this directory | Bytes | SHA-256 |
|---|---|---:|---|
| taxonomy | `profiles/single-account-date-r2/taxonomy/Tavi_JournalEntries_SingleAccount_Date_r2_candidate.json` | 17200 | `5c78270b3fb9e3ed57f5ffb3b97a2f7a5694d11f68728a57b650d5a73890c80e` |
| csv | `profiles/single-account-date-r2/instance/tavi-inst.csv` | 279 | `63c6103e07f0f0d5ae57a6c7bec5325d83b7ad837b0bd9f69da7b63b7f8cbcec` |
| metadata | `profiles/single-account-date-r2/instance/tavi-inst-nine-column-Date-r2-candidate.json` | 1902 | `849ff63ebf4b113f76cb0cdc5a3dbf87863d2ea97db9301a12027f776cbb30f6` |

The standalone taxonomy contains ten concepts, seven types, two dimensions, two domains, two cubes, one network and forty labels; it imports no Full taxonomy. `cor:headerEntryDate` uses `xs:date`. CSV dates remain `YYYY-MM-DD`; the OIM period is independent.

The saved 12 October populated run loaded 24 native facts and matched all nonempty source cells, Header/Detail occurrences, entity, period, JPY and decimals. No GUI execution was recorded for this exact Date r2 set. The later user screenshot shows the legacy minimal concept names (`cor:entryNumber`, `cor:accountCode`); its input path/SHA was not captured. The 19:58 HOLD-release decision and 20:04 scope decision therefore do not establish A's Date r2 screen-display PASS. No test was repeated for registration.

### B — preserved Full Date r2 Candidate

The preserved Full Date r2 source taxonomy is a historical WORK Candidate outside this registered package; 621029 bytes; SHA-256 `c0aa1f2ae861a1f594938a762adb63784a30013c8c95b10e732c799d16393936`. This candidate retains 399 concepts, 353 datatypes, 44 dimensions, 45 domains, 46 cubes, one network and 1594 labels. Phase A provides taxonomy-load evidence, not CSV-instance display acceptance.

The earlier registration gate did not identify dedicated Full Date r2 metadata; that historical result is preserved. The latest instruction now excludes Full-taxonomy Table Templates from registration. No Full Date r2 metadata is created or copied, and its taxonomy remains a WORK Candidate. View-instance PASS is not transferred to this Full model. Full v3 has its own separate existing scaffold, described above; the two versions are not interchangeable.

### Why identical CSV bytes do not imply identical cases

The CSV stores physical values; each JSON metadata file maps its columns and occurrences into the selected taxonomy. A's CSV is byte-identical to the legacy minimal CSV, but A maps `entryNumber` to `cor:entryId`, `accountCode` to `cor:accountNumber`, and `entryDate` to `cor:headerEntryDate`. The legacy metadata maps those columns to different concepts and a different namespace. Matching CSV bytes do not make the view taxonomy interchangeable with either Full taxonomy. Tests belong to the exact three-file set.

## Acceptance and separate validation issue

Both instance load and Arelle screen display must be PASS for combined load/display PASS. Formal validation errors, warnings and validator exceptions do not determine that result. Known B5 remains a separate validation-route issue; no fix or formal validation was performed in this registration task. Missing case-specific screen evidence is reported as unverified, without changing the previous successful legacy case.

Historical registration, integrity and acceptance records are retained in WORK, not required as runtime inputs. A's version/filename retains `candidate` because its bytes were copied unchanged; the three-file table above identifies its registered example role. This does not establish B's screen-display PASS.

## Preserved v3 and legacy minimal example

The previously registered `taxonomy/XBRL_GL_Next_Tavi_AccountingEntries_v3.json` is Full HMD-derived v3, SHA-256 `c5a22efd355f3184a6b308f7e6a052621bae401f955c619df8f5c783804db5b1`. It is distinct from Full Date r2 and is preserved byte-for-byte. The existing `instance/tavi-inst.json` references `../taxonomy/tavi-tax.json`, not Full v3. Its CSV/JSON pair and the minimal taxonomy are also unchanged.

The following historical instructions continue to apply to the preserved legacy case. The existing patches and v3 acceptance records are retained. Current README/manifest changes and A's Date r2 example have not been committed or pushed to Official GIT. The 11 October publication is a separate saved baseline.

---

## Legacy PoC instructions

This proof of concept represents Header and Detail accounting entries with a Tavi/OIM taxonomy and an xBRL-CSV metadata + CSV report. Three Arelle OimTaxonomy patches provide native fact loading, a transposed Structured Tidy Data view reconstructed from the loaded model, and the selected label language in taxonomy views.

This is a first-publication candidate for a fresh installation at the specified Arelle base. It is experimental and does not claim full specification conformance, an upstream Arelle release, or general compatibility with other Arelle versions.

## Run the PoC

1. Obtain a separate, clean Arelle checkout at public base `0c773d6f79681caf598aded5ccb3812bbb0b9b28`.
2. Verify the supplied file hashes and apply these patches in order:
   1. `arelle-oimtaxonomy-tavi-poc.patch`: accepted loader, DTS, native xBRL-CSV and original Structured Tidy Data implementation.
   2. `0010-oim-taxonomy-structured-tidy-transposed-view.patch`: transposed Structured Tidy Data and Item/native-fact Properties selection.
   3. `arelle-oimtaxonomy-label-language-additional.patch`: selected label language for taxonomy views.
3. Follow [APPLY_PATCH.md](arelle/APPLY_PATCH.md) for the exact checkout, patch, Python/Tk prerequisite, hash and plug-in instructions.
4. From the new Arelle checkout, start the GUI:

   ```bash
   .venv/bin/python arelleGUI.pyw
   ```

   Enable **OIM Taxonomy** through **Help → Manage plug-ins**, as described in the guide.
5. Use **File → Open** to inspect each taxonomy listed below. For the minimal report example, open [instance/tavi-inst.json](instance/tavi-inst.json) as the entry point.

## Package

- [taxonomy/tavi-tax.json](taxonomy/tavi-tax.json): minimal Header/Detail taxonomy, with 7 concepts and 2 cubes. The supplied minimal metadata/CSV example uses this taxonomy.
- [taxonomy/XBRL_GL_Next_Tavi_AccountingEntries_v3.json](taxonomy/XBRL_GL_Next_Tavi_AccountingEntries_v3.json): full HMD-derived Accounting Entries taxonomy, with 399 concepts, 44 dimensions, 45 domains, 46 cubes and 1 network. It has no Groups definitions or Table Templates.
- [instance/tavi-inst.json](instance/tavi-inst.json) and [instance/tavi-inst.csv](instance/tavi-inst.csv): existing minimal report example; open the metadata JSON.
- [Patch guide](arelle/APPLY_PATCH.md): fresh-install procedure for all three patches.
- Historical package-integrity and acceptance records are retained in WORK; they are not runtime inputs. The [patch guide](arelle/APPLY_PATCH.md) contains the installation sequence and source-hash conditions.
- Historical v3 datatype-provenance and full-DTS acceptance records are retained in WORK, separately from the taxonomy itself.
- [Original expected results](expected/STRUCTURED_TIDY_DATA.md) describe the historical layout before 0010; that nine-column layout is not the final transposed layout. Historical cumulative-patch acceptance is retained in WORK.

The taxonomy, instance and patch bytes are preserved. The final minimal report view has nine Item rows and six occurrence columns, with native fact/Properties links.

## Published static HTML demonstrations

- [Simple Tavi Viewer](https://pontsoleil.github.io/XBRL_GL_Next/tavi-inst.html)
- [HMD View Viewer](https://pontsoleil.github.io/XBRL_GL_Next/tavi-inst-hmd-view.html)

These existing pages display the Table Template and Tavi taxonomy JSON sources alongside a transposed CSV. Opening them does not require a retired local HTML-generation script and does not perform formal XBRL/Tavi validation. Native Arelle fact/Properties handling is a separate implementation. Canonical registration, GitHub publication, static display acceptance and formal validation remain distinct.

## Development baseline

The accepted development repository used branch `work/oim-taxonomy-tavi` and these commits:

- Cumulative implementation: `f8f50ee1d06a12f2e9798437c66e2d360514d6be`.
- 0010: `7fe66c11cda8f23d60149cb119e3646f4a508fe3`.
- Labels / final development HEAD: `d19d2e7ad369f3356746252d1f63d808ed4281cc`.

Applying the distribution patches reproduces the documented source contents and SHA-256 values. It does not create those Git commit IDs. Saved native and GUI acceptance is reused; the first-publication documentation candidate has received static checks only.

## macOS GUI operation

Before interacting with tabs, make the Arelle window active by clicking inside it. Users observed that a direct Cubes-tab click left Groups selected, whereas clicking inside the window before clicking Cubes allowed the switch. Whether activation or focus actually changed, and the Tk/macOS runtime cause, remain unconfirmed.

For v3, an empty **XBRL Groups** view is expected because there are no Groups definitions. Inspect **XBRL Networks** and **XBRL Cubes**. For the minimal taxonomy, Networks is empty and Cubes should contain `cor:entryHeaderCube` and `cor:entryDetailCube`.
