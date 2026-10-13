**English** | [日本語](README_ja.md)

# XBRL GL Next Tavi PoC

This proof of concept represents Header and Detail accounting entries with a Tavi/OIM taxonomy and an xBRL-CSV metadata + CSV report. Three Arelle OimTaxonomy patches provide native fact loading, a transposed Structured Tidy Data view reconstructed from the loaded model, and the selected label language in taxonomy views.

This is a first-publication candidate for a fresh installation at the specified Arelle base. It is experimental and does not claim full specification conformance, an upstream Arelle release, or general compatibility with other Arelle versions.

## Three Tavi taxonomies and two report definitions

The Simple, COR Full and HMD View taxonomies serve different purposes and are not interchangeable. These are documentation cases, not runtime profile settings.

Table 1 summarises the published taxonomy and report combinations.

Table 1 — Tavi taxonomy and report availability

| Case | Published taxonomy JSON | Instance CSV / JSON metadata | Static HTML viewer |
| --- | --- | --- | --- |
| Simple Tavi | [tavi-tax.json](taxonomy/tavi-tax.json) | Published [tavi-inst.json](instance/tavi-inst.json) and [tavi-inst.csv](instance/tavi-inst.csv) | [Simple Tavi Viewer](https://pontsoleil.github.io/XBRL_GL_Next/tavi-inst.html) |
| COR Full Accounting Entries | [XBRL_GL_Next_Tavi_AccountingEntries_v3.json](taxonomy/XBRL_GL_Next_Tavi_AccountingEntries_v3.json) | **None** | **None** |
| HMD View — Single Account Date r2 | [Tavi_JournalEntries_SingleAccount_Date_r2_candidate.json](taxonomy/Tavi_JournalEntries_SingleAccount_Date_r2_candidate.json) | Canonical-registered `tavi-inst-hmd-view.json` with the same CSV as Simple Tavi; the metadata is **not published as a standalone GitHub file** | [HMD View Viewer](https://pontsoleil.github.io/XBRL_GL_Next/tavi-inst-hmd-view.html) |

Simple Tavi illustrates basic taxonomy and Table Template definitions. COR Full represents the full HMD-derived COR Accounting Entries taxonomy. HMD View represents a selected purpose-specific view.

COR Full is a **taxonomy-only artefact**: no corresponding instance CSV, instance JSON metadata or HTML viewer is provided. The historical zero-data-row `accountingEntriesV3` Table Template scaffold and its CSV/JSON files are excluded from Canonical registration and publication; they are not Full instances in this package.

Simple and HMD View are two metadata/taxonomy combinations using the same Structured Tidy Data CSV, not two distinct CSV datasets. The HMD View metadata is Canonical-registered, and its Table Template and taxonomy sources are displayed in the published static viewer. This does not make the metadata available as an independent GitHub JSON file.

The published HMD View taxonomy matches the accepted Canonical bytes (SHA-256: `5c78270b3fb9e3ed57f5ffb3b97a2f7a5694d11f68728a57b650d5a73890c80e`). The `candidate` component is retained in its historical filename; registration records determine its accepted scope.

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
- [Manifest](validation/MANIFEST.json): first-publication candidate integrity, patch order, source hashes and acceptance references.
- [v3 manifest](validation/TAVI_ACCOUNTING_ENTRIES_MANIFEST_v3.json) and [v3 acceptance](validation/FULL_HMD_TAVI_V3_ARELLE_ACCEPTANCE.md): datatype provenance and saved full-DTS acceptance for the large taxonomy.
- [Cumulative-patch acceptance](validation/ACCEPTANCE.md) and [original expected results](expected/STRUCTURED_TIDY_DATA.md): historical acceptance before 0010; their original nine-column layout is not the final transposed layout.

The taxonomy, instance and patch bytes are preserved. The final minimal report view has nine Item rows and six occurrence columns, with native fact/Properties links.

## Tavi PoC — Structured Tidy Data Viewer

The Tavi PoC demonstrates how the same Structured Tidy Data CSV can be displayed using two different Tavi taxonomy definitions.

### Online Viewers

- **[Simple Tavi Viewer](https://pontsoleil.github.io/XBRL_GL_Next/tavi-inst.html)** — A basic example illustrating the relationship between a Tavi taxonomy, a Table Template, and a CSV instance.
- **[HMD View Viewer](https://pontsoleil.github.io/XBRL_GL_Next/tavi-inst-hmd-view.html)** — An example based on the XBRL GL Next HMD View, using the same CSV with a different taxonomy definition.

Each viewer provides two panels:

- **Left:** The original Table Template and Tavi taxonomy JSON sources, accessible through tabs.
- **Right:** The Structured Tidy Data CSV displayed in transposed form.

The pages are generated from Tavi instance JSON metadata using `tavi_inst_json_to_html.py`.

**Phase 1** provides self-contained static HTML without JavaScript. **Phase 2** is planned to introduce interactive Properties display based on the Table Template and taxonomy definitions.

These viewers are intended for demonstration and do not perform formal XBRL/Tavi validation.

Canonical registration, GitHub publication, static HTML display acceptance and formal XBRL/Tavi validation are distinct states. The viewers' source display is not formal validation evidence. The B5 validation issue remains a separate matter. HTML Phase 2 has not started; the native Arelle fact/Properties functionality described above is a separate implementation.

## Development baseline

The accepted development repository used branch `work/oim-taxonomy-tavi` and these commits:

- Cumulative implementation: `f8f50ee1d06a12f2e9798437c66e2d360514d6be`.
- 0010: `7fe66c11cda8f23d60149cb119e3646f4a508fe3`.
- Labels / final development HEAD: `d19d2e7ad369f3356746252d1f63d808ed4281cc`.

Applying the distribution patches reproduces the documented source contents and SHA-256 values. It does not create those Git commit IDs. Saved native and GUI acceptance is reused; the first-publication documentation candidate has received static checks only.

## macOS GUI operation

Before interacting with tabs, make the Arelle window active by clicking inside it. Users observed that a direct Cubes-tab click left Groups selected, whereas clicking inside the window before clicking Cubes allowed the switch. Whether activation or focus actually changed, and the Tk/macOS runtime cause, remain unconfirmed.

For v3, an empty **XBRL Groups** view is expected because there are no Groups definitions. Inspect **XBRL Networks** and **XBRL Cubes**. For the minimal taxonomy, Networks is empty and Cubes should contain `cor:entryHeaderCube` and `cor:entryDetailCube`.
