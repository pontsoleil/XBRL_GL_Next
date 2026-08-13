**English** | [日本語](README_ja.md)

# Tools

This directory contains the canonical Python tools used to reproduce the XBRL GL Next semantic-model pipeline and to generate the sample Tuple and OIM taxonomy package.

The XBRL GL Next Requirements Specification and Taxonomy Framework are authoritative. These scripts are reference implementations used to execute and test those requirements; they do not replace the Framework.

## Contents

```text
tools/
├─ semantic/
│  ├─ specialisation.py
│  ├─ graphwalk.py
│  ├─ post_graphwalk.py
│  └─ validate_lhm.py
└─ taxonomy/
   └─ xBRLGL_TaxonomyGenerator.py
```

### `semantic/specialisation.py`

Reads one or more canonical 15-column FSM CSV files, applies **Specialisation**, and generates the 16-column BSM. It processes inheritance, additions, overrides and deletion directives defined by Specialisation Associations and produces the BSM used by Graph Walk.

```text
py tools/semantic/specialisation.py -h
```

### `semantic/graphwalk.py`

Generates the canonical 18-column **candidate LHM** from a 16-column BSM and one or more supplied root Classes. Graph Walk traverses Associations deterministically and produces the initial `local_name`, `xpath`, and diagnostics.

```text
py tools/semantic/graphwalk.py -h
```

### `semantic/validate_lhm.py`

Checks the format and consistency conditions of an 18-column LHM. It does not replace human semantic review.

```text
py tools/semantic/validate_lhm.py -h
```

### `semantic/post_graphwalk.py`

Processes the human-reviewed 18-column LHM and generates one formal HMD-for-taxonomy CSV for each effective level-1 root. It preserves the reviewed `local_name` and `multiplicity`, regenerates `xpath`, validates the formal output specification, and may issue diagnostics and `manifest.csv`.

```text
py tools/semantic/post_graphwalk.py -h
```

### `taxonomy/xBRLGL_TaxonomyGenerator.py`

Generates the complete XBRL GL Next Tuple and OIM taxonomy package from one `LHM_for_taxonomy` directory. The formal HMD CSV files directly under that directory are the taxonomy-generation inputs. `manifest.csv`, when present, is an execution-confirmation artifact and does not determine taxonomy content.

```text
py tools/taxonomy/xBRLGL_TaxonomyGenerator.py -h
```

Example from the repository root:

```text
py tools/taxonomy/xBRLGL_TaxonomyGenerator.py semantic-model/LHM_for_taxonomy \
  -b <empty-output-directory> \
  -n http://www.xbrl.org/int/gl/plt/2026-12-31
```

The output directory must be empty.

## Processing sequence

```text
FSM.csv + FSM_btx.csv
        |
        | Specialisation
        v
      BSM.csv
        |
        | Graph Walk
        v
 LHM_candidate.csv
        |
        | human semantic review
        v
XBRL_GL_Next_LHM_reviewed.csv
        |
        | Post-Graph Walk
        v
LHM_for_taxonomy/*.csv
        |
        | Taxonomy Generator
        v
taxonomy/  (Tuple + OIM)
```

The candidate-LHM to reviewed-LHM transition is a human-review boundary and must not be replaced by automatic regeneration or checksum equality.

## Validation and editing policy

Corresponding regression and package checks are under [`../tests/`](../tests/). Do not hand-edit generated semantic-model or taxonomy artifacts merely to make a test pass. Correct the responsible model or processing stage, regenerate downstream artifacts, and rerun validation.
