# TEST RESULTS

## Scope and environment

- Execution date: 2026-08-19 (Asia/Tokyo)
- Part 1: `TaxonomyFramework/XBRL_GL_Next_Taxonomy_Framework_Part_1_General_rules.docx`
- Detailed specification: `tools/XBRL_GL_Next_Detailed_Program_Specification_2026-08-16.docx`
- Python 3.12.13; python-docx 1.2.0; lxml 6.1.1
- LibreOffice 26.2.5.2; Poppler/pdfinfo 26.05.0

## Inputs and outputs

| Artefact | SHA-256 |
| --- | --- |
| Part 1, unchanged | `3A356540FB8970368E082E6DE399F74B067AEE9164D9269D65B3C5CC50AA5B4A` |
| Detailed specification before edit / verified backup | `D23923F5DD2F876B8044533C9EE35F964D513388468245A0436E813F779867EB` |
| Detailed specification after edit | `51FB43F981C7C7ADFE9EF560114929392A25DC2C9868829C105BC8AB3959D3CD` |

## Test results

| Test | Expected | Actual | Result |
| --- | --- | --- | --- |
| Backup integrity | Source and backup hashes equal before edit | Both `D23923...67EB` | PASS |
| Exact wording | Old sentence absent; approved sentence occurs once | Old 0, new 1 | PASS |
| Review contract | Only `local_name` and permitted multiplicity restrictions are changeable; `name` and `semantic_path` expressly immutable | Confirmed in revised sentence | PASS |
| DOCX package scope | Only `word/document.xml` differs | Exactly one changed package part | PASS |
| Package structure | Same part names before/after | Equal | PASS |
| Document structure | Paragraph/table/section/shape counts unchanged | 116/22/1/0 before and after | PASS |
| Media | Embedded media unchanged | No media differences | PASS |
| Part 1 preservation | Part 1 SHA-256 remains the accepted value | `3A3565...B4A` | PASS |
| Render | Before and after render with equal page counts | 11 pages each | PASS |
| Render containment | Only the page containing section 5.2 changes | Pages 1–5 and 7–11 byte-identical; page 6 changed | PASS |
| Visual QA | Every final PNG clean at 100% | 11/11 pages inspected; no clipping, overlap, broken table, missing glyph, or pagination defect | PASS |

## Commands and reproducibility

- `audit_program_spec.py <backup> <edited> <part1>` performs the package, structure, wording, hash, and Part 1 preservation checks.
- `render_docx.py <docx> --output_dir <dir> --emit_pdf` rendered the before and after versions.
- Per-page SHA-256 comparison confirmed that only page 6 changed visually.
- `Get-FileHash -Algorithm SHA256` recorded source and output hashes.

## Errors and warnings

- The first edit attempt created a complete replacement package but Windows rejected atomic `os.replace` with `WinError 5`. The script deleted its temporary file in `finally`; the target hash remained unchanged. The second edit used the verified backup-protected direct-write path and succeeded.
- Poppler prints its version to stderr, which PowerShell reports as `NativeCommandError`; rendering completed successfully with exit code 0 and all expected PNG/PDF files.

## Not run and residual risk

- Graph Walk, Post-Graph-Walk, HMD generation, taxonomy generation, Arelle, XMLSpy, and semantic-model tests were not rerun because neither Part 1 nor any executable/model/taxonomy artefact changed in this task.
- The detailed specification remains dated 2026-08-16; the user requested correction of its section 5.2 wording, not a document-date revision.

## Acceptance

**PASS.** The identified inconsistency is resolved, the Part 1 revision is unchanged, and the DOCX structure and rendering are clean.
