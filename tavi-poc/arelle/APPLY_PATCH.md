# Arelle OimTaxonomy — patch application

This guide installs the published Tavi PoC extension into a separate, clean Arelle source checkout. It does not imply general compatibility with other Arelle versions or establish formal specification conformance.

## Base and patches

Arelle base commit: `0c773d6f79681caf598aded5ccb3812bbb0b9b28`.

Apply the following three files **in order**, from the Arelle repository root:

| Order | Patch relative to `tavi-poc/arelle/patches/` | SHA-256 |
| --- | --- | --- |
| 1 | `arelle-oimtaxonomy-tavi-poc.patch` | `e27804957bad2ff26d92d86b6639e9fc55413a7677efcb89e870a215e737ae01` |
| 2 | `0010-oim-taxonomy-structured-tidy-transposed-view.patch` | `7e123da44b2a3e32d3d654dd52f131809c46c9ef75328168d4200100167d5eeb` |
| 3 | `arelle-oimtaxonomy-label-language-additional.patch` | `bd00e31dbd38e2c9dabd6f41e3b5362aef904863c0fcb2a2832efe4d3d30cefd` |

The first patch supplies the OimTaxonomy loader and DTS/report support; the second supplies the transposed Structured Tidy Data view and native-fact selection; the third supplies controller-selected label language. The combined changes affect nine Arelle source files.

## Prepare a separate checkout

Replace `<TAVI_POC_DIR>` with the absolute path to the published `tavi-poc` directory. Verify the patch file SHA-256 values above using the SHA-256 utility available on your platform.

```sh
git clone https://github.com/Arelle/Arelle.git Arelle-tavi-poc
cd Arelle-tavi-poc
git checkout --detach 0c773d6f79681caf598aded5ccb3812bbb0b9b28
git rev-parse HEAD
git status --porcelain
```

Before applying patches, HEAD must equal the specified base commit and the working tree must be clean.

```sh
git apply --check "<TAVI_POC_DIR>/arelle/patches/arelle-oimtaxonomy-tavi-poc.patch" && git apply "<TAVI_POC_DIR>/arelle/patches/arelle-oimtaxonomy-tavi-poc.patch"
git apply --check "<TAVI_POC_DIR>/arelle/patches/0010-oim-taxonomy-structured-tidy-transposed-view.patch" && git apply "<TAVI_POC_DIR>/arelle/patches/0010-oim-taxonomy-structured-tidy-transposed-view.patch"
git apply --check "<TAVI_POC_DIR>/arelle/patches/arelle-oimtaxonomy-label-language-additional.patch" && git apply "<TAVI_POC_DIR>/arelle/patches/arelle-oimtaxonomy-label-language-additional.patch"
```

Each `git apply --check` and `git apply` must exit successfully before proceeding. Do not edit patches or use `--3way` or `--reject` to bypass a failure. `git status --short --untracked-files=all` should show the nine changed source paths, including the new `arelle/plugin/OimTaxonomy/ViewStructuredTidyData.py`.

## Environment and use

Follow [ENVIRONMENT.md](ENVIRONMENT.md) to install dependencies using Tk-enabled Python 3.10 or later, launch the GUI and enable **OIM Taxonomy** via **Help → Manage plug-ins**.

Open the [Simple taxonomy](../taxonomy/tavi-tax.json) or [Full v3 taxonomy](../taxonomy/XBRL_GL_Next_Tavi_AccountingEntries_v3.json) individually, or open [Simple report metadata](../instance/tavi-inst.json) to inspect native facts. For the four independent current taxonomy models, use the [four-model reproduction guide](../README_REPRODUCE_4_MODELS.md).

Stop if checkout, patch verification, application, installation or taxonomy loading fails. Record the error; do not change the expected base, patches or file contents to claim the documented outcome. Loading a taxonomy is not the same as validating an instance.
