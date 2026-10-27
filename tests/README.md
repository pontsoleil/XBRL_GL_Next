# Reproduction and regression tests

These are **existing project tests**, not a claim that all run in a fresh clone or that all historical executions share the same acceptance baseline. Identify the relevant test's imports, source version, input fixtures, accepted expected outputs and external Arelle checkout before execution.

| Current checked-in test | Main purpose |
|---|---|
| `check_generated_package.py` | Package-level checks; determine the applicable input contract and dependencies before use |

Earlier `test_*.py` suites are historical WORK evidence and are not present in this Canonical snapshot. Do not treat their historical PASS as a fresh public-clone test result.

**Running tests:** Use the CLI and fixtures documented by each checked-in test/module and applicable package inventory; do not invent a single blanket command or assert PASS merely because files exist. Resolve any missing/non-public dependency first. Do not compare four independent model identities as if they must match.

**Four-model Tavi taxonomy reproduction:** Follow [`tavi-poc/README_REPRODUCE_4_MODELS.md`](../tavi-poc/README_REPRODUCE_4_MODELS.md) for separate generation and Arelle validation. The October 26 WORK acceptance review PASSED; a clean GitHub clone was **not** independently tested at the checked public snapshot. The legacy `verify_hmd_to_tavi.py` is a 401-row historic fixture check, not a universal 4-model check. Save new validation output to separate paths; do not replace accepted artifacts.
