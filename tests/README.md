**English** | [日本語](README_ja.md)

# Tests

This directory contains the retained automated checks for the XBRL GL Next semantic pipeline and generated taxonomy package.

The tests support implementation conformance and regression control. The Requirements Specification and Taxonomy Framework remain the authoritative specification.

## Contents

```text
tests/
├─ README.md
├─ README_ja.md
├─ test_specialisation.py
├─ test_graphwalk.py
├─ test_semantic_pipeline.py
├─ test_v5_taxonomy_generator.py
└─ check_generated_package.py
```

### `test_specialisation.py`

Tests the FSM-to-BSM **Specialisation** conversion, including canonical Specialisation Association handling, normalization of the supported legacy spelling `Specialization`, deletion behaviour, and deterministic BSM output.

### `test_graphwalk.py`

Tests the 16-column BSM to 18-column candidate-LHM **Graph Walk** conversion, including deterministic traversal from supplied roots, `source_bsm_id` reuse diagnostics, `local_name` and `xpath` generation, and collision diagnostics.

### `test_semantic_pipeline.py`

Tests the end-to-end lifecycle from FSM through BSM, candidate LHM, reviewed LHM, HMD-for-taxonomy and taxonomy generation. The candidate-LHM to reviewed-LHM transition is a human-review boundary; the test does not replace that review.

### `test_v5_taxonomy_generator.py`

Regression tests for the formal taxonomy generator, including the 18-column HMD input specification, non-use subtree handling, multiple HMDs, Tuple/OIM separation, binding-specific module presentation, OIM `p_` Class primary items, and deterministic generation.

### `check_generated_package.py`

Standalone static checker for the accepted formal 56-file taxonomy package. It checks package structure, local references, locator fragments, Tuple/OIM DTS separation, binding-specific module presentation, OIM module schemas, dimensional locators, and duplicate locator/presentation-arc groups.

Repository documentation files such as `taxonomy/README.md` and `taxonomy/README_ja.md` are not part of the formal 56-file taxonomy package.

## Running the tests

From the repository root, with `pytest` installed:

```text
py -m pytest tests
```

Accepted 2026-08-12 baseline:

```text
63 passed
```

The pass count is informative; the essential acceptance condition is zero failures and zero collection/runtime errors.

Run the package checker separately:

```text
py tests/check_generated_package.py taxonomy
```

Accepted package-checker baseline:

```text
formal taxonomy files: 56
local references checked: 3,821
unresolved local files: 0
unresolved local fragments: 0
dimensional locators checked: 850
failures: 0
```

## External validation

The Python tests do not replace XBRL-processor validation. The accepted 2026-08-12 baseline also included:

- Arelle 2.44.1: four taxonomy entry points, error 0 / warning 0;
- Arelle 2.44.1: four sample instances, error 0 / warning 0;
- XMLSpy GUI review of the Tuple and OIM DTSs.

## When to run tests

Run relevant tests when changing a semantic-processing tool, formal semantic-model artefact, taxonomy generator, generated taxonomy, or a sample instance when report validation is affected. Before registering a change, run the complete retained suite and the package checker.

## Failure policy

Do not modify generated artefacts merely to make a test pass. Identify whether the failure belongs to the semantic model, processing tool, taxonomy generator, test expectation, or sample data; correct the responsible source and rerun downstream checks.
