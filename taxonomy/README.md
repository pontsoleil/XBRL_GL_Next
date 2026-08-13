**English** | [日本語](README_ja.md)

# XBRL GL Next sample taxonomy

This directory contains the generated XBRL GL Next sample taxonomy package for taxonomy version `2026-12-31`.

The version date `2026-12-31` reflects the current project plan to complete XBRL GL Next and publish the taxonomy within 2026. It is used as the planned version date for the generated taxonomy package and does not indicate that the taxonomy has already been approved for public release.

The package is generated deterministically from the formal HMD files under `../semantic-model/LHM_for_taxonomy/` by `../tools/taxonomy/xBRLGL_TaxonomyGenerator.py`. It contains XBRL 2.1 Tuple and OIM-compatible realisations of the same reviewed semantic model.

## Package overview

```text
taxonomy/
├─ gen/
│  └─ gl-gen-2026-12-31.xsd
├─ btx/
├─ bus/
├─ cor/
├─ lnk/
├─ taf/
├─ tuple/
│  ├─ cor_accountingEntries/
│  └─ btx_businessTransactions/
└─ oim/
   ├─ cor_accountingEntries/
   └─ btx_businessTransactions/
```

The formal generated taxonomy package contains **56 files**. Repository documentation such as `README.md` and `README_ja.md` is not included in that count.

## Module-level palette components

Each current module directory (`btx`, `bus`, `cor`, `lnk`, `taf`) contains reusable module-level palette components shared by the Tuple and OIM bindings.

```text
<module>-2026-12-31.xsd
<module>-pre-2026-12-31.xml
label/<module>-lab-en-2026-12-31.xml
label/<module>-lab-ja-2026-12-31.xml
```

These module-level components provide reusable taxonomy concepts, labels and presentation relationships. The same semantic modules are used by both bindings. Binding-specific structures are assembled separately for Tuple and OIM.

## Tuple entry points

Use one of these schemas as the Tuple DTS entry point:

```text
tuple/cor_accountingEntries/cor-all-2026-12-31.xsd
tuple/btx_businessTransactions/btx-all-2026-12-31.xsd
```

The HMD-specific `*-content-2026-12-31.xsd` schemas provide the effective structural ComplexTypes for the selected Tuple DTS. A module schema is a palette component and is not the validation boundary by itself; validate from the HMD-specific Tuple entry point.

## OIM entry points

Use one of these schemas as the OIM taxonomy entry point:

```text
oim/cor_accountingEntries/cor-all-oim-2026-12-31.xsd
oim/btx_businessTransactions/btx-all-oim-2026-12-31.xsd
```

Their dimensional definition linkbases are:

```text
oim/cor_accountingEntries/cor-all-dim-2026-12-31.xml
oim/btx_businessTransactions/btx-all-dim-2026-12-31.xml
```

The OIM binding uses primary items, closed hypercubes and typed dimensions to represent Class occurrence scopes. Its DTS does not discover Tuple content schemas.

## How to use the taxonomy

For inspection or validation, start from one of the four HMD-specific entry points above rather than from an individual module schema. Sample reports are under [`../ids/`](../ids/).

To regenerate the package from the repository root:

```text
py tools/taxonomy/xBRLGL_TaxonomyGenerator.py semantic-model/LHM_for_taxonomy \
  -b <empty-output-directory> \
  -n http://www.xbrl.org/int/gl/plt/2026-12-31
```

## Validation baseline

Accepted 2026-08-12 baseline:

- formal generated taxonomy files: 56
- local references checked: 3,821
- unresolved local files: 0
- unresolved local fragments: 0
- dimensional locators checked: 850
- static package-checker failures: 0
- Arelle 2.44.1 taxonomy entry points: 4/4, error 0 / warning 0
- XMLSpy GUI: Tuple and OIM DTS checked

Static checker:

```text
py tests/check_generated_package.py taxonomy
```

## Editing policy

This directory contains generated taxonomy artifacts. Do not hand-edit generated taxonomy files as a normal maintenance procedure. Changes should originate in the reviewed semantic model, formal HMD, or taxonomy generator as appropriate, followed by deterministic regeneration and validation.
