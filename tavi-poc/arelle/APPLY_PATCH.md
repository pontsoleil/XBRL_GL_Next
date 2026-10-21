# Arelle OimTaxonomy Tavi PoC — Patch Application Guide

## Purpose

This guide defines the first installation in a new Arelle checkout. The three supplied patches reproduce the adopted PoC source contents from one exact public base. General compatibility with other Arelle revisions is not claimed.

The existing MacBook development checkout already contains all three changes and must not be patched again. The commands below are instructions for a new checkout; they were not executed as part of this documentation task.

## Authority

Public Arelle base: `0c773d6f79681caf598aded5ccb3812bbb0b9b28`.

Table 1 — Required patch order and SHA-256

|Order|File in this package's arelle/patches directory|Bytes|SHA-256|
|---|---|---|---|
|1|arelle-oimtaxonomy-tavi-poc.patch|41779|e27804957bad2ff26d92d86b6639e9fc55413a7677efcb89e870a215e737ae01|
|2|0010-oim-taxonomy-structured-tidy-transposed-view.patch|7736|7e123da44b2a3e32d3d654dd52f131809c46c9ef75328168d4200100167d5eeb|
|3|arelle-oimtaxonomy-label-language-additional.patch|731|bd00e31dbd38e2c9dabd6f41e3b5362aef904863c0fcb2a2832efe4d3d30cefd|

Table 1 fixes the application order. The cumulative patch supplies the accepted loader/DTS, native CSV, object-index/bootstrap, Structured Tidy and QName-mapping changes. 0010 supplies the transposed view and selection links. Labels supplies the controller-selected label language.

Table 2 — Source correspondence with the development history

|After|Development commit with matching source contents|
|---|---|
|Cumulative patch|`f8f50ee1d06a12f2e9798437c66e2d360514d6be`|
|0010|`7fe66c11cda8f23d60149cb119e3646f4a508fe3`|
|Labels|`d19d2e7ad369f3356746252d1f63d808ed4281cc`|

Table 2 records the historical source correspondence. Patch application leaves the new checkout's HEAD at the public base; it does not create these development commits.

## Patch scope

All three files are Git-style unified diffs with `a/arelle/...` and `b/arelle/...` paths. Run `git apply` from the Arelle repository root, using its default path stripping.

The cumulative patch changes eight files. 0010 changes only `arelle/plugin/OimTaxonomy/ViewStructuredTidyData.py`. Labels changes only `arelle/plugin/OimTaxonomy/ViewXbrlTxmyObj.py`. There are nine distinct affected source files overall; no other implementation is supplied.

## Prepare a fresh checkout and verify the package

Replace the example package path with the absolute path to your extracted `tavi-poc` directory. It must contain the taxonomy and patch files described in Table 1.

```bash
export TAVI_POC_DIR="/absolute/path/to/tavi-poc"
cd "$TAVI_POC_DIR"
shasum -a 256 -c <<'EXPECTED_PACKAGE_SHA256'
19121e5b7938ef59f42960910aea1923dbf5297195bbc5369137aeb325559da3  taxonomy/tavi-tax.json
c5a22efd355f3184a6b308f7e6a052621bae401f955c619df8f5c783804db5b1  taxonomy/XBRL_GL_Next_Tavi_AccountingEntries_v3.json
e27804957bad2ff26d92d86b6639e9fc55413a7677efcb89e870a215e737ae01  arelle/patches/arelle-oimtaxonomy-tavi-poc.patch
7e123da44b2a3e32d3d654dd52f131809c46c9ef75328168d4200100167d5eeb  arelle/patches/0010-oim-taxonomy-structured-tidy-transposed-view.patch
bd00e31dbd38e2c9dabd6f41e3b5362aef904863c0fcb2a2832efe4d3d30cefd  arelle/patches/arelle-oimtaxonomy-label-language-additional.patch
EXPECTED_PACKAGE_SHA256
```

All five checks must report `OK`. On platforms without `shasum`, use an equivalent SHA-256 checker against the same values.

From a directory where a new checkout can be created:

```bash
git clone https://github.com/Arelle/Arelle.git Arelle-tavi-poc
cd Arelle-tavi-poc
git checkout --detach 0c773d6f79681caf598aded5ccb3812bbb0b9b28
git rev-parse HEAD
git status --porcelain
```

HEAD must be exactly `0c773d6f79681caf598aded5ccb3812bbb0b9b28` and status must be empty. Stop if either condition fails.

## Apply the patches

Keep this shell at the new Arelle repository root.

### Patch application verification

Apply the three published patches in the specified order to the designated Arelle base commit.

For each patch, both `git apply --check` and `git apply` must complete successfully with exit code 0.

If either command fails, stop the procedure. Do not modify the published patches to make them apply.

Raw SHA-256 verification of the resulting nine source files is not required for patch application.

Line-ending differences between platforms do not affect the patch application acceptance criteria.

After all three patches have been successfully applied, proceed to the documented dependency setup and functional verification steps.

### 1. Cumulative implementation

```bash
git apply --check "$TAVI_POC_DIR/arelle/patches/arelle-oimtaxonomy-tavi-poc.patch" &&
git apply "$TAVI_POC_DIR/arelle/patches/arelle-oimtaxonomy-tavi-poc.patch"
```

The cumulative patch supplies the loader, DTS, native CSV and Structured Tidy implementation across eight source files, corresponding to `f8f50ee1d`.

### 2. 0010 transposed Structured Tidy view

```bash
git apply --check "$TAVI_POC_DIR/arelle/patches/0010-oim-taxonomy-structured-tidy-transposed-view.patch" &&
git apply "$TAVI_POC_DIR/arelle/patches/0010-oim-taxonomy-structured-tidy-transposed-view.patch"
```

This patch updates `ViewStructuredTidyData.py` with the transposed view and selection links, corresponding to `7fe66c11`. The Labels source still has its pre-Labels content.

### 3. Labels

```bash
git apply --check "$TAVI_POC_DIR/arelle/patches/arelle-oimtaxonomy-label-language-additional.patch" &&
git apply "$TAVI_POC_DIR/arelle/patches/arelle-oimtaxonomy-label-language-additional.patch"
```

This patch updates `ViewXbrlTxmyObj.py` to use the controller-selected label language, corresponding to `d19d2e7a`.

## Check the nine changed source files

The three patches affect these nine distinct source files:

- `arelle/ModelDocument.py`
- `arelle/oim/Load.py`
- `arelle/plugin/OimTaxonomy/ValidateDTS.py`
- `arelle/plugin/OimTaxonomy/ViewStructuredTidyData.py`
- `arelle/plugin/OimTaxonomy/ViewXbrlTxmyObj.py`
- `arelle/plugin/OimTaxonomy/XbrlCube.py`
- `arelle/plugin/OimTaxonomy/XbrlDts.py`
- `arelle/plugin/OimTaxonomy/XbrlReport.py`
- `arelle/plugin/OimTaxonomy/__init__.py`

Run this at the Arelle repository root:

```bash
git status --short --untracked-files=all
```

The status must identify exactly the nine source paths listed above: eight modified tracked files and one new, untracked `ViewStructuredTidyData.py` introduced by the cumulative patch. `git apply` does not stage that new file; `git diff --name-only` alone would omit it. The checkout has patch changes in its working tree; a clean status is required before applying patches, not after applying them.

The saved base-to-cumulative reproduction and additional-patch static reconstruction checks establish the source correspondence. Existing acceptance records are reused; a new native or GUI test was not run for this guide.

## Python/Tk environment and GUI startup

The public base requires Python >= 3.10 in `pyproject.toml`. Choose a Python distribution with working Tk support. pip installation of Arelle does not supply a missing system/interpreter Tk runtime.

The verified MacBook development environment is Python 3.10.1, arm64, with Tcl/Tk 8.6.12. This is a recorded environment, not a requirement for those exact versions or proof that other combinations work. Dependency versions are not locked by this package.

After successful patch application, create a fresh virtual environment from the selected Tk-enabled Python:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install --upgrade pip
.venv/bin/python -m pip install -e .
.venv/bin/python -m pip check
.venv/bin/python arelleGUI.pyw
```

In the GUI, open **Help → Manage plug-ins**. Use **Browse** to select `arelle/plugin/OimTaxonomy/__init__.py` inside this new checkout. Confirm that **OIM Taxonomy** is enabled; use **Enable** if it is disabled, then **Close**. Follow a restart prompt if shown before loading a taxonomy. This menu/file path is defined by the inspected Arelle GUI implementation.

The startup command intentionally uses the GUI entry point directly. Plug-in activation is performed through the GUI manager.

## Open the two taxonomies

Use **File → Open** to open these package files individually:

1. [taxonomy/tavi-tax.json](../taxonomy/tavi-tax.json): inspect **XBRL Cubes** for `cor:entryHeaderCube` and `cor:entryDetailCube`. Its Networks definition count is zero.
2. [taxonomy/XBRL_GL_Next_Tavi_AccountingEntries_v3.json](../taxonomy/XBRL_GL_Next_Tavi_AccountingEntries_v3.json): inspect **XBRL Networks** and **XBRL Cubes**. **XBRL Groups** is expected to be empty because v3 has no Groups definitions.

For the minimal native-report/Structured Tidy example, open [instance/tavi-inst.json](../instance/tavi-inst.json). It references the minimal taxonomy and CSV. The v3 taxonomy contains no Table Templates and is not the taxonomy for that minimal report example.

Before using tabs on macOS, make the Arelle window active by clicking inside it. Users observed a tab-selection failure on a direct click and a successful switch after an interior click followed by a tab click. Actual activation/focus changes and the Tk/macOS cause were not measured; the PoC patches do not claim to fix that issue.

## Manifest and saved acceptance

[MANIFEST.json](../validation/MANIFEST.json) identifies the five registration files, supporting package files, patch order, final source hashes and development acceptance references. Recorded source hashes remain provenance identifiers; they are not additional patch-application acceptance conditions. The [v3-specific manifest](../validation/TAVI_ACCOUNTING_ENTRIES_MANIFEST_v3.json) retains its separate datatype mapping/provenance role.

The [cumulative acceptance](../validation/ACCEPTANCE.md) records the pre-0010 layout. The final minimal view is transposed: nine Item rows and six occurrence columns. 0010 headless/native mapping and user manual Properties acceptance, and Labels user manual English-label acceptance, are documented as reused evidence in the distribution manifest.

## Stop conditions

Stop at the first failed checkout, public-package hash check, patch check/application, dependency or source-scope check. Record the failing command and output. Do not continue to the next patch, edit a patch, use `--3way`/`--reject`, resolve conflicts manually or change the expected hashes and claim the documented result.

Stop if a package file or plug-in is missing, or taxonomy loading reports an error. Do not treat an empty v3 Groups tab alone as an error. No reset, cleanup or automatic recovery command is prescribed.

This procedure covers a fresh installation only. Successful documentation checks do not constitute a new GUI acceptance or public release.
