# Acceptance

Saved public cumulative-patch reproduction acceptance: PASS, 10 October 2026.

Public base: `0c773d6f79681caf598aded5ccb3812bbb0b9b28`.
Accepted target: `f8f50ee1d06a12f2e9798437c66e2d360514d6be`.
Patch SHA-256: `e27804957bad2ff26d92d86b6639e9fc55413a7677efcb89e870a215e737ae01`.

- Patch application from the public base: PASS.
- Scope: 8 files, 532 insertions and 23 deletions.
- Resulting source blobs match the accepted target: 8/8.
- Native report errors/warnings: 0/0; native facts: 24.
- Structured Tidy Data: 9 columns / 6 rows / all values PASS.
- Amount cell → native fact mapping: PASS; JPY / decimals=0 retained.
- GUI runtime and Structured Tidy Data tab: PASS.

The saved reproduction test inspected actual Tk widgets and the expected rows. Manual GUI cell → native XbrlFact → Properties acceptance is supplemental evidence. These statements do not claim a new GUI screenshot or a repeated manual GUI test.

For this publication candidate, taxonomy and CSV bytes are unchanged; metadata changes only the relative taxonomy and CSV references. JSON, relative paths, CSV values, patch integrity, document links and manifest integrity are checked separately. Native and GUI acceptance are reused; no duplicate Arelle execution is performed for packaging.

The candidate has not been committed, pushed or published. Development-stage patch history is intentionally omitted.

## Recorded acceptance values

```text
PUBLIC_PATCH_APPLY = PASS
PUBLIC_PATCH_FILES = 8
DIFF = 532 insertions / 23 deletions
TARGET_BLOB_MATCH = 8/8
NATIVE_ERRORS_WARNINGS = 0/0
NATIVE_FACTS = 24
STRUCTURED_TIDY_COLUMNS = 9
HEADER_ROWS = 2
DETAIL_ROWS = 4
TOTAL_ROWS = 6
ROW_VALUE_MATCH = PASS
CELL_NATIVE_FACT_MAPPING = PASS
JPY / decimals=0 = PASS
GUI_RUNTIME = PASS
STRUCTURED_TIDY_TAB = PASS
```
