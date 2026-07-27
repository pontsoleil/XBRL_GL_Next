# Copy report: collaborative-review framework documents

- Date: 2026-07-27
- Target branch: `rearchitecture/oim-taxonomy-2026`
- Target HEAD before copying: `65b85f999170cac1bd4bf1818efcabbec0e0c920`
- Copy status: completed, unstaged; DOCX files are currently ignored by Git

## Source

The source package was the WORK-checkout file:

`TaxonomyFramework/XBRL_GL_Next_revised_collaborative-review_documents_2026-07-27.zip`

ZIP SHA-256:

`C0B859C0F3E632A8E803DEF7F202BC2C5AC75CFA21C9853A4D981B2641976993`

The ZIP contained exactly the six DOCX files listed below. No other ZIP entry was copied.

## Consistency verification

The revised documents consistently state or apply the following approved PoC baseline:

1. FSM has 14 columns.
2. BSM has 15 columns, with `id` as the fifteenth column and no `element` column.
3. LHM has 17 columns.
4. BSM Class IDs use `XXnn`; property IDs use `XXnn-pp`, with additional sequence width when required for more than 99 properties.
5. HMD is excluded from the semantic model and introduced only as a structure derived for syntax binding from a specified LHM root Class.
6. The semantic-binding and syntax-binding sheets are identified as provisional proposals.

The previous Part 1 wording that treated an HMD as being generated inside the LHM and the previous Part 3 `LHM/HMD semantics` wording are not present in this revision.

## Structural and privacy checks

- All DOCX packages opened as valid ZIP packages.
- All XML and relationship parts parsed successfully.
- No comments, tracked revisions, macros, or embedded objects were found.
- No Windows absolute paths, email addresses, or credential-like assignments were found.
- Core properties identify `Nobuyuki SAMBUICHI` as creator and last modifier.
- Hidden runs were limited to Word table-of-contents field instructions and cached page numbers.
- Document links and tables were included in the text consistency inspection.

Visual re-rendering was attempted but not completed. LibreOffice reported that its `bootstrap.ini` was damaged. A read-only Microsoft Word PDF-conversion fallback also timed out. The source files were not modified by either attempt. Visual rendering therefore remains a follow-up verification item; the copy decision is based on the completed semantic, OOXML, metadata, privacy, and checksum checks.

## Copied files and SHA-256 verification

| File | Source SHA-256 | Destination SHA-256 | Result |
|---|---|---|---|
| `XBRL_GL_Next_Requirements_Specification_revised_collaborative-review_2026-07-27.docx` | `816DA0514EE791C6EDF6D197ACDC8D08DDCF6AF4FC6DE73BC22F1D74828248D0` | `816DA0514EE791C6EDF6D197ACDC8D08DDCF6AF4FC6DE73BC22F1D74828248D0` | match |
| `XBRL_GL_Next_Taxonomy_Framework_How_to_extend_the_taxonomy_revised_collaborative-review_2026-07-27.docx` | `6FAE2D6D05DCCFD82AAF9BA7B21A4DBA773FEDE5CFC75115D087EF5C01BC3952` | `6FAE2D6D05DCCFD82AAF9BA7B21A4DBA773FEDE5CFC75115D087EF5C01BC3952` | match |
| `XBRL_GL_Next_Taxonomy_Framework_Part_1_General_rules_revised_collaborative-review_2026-07-27.docx` | `9B16A90A103B0183CAEB9EEDCFF7D7C0B693D36568CDFC45AC643DF050A207C6` | `9B16A90A103B0183CAEB9EEDCFF7D7C0B693D36568CDFC45AC643DF050A207C6` | match |
| `XBRL_GL_Next_Taxonomy_Framework_Part_2_XBRL_2_1_palette_taxonomy_revised_collaborative-review_2026-07-27.docx` | `28EE0E920C9960DA87E770CF947093B35293B6EE98E0FF555CE69D09066276D0` | `28EE0E920C9960DA87E770CF947093B35293B6EE98E0FF555CE69D09066276D0` | match |
| `XBRL_GL_Next_Taxonomy_Framework_Part_3_xBRL_CSV_palette_taxonomy_revised_collaborative-review_2026-07-27.docx` | `F7A73FF9A6ACA81DC291A6BFDE2DB52FC0E12826BE17D7222BA6765EE216D1A7` | `F7A73FF9A6ACA81DC291A6BFDE2DB52FC0E12826BE17D7222BA6765EE216D1A7` | match |
| `XBRL_GL_Next_Taxonomy_Framework_Part_4_Aligned_pool_for_extension_revised_collaborative-review_2026-07-27.docx` | `0BFB3A87510652FDDBA4F21A25EF6E576A7B372D5F2AEEE491CF3D75D3CE5D3E` | `0BFB3A87510652FDDBA4F21A25EF6E576A7B372D5F2AEEE491CF3D75D3CE5D3E` | match |

## Destination and Git operations

All eight registration candidates are located under:

`TaxonomyFramework/docs/framework/working-drafts/`

They comprise six DOCX files, `README.md`, and this `COPY_REPORT.md`.

The six DOCX filenames match `.gitignore` line 33:

```gitignore
*20[0-9][0-9]-[01][0-9]-[0-3][0-9]*
```

Consequently, the DOCX files are present and checksum-verified but do not appear in the normal untracked-file list. No `.gitignore` exception and no force-add operation was applied because neither was included in the copy-only authorisation.

No source DOCX, source ZIP, existing repository file, branch, remote, or GitHub setting was changed. No file was staged, committed, amended, or pushed.
