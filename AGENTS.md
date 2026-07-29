# XBRL GL Next repository instructions

## Current semantic-model contract

- FSM has exactly 15 columns in this order:
  `sequence`, `level`, `property_type`, `identifier`, `module`, `class_term`,
  `property_term`, `association_role`, `representation_term`,
  `associated_module`, `associated_class`, `multiplicity`, `definition`,
  `label_local`, `definition_local`.
- BSM has exactly the 15 FSM columns followed by `id`, for 16 columns total.
- BSM does not contain an `element` column.
- LHM and HMD use the same 17-column output header:
  `sequence`, `module`, `level`, `type`, `identifier`, `name`, `datatype`,
  `multiplicity`, `domain_name`, `definition`, `label_local`,
  `definition_local`, `element`, `id`, `semantic_path`, `associated_module`,
  `class_term`.
- Attribute identity is `property_term`.
- Association identity is
  `(association_role, associated_module, associated_class)`.
  `property_term` is not part of Association identity.

Graph Walk over the declared root Class set produces the combined LHM. Graph
Walk from one explicitly supplied root Class QName produces the root-specific
HMD directly from the BSM. HMD is not a fourth semantic model, and generating
an LHM first is not a prerequisite for generating an HMD.

For a Reference Association, emit the R occurrence and only target Attributes
whose `identifier` is `PK` as `REF`. If the target has no PK, emit no row below
the R occurrence, record a non-fatal error diagnostic, and continue with the
originating Class.

## Preservation and Git rules

- Treat `semantic-model/`, `scripts/`, historical reports, backups, archives,
  snapshots, and legacy fixtures as historical unless a task explicitly adopts
  them into the current contract.
- Do not rewrite historical results merely to match the current contract.
- Do not infer missing columns, reorder headers silently, or accept legacy
  headers as current input.
- Preserve unrelated user changes.
- Do not stage, commit, push, merge, rebase, change remotes, or change
  repository visibility without explicit user approval.
