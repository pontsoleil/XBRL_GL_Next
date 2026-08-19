# Part 1 / detailed program specification consistency resolution

## Scope

- Preserve the previously revised Part 1 without modification.
- Correct the single review-scope inconsistency in section 5.2, “Required checks”, of `tools/XBRL_GL_Next_Detailed_Program_Specification_2026-08-16.docx`.
- Selectively publish only the two formal DOCX files and the minimum task records identified in `COPY_PLAN.csv`.

## Detailed specification change

Previous wording:

> When --reviewed is supplied, row count/order and immutable fields remain controlled; changes are limited to the approved name/local_name and multiplicity restrictions.

Revised wording:

> When `--reviewed` is supplied, row count/order and immutable fields, including `name` and `semantic_path`, remain controlled; changes are limited to approved `local_name` adjustments and permitted `multiplicity` restrictions.

This makes the review boundary consistent with Part 1:

- reviewable: approved `local_name` adjustments and permitted `multiplicity` restrictions;
- not reviewable: `name`, `semantic_path`, hierarchy, row order, and other immutable fields.

## Deliberately unchanged

- Part 1 content and SHA-256.
- FSM, BSM, candidate/reviewed LHM, HMDs, manifest, semantic processing programs, taxonomy generator, generated taxonomy, and entry points.
- Table of Contents and all other detailed-specification wording.
